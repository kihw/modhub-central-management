# Dans backend/core/process_management/advanced_monitor.py

import psutil
import logging
from typing import Dict, List, Optional, Callable, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from queue import Queue
import threading
import time
import re
from weakref import WeakValueDictionary

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ProcessInfo:
    pid: int
    name: str
    exe_path: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    io_read_bytes: int = 0
    io_write_bytes: int = 0
    threads_count: int = 0
    status: str = 'running'
    parent_pid: Optional[int] = None
    cmdline: tuple[str, ...] = field(default_factory=tuple)
    tags: frozenset[str] = field(default_factory=frozenset)
    is_monitored: bool = False
    last_updated: datetime = field(default_factory=datetime.now)

class AdvancedProcessMonitor:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(
        self, 
        scan_interval: float = 5.0, 
        max_tracked_processes: int = 500,
        resource_threshold_cpu: float = 70.0,
        resource_threshold_memory: float = 80.0
    ):
        # Éviter la réinitialisation si déjà initialisé (singleton)
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        # Définir les catégories de processus
        self.PROCESS_CATEGORIES = (
            {'pattern': r'steam\.exe|origin\.exe|epicgames\.exe|game|unity\.exe', 'tag': 'gaming'},
            {'pattern': r'vlc\.exe|spotify\.exe|netflix\.exe|media|player|audio', 'tag': 'media'},
            {'pattern': r'code\.exe|idea64\.exe|pycharm64\.exe|dev|studio|compiler', 'tag': 'development'}
        )
        
        # Initialiser les attributs
        self._tracked_processes = WeakValueDictionary()
        self._monitored_callbacks: Dict[str, Set[Callable]] = {}
        self._scan_interval = max(0.1, min(scan_interval, 60.0))
        self._max_tracked_processes = max(10, min(max_tracked_processes, 1000))
        self._resource_thresholds = {
            'cpu': min(100.0, max(0.0, resource_threshold_cpu)),
            'memory': min(100.0, max(0.0, resource_threshold_memory))
        }
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._event_queue: Queue = Queue(maxsize=1000)
        self._process_patterns = {cat['tag']: re.compile(cat['pattern'], re.IGNORECASE) for cat in self.PROCESS_CATEGORIES}
        self._initialized = True
        self._is_monitoring_active = False
        self._lock = threading.RLock()
        
        logger.info("AdvancedProcessMonitor initialized")

    def start_monitoring(self) -> bool:
        with self._lock:
            if self._is_monitoring_active:
                logger.info("Process monitoring is already running")
                return True
                
            if self._monitoring_thread and self._monitoring_thread.is_alive():
                logger.info("Process monitoring thread is already running")
                return True
            
            try:
                self._stop_event.clear()
                self._monitoring_thread = threading.Thread(
                    target=self._monitoring_loop,
                    daemon=True,
                    name="ProcessMonitor"
                )
                self._monitoring_thread.start()
                self._is_monitoring_active = True
                logger.info("Process monitoring started")
                return True
            except Exception as e:
                logger.error(f"Failed to start process monitoring: {e}")
                self._is_monitoring_active = False
                return False

    def stop_monitoring(self) -> bool:
        with self._lock:
            if not self._is_monitoring_active:
                logger.info("Process monitoring is not running")
                return True
                
            try:
                self._stop_event.set()
                if self._monitoring_thread and self._monitoring_thread.is_alive():
                    self._monitoring_thread.join(timeout=5)
                    if self._monitoring_thread.is_alive():
                        logger.warning("Process monitoring thread did not terminate properly")
                
                self._is_monitoring_active = False
                self._tracked_processes.clear()
                logger.info("Process monitoring stopped")
                return True
            except Exception as e:
                logger.error(f"Error stopping process monitoring: {e}")
                return False

    def is_monitoring(self) -> bool:
        """Vérifier si le monitoring est actif"""
        return self._is_monitoring_active and self._monitoring_thread and self._monitoring_thread.is_alive()

    def _monitoring_loop(self) -> None:
        """Boucle principale de surveillance des processus"""
        logger.info("Process monitoring loop started")
        last_full_scan_time = 0
        
        while not self._stop_event.is_set():
            try:
                current_time = time.time()
                
                # Scan complet toutes les scan_interval secondes
                if current_time - last_full_scan_time >= self._scan_interval:
                    self._scan_processes()
                    last_full_scan_time = current_time
                
                # Traiter les événements en attente
                self._process_events()
                
                # Vérifier les processus à haute utilisation
                self._check_resource_thresholds()
                
                # Pause courte pour éviter une utilisation CPU élevée
                time.sleep(0.2)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}", exc_info=True)
                time.sleep(max(1.0, self._scan_interval / 2))

    def _scan_processes(self) -> None:
        """Scanner tous les processus actifs"""
        try:
            current_processes = WeakValueDictionary()
            
            process_iter = list(psutil.process_iter(['pid', 'name', 'exe', 'status', 'cmdline']))
            logger.debug(f"Found {len(process_iter)} running processes")
            
            for proc in process_iter:
                if len(current_processes) >= self._max_tracked_processes:
                    break
                    
                try:
                    process_info = self._create_process_info(proc)
                    if process_info:
                        current_processes[process_info.pid] = process_info
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    continue
                except Exception as e:
                    logger.warning(f"Error processing process {proc.pid}: {e}")
            
            # Mettre à jour la liste des processus suivis
            self._tracked_processes = current_processes
            logger.debug(f"Tracking {len(self._tracked_processes)} processes")
            
        except Exception as e:
            logger.error(f"Process scan error: {e}", exc_info=True)

    def _create_process_info(self, proc: psutil.Process) -> Optional[ProcessInfo]:
        """Créer un objet ProcessInfo à partir d'un processus psutil"""
        try:
            proc_info = proc.info
            
            # Informations de base
            pid = proc_info['pid']
            name = proc_info.get('name', '')
            if not name:
                return None
                
            exe_path = proc_info.get('exe')
            status = proc_info.get('status', 'unknown')
            
            # Convertir cmdline en tuple
            cmdline = tuple(proc_info.get('cmdline', []))
            
            # Calculer les tags basés sur le nom du processus
            tags = frozenset(self._categorize_process(name))
            
            # Créer l'objet ProcessInfo de base
            process_info = ProcessInfo(
                pid=pid,
                name=name,
                exe_path=exe_path,
                status=status,
                cmdline=cmdline,
                tags=tags,
                last_updated=datetime.now()
            )

            # Ajouter les métriques de ressources et autres informations détaillées
            try:
                with proc.oneshot():
                    return ProcessInfo(
                        **{**process_info.__dict__,
                          'cpu_usage': proc.cpu_percent() or 0.0,
                          'memory_usage': proc.memory_percent() or 0.0,
                          'threads_count': proc.num_threads(),
                          'start_time': datetime.fromtimestamp(proc.create_time()),
                          'io_read_bytes': getattr(proc.io_counters(), 'read_bytes', 0) if hasattr(proc, 'io_counters') else 0,
                          'io_write_bytes': getattr(proc.io_counters(), 'write_bytes', 0) if hasattr(proc, 'io_counters') else 0,
                          'parent_pid': proc.parent().pid if proc.parent() else None}
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Retourner l'objet de base si les métriques détaillées échouent
                return process_info
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
        except Exception as e:
            logger.warning(f"Error creating process info for PID {proc.pid}: {e}")
            return None

    def _categorize_process(self, process_name: str) -> Set[str]:
        """Catégoriser un processus en fonction de son nom"""
        if not process_name:
            return set()
            
        return {tag for tag, pattern in self._process_patterns.items() if pattern.search(process_name)}

    def _check_resource_thresholds(self) -> None:
        """Vérifier si les processus dépassent les seuils de ressources"""
        try:
            high_resource_processes = [
                process for process in self._tracked_processes.values()
                if (process.cpu_usage > self._resource_thresholds['cpu'] or
                    process.memory_usage > self._resource_thresholds['memory'])
            ]
            
            if high_resource_processes and not self._event_queue.full():
                self._event_queue.put(('high_resource', tuple(high_resource_processes)))
                logger.debug(f"Found {len(high_resource_processes)} high resource processes")
        except Exception as e:
            logger.error(f"Error checking resource thresholds: {e}")

    def _process_events(self) -> None:
        """Traiter les événements en attente dans la queue"""
        try:
            while not self._event_queue.empty():
                event_type, data = self._event_queue.get_nowait()
                if event_type == 'high_resource':
                    self._handle_high_resource_processes(data)
                self._event_queue.task_done()
        except Exception as e:
            logger.error(f"Error processing events: {e}")

    def _handle_high_resource_processes(self, processes: tuple[ProcessInfo, ...]) -> None:
        """Traiter les processus à haute utilisation de ressources"""
        try:
            for process in processes:
                for callback_key, callbacks in self._monitored_callbacks.items():
                    pattern, tag = callback_key.split(':')
                    if (not pattern or re.search(pattern, process.name, re.IGNORECASE)) and \
                    (not tag or tag in process.tags):
                        for callback in callbacks:
                            try:
                                callback(process)
                            except Exception as e:
                                logger.error(f"Callback error for {process.name}: {e}")
        except Exception as e:
            logger.error(f"Error handling high resource processes: {e}")

    def get_processes_by_tag(self, tag: str) -> tuple[ProcessInfo, ...]:
        """Obtenir tous les processus avec un tag spécifique"""
        if not tag:
            return tuple()
            
        return tuple(proc for proc in self._tracked_processes.values() if tag in proc.tags)

    def get_all_processes(self) -> tuple[ProcessInfo, ...]:
        """Obtenir tous les processus suivis"""
        return tuple(self._tracked_processes.values())

    def get_process_by_name(self, name: str) -> tuple[ProcessInfo, ...]:
        """Obtenir les processus par nom (correspondance partielle)"""
        if not name:
            return tuple()
            
        name_lower = name.lower()
        return tuple(proc for proc in self._tracked_processes.values() 
                    if name_lower in proc.name.lower())

    def get_process_by_pid(self, pid: int) -> Optional[ProcessInfo]:
        """Obtenir un processus par PID"""
        return self._tracked_processes.get(pid)

    def register_process_callback(
        self, 
        callback: Callable[[ProcessInfo], None],
        process_name_pattern: str = '',
        tag: str = ''
    ) -> bool:
        """Enregistrer un callback pour certains processus"""
        if not callable(callback):
            return False
            
        key = f"{process_name_pattern}:{tag}"
        if key not in self._monitored_callbacks:
            self._monitored_callbacks[key] = set()
        self._monitored_callbacks[key].add(callback)
        logger.info(f"Registered process callback for '{key}'")
        return True

    def unregister_process_callback(
        self,
        callback: Callable[[ProcessInfo], None],
        process_name_pattern: str = '',
        tag: str = ''
    ) -> bool:
        """Supprimer un callback enregistré"""
        key = f"{process_name_pattern}:{tag}"
        if key in self._monitored_callbacks and callback in self._monitored_callbacks[key]:
            self._monitored_callbacks[key].remove(callback)
            logger.info(f"Unregistered process callback for '{key}'")
            
            # Supprimer la clé si elle n'a plus de callbacks
            if not self._monitored_callbacks[key]:
                del self._monitored_callbacks[key]
                
            return True
        return False
        
    def get_high_resource_processes(self, cpu_threshold: Optional[float] = None, memory_threshold: Optional[float] = None) -> tuple[ProcessInfo, ...]:
        """Obtenir les processus à haute utilisation de ressources"""
        cpu_limit = cpu_threshold if cpu_threshold is not None else self._resource_thresholds['cpu']
        mem_limit = memory_threshold if memory_threshold is not None else self._resource_thresholds['memory']
        
        return tuple(
            proc for proc in self._tracked_processes.values()
            if proc.cpu_usage > cpu_limit or proc.memory_usage > mem_limit
        )
    
    def get_process_stats(self) -> Dict[str, Any]:
        """Obtenir des statistiques sur les processus suivis"""
        processes = list(self._tracked_processes.values())
        
        if not processes:
            return {
                "count": 0,
                "total_cpu": 0.0,
                "total_memory": 0.0,
                "top_cpu": [],
                "top_memory": [],
                "by_tag": {}
            }
        
        # Calculer les statistiques
        total_cpu = sum(p.cpu_usage for p in processes)
        total_memory = sum(p.memory_usage for p in processes)
        
        # Processus avec le plus d'utilisation CPU
        top_cpu = sorted(processes, key=lambda p: p.cpu_usage, reverse=True)[:5]
        top_cpu_info = [{
            "pid": p.pid,
            "name": p.name,
            "cpu_usage": p.cpu_usage,
            "tags": list(p.tags)
        } for p in top_cpu]
        
        # Processus avec le plus d'utilisation mémoire
        top_memory = sorted(processes, key=lambda p: p.memory_usage, reverse=True)[:5]
        top_memory_info = [{
            "pid": p.pid,
            "name": p.name,
            "memory_usage": p.memory_usage,
            "tags": list(p.tags)
        } for p in top_memory]
        
        # Stats par tag
        tags_stats = {}
        all_tags = set()
        for p in processes:
            for tag in p.tags:
                all_tags.add(tag)
        
        for tag in all_tags:
            tagged_processes = [p for p in processes if tag in p.tags]
            if tagged_processes:
                tags_stats[tag] = {
                    "count": len(tagged_processes),
                    "total_cpu": sum(p.cpu_usage for p in tagged_processes),
                    "total_memory": sum(p.memory_usage for p in tagged_processes)
                }
        
        return {
            "count": len(processes),
            "total_cpu": total_cpu,
            "total_memory": total_memory,
            "top_cpu": top_cpu_info,
            "top_memory": top_memory_info,
            "by_tag": tags_stats,
            "timestamp": datetime.now().isoformat()
        }

# Créer l'instance singleton
advanced_process_monitor = AdvancedProcessMonitor()

# Démarrer automatiquement le monitoring des processus lors de l'importation
try:
    advanced_process_monitor.start_monitoring()
except Exception as e:
    logger.error(f"Error auto-starting process monitor: {e}")

# Pour faciliter l'importation
__all__ = ['AdvancedProcessMonitor', 'ProcessInfo', 'advanced_process_monitor']