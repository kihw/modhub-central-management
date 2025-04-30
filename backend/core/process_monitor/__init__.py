import psutil
import logging
from typing import Dict, List, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
import time

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ProcessInfo:
    process: psutil.Process
    start_time: datetime
    last_seen: datetime = field(default_factory=datetime.now)

class ProcessMonitor:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        # Éviter la réinitialisation si déjà initialisé (singleton)
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.watched_processes: Dict[str, Callable[[psutil.Process], None]] = {}
        self.current_processes: Dict[str, ProcessInfo] = {}
        self.logger = logging.getLogger(__name__)
        self.is_monitoring: bool = False
        self._scan_interval: float = 1.0
        self._last_scan: datetime = datetime.min
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.RLock()
        self._callbacks: Dict[str, Set[Callable]] = {}
        self._initialized = True
        
        logger.info("ProcessMonitor initialized")

    def add_watch(self, process_name: str, callback: Callable[[psutil.Process], None]) -> bool:
        """Ajouter une surveillance pour un processus spécifique"""
        with self._lock:
            if not isinstance(process_name, str) or not callable(callback):
                return False
                
            process_name = process_name.strip().lower()
            if not process_name:
                return False
                
            if process_name not in self._callbacks:
                self._callbacks[process_name] = set()
            self._callbacks[process_name].add(callback)
            self.watched_processes[process_name] = callback  # Pour compatibilité
            
            self.logger.info(f"Added watch for process: {process_name}")
            return True

    def remove_watch(self, process_name: str, callback: Optional[Callable] = None) -> bool:
        """Supprimer une surveillance pour un processus"""
        with self._lock:
            if not isinstance(process_name, str):
                return False
                
            process_name = process_name.strip().lower()
            
            if callback is not None:
                # Supprimer uniquement ce callback spécifique
                if process_name in self._callbacks and callback in self._callbacks[process_name]:
                    self._callbacks[process_name].remove(callback)
                    if not self._callbacks[process_name]:
                        del self._callbacks[process_name]
                        self.watched_processes.pop(process_name, None)  # Pour compatibilité
                    self.logger.info(f"Removed specific callback for process: {process_name}")
                    return True
                return False
            else:
                # Supprimer tous les callbacks pour ce processus
                removed = self._callbacks.pop(process_name, None)
                self.watched_processes.pop(process_name, None)  # Pour compatibilité
                if removed:
                    self.logger.info(f"Removed all watches for process: {process_name}")
                    return True
                return False

    def scan(self) -> None:
        """Scanner les processus en cours d'exécution"""
        if not self.is_monitoring:
            return
            
        current_time = datetime.now()
        if current_time - self._last_scan < timedelta(seconds=self._scan_interval):
            return

        with self._lock:
            self._last_scan = current_time
            new_processes: Dict[str, ProcessInfo] = {}

            try:
                # Obtenir la liste des processus
                process_list = list(psutil.process_iter(['pid', 'name', 'create_time']))
                
                # Créer un dictionnaire des noms de processus pour recherche efficace
                process_name_map = {}
                for proc in process_list:
                    try:
                        proc_name = proc.info['name'].lower()
                        if proc_name in self.watched_processes or proc_name in self.current_processes:
                            process_name_map[proc_name] = proc
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, KeyError):
                        continue
                
                # Traiter les processus surveillés et actuels
                for proc_name in set(list(self.watched_processes.keys()) + list(self.current_processes.keys())):
                    proc = process_name_map.get(proc_name)
                    
                    if proc:
                        # Le processus existe
                        if proc_name in self.current_processes:
                            # Mise à jour des informations du processus
                            new_processes[proc_name] = ProcessInfo(
                                process=proc,
                                start_time=self.current_processes[proc_name].start_time,
                                last_seen=current_time
                            )
                        else:
                            # Nouveau processus détecté
                            try:
                                create_time = datetime.fromtimestamp(proc.info['create_time'])
                            except (KeyError, TypeError, ValueError, OSError):
                                create_time = current_time
                                
                            new_processes[proc_name] = ProcessInfo(
                                process=proc,
                                start_time=create_time,
                                last_seen=current_time
                            )
                            
                            # Déclencher les callbacks pour les nouveaux processus surveillés
                            if proc_name in self.watched_processes:
                                self._trigger_callbacks(proc_name, proc)
                
                # Traiter les processus qui ont terminé
                self._handle_ended_processes(new_processes)
                
                # Mettre à jour la liste des processus
                self.current_processes = new_processes
                
            except Exception as e:
                self.logger.error(f"Error during process scan: {str(e)}", exc_info=True)

    def _trigger_callbacks(self, proc_name: str, proc: psutil.Process) -> None:
        """Déclencher tous les callbacks enregistrés pour un processus"""
        if proc_name not in self._callbacks:
            return
            
        for callback in self._callbacks[proc_name]:
            try:
                callback(proc)
                self.logger.debug(f"Triggered callback for process: {proc_name}")
            except Exception as e:
                self.logger.error(f"Error in process callback for {proc_name}: {str(e)}")
        
        # Pour compatibilité - appeler le callback de watched_processes
        self._trigger_callback(proc_name, proc)
                
    def _trigger_callback(self, proc_name: str, proc: psutil.Process) -> None:
        """Déclencher le callback unique enregistré pour un processus (compatibilité)"""
        try:
            if callback := self.watched_processes.get(proc_name):
                callback(proc)
                self.logger.debug(f"Triggered legacy callback for process: {proc_name}")
        except Exception as e:
            self.logger.error(f"Error in legacy process callback for {proc_name}: {str(e)}")

    def _handle_ended_processes(self, new_processes: Dict[str, ProcessInfo]) -> None:
        """Gérer les processus qui ont terminé"""
        ended_processes = set(self.current_processes) - set(new_processes)
        for proc_name in ended_processes:
            if proc_name in self.watched_processes:
                self.logger.info(f"Watched process ended: {proc_name}")

    def _monitoring_loop(self) -> None:
        """Boucle principale de surveillance des processus"""
        self.logger.info("Process monitoring loop started")
        
        while not self._stop_event.is_set():
            try:
                self.scan()
                time.sleep(0.1)  # Pause courte pour éviter une utilisation CPU élevée
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                time.sleep(1.0)  # Pause plus longue en cas d'erreur

    def get_running_processes(self) -> List[str]:
        """Obtenir la liste des processus en cours d'exécution"""
        with self._lock:
            return sorted(self.current_processes.keys())

    def is_process_running(self, process_name: str) -> bool:
        """Vérifier si un processus est en cours d'exécution"""
        if not isinstance(process_name, str):
            return False
        with self._lock:
            return process_name.strip().lower() in self.current_processes

    def start_monitoring(self) -> bool:
        """Démarrer la surveillance des processus"""
        with self._lock:
            if self.is_monitoring:
                self.logger.info("Process monitoring is already running")
                return True
                
            try:
                self._stop_event.clear()
                self._monitoring_thread = threading.Thread(
                    target=self._monitoring_loop,
                    daemon=True,
                    name="SimpleProcessMonitor"
                )
                self._monitoring_thread.start()
                self.is_monitoring = True
                self._last_scan = datetime.min
                self.logger.info("Process monitoring started")
                return True
            except Exception as e:
                self.logger.error(f"Failed to start process monitoring: {e}")
                return False

    def stop_monitoring(self) -> bool:
        """Arrêter la surveillance des processus"""
        with self._lock:
            if not self.is_monitoring:
                self.logger.info("Process monitoring is not running")
                return True
                
            try:
                self._stop_event.set()
                if self._monitoring_thread and self._monitoring_thread.is_alive():
                    self._monitoring_thread.join(timeout=5)
                    if self._monitoring_thread.is_alive():
                        self.logger.warning("Process monitoring thread did not terminate properly")
                        
                self.is_monitoring = False
                self.current_processes.clear()
                self.logger.info("Process monitoring stopped")
                return True
            except Exception as e:
                self.logger.error(f"Error stopping process monitoring: {e}")
                return False

    def get_process_info(self, process_name: str) -> Optional[ProcessInfo]:
        """Obtenir les informations d'un processus spécifique"""
        if not isinstance(process_name, str):
            return None
        with self._lock:
            return self.current_processes.get(process_name.strip().lower())

    def set_scan_interval(self, interval: float) -> None:
        """Définir l'intervalle de scan en secondes"""
        if isinstance(interval, (int, float)) and interval > 0:
            with self._lock:
                self._scan_interval = float(interval)
                self.logger.info(f"Scan interval set to {interval} seconds")

    def get_scan_interval(self) -> float:
        """Obtenir l'intervalle de scan en secondes"""
        return self._scan_interval

# Créer l'instance singleton
process_monitor = ProcessMonitor()

# Démarrer automatiquement le monitoring lors de l'importation
try:
    process_monitor.start_monitoring()
except Exception as e:
    logger.error(f"Error auto-starting simple process monitor: {e}")

# Pour faciliter l'importation
__all__ = ['ProcessMonitor', 'ProcessInfo', 'process_monitor']