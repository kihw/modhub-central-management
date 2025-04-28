import psutil
import logging
from typing import Dict, List, Optional, Callable

logger = logging.getLogger(__name__)

class ProcessMonitor:
    """
    Monitor system processes to trigger automation rules based on running applications.
    """
    def __init__(self):
        self.watched_processes: Dict[str, Callable] = {}
        self.current_processes: Dict[str, psutil.Process] = {}
        self.logger = logging.getLogger(__name__)
    
    def add_watch(self, process_name: str, callback: Callable) -> None:
        """
        Add a process to the watch list with a callback when detected.
        
        Args:
            process_name: Name of the process to watch for
            callback: Function to call when process is detected
        """
        self.watched_processes[process_name.lower()] = callback
        self.logger.info(f"Added watch for process: {process_name}")
    
    def remove_watch(self, process_name: str) -> None:
        """
        Remove a process from the watch list.
        
        Args:
            process_name: Name of the process to stop watching
        """
        if process_name.lower() in self.watched_processes:
            del self.watched_processes[process_name.lower()]
            self.logger.info(f"Removed watch for process: {process_name}")
    
    def scan(self) -> None:
        """
        Scan running processes and trigger callbacks for watched processes.
        """
        new_processes = {}
        
        # Get all running processes
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                new_processes[proc_name] = proc
                
                # If this is a new process we're watching, trigger callback
                if proc_name in self.watched_processes and proc_name not in self.current_processes:
                    self.logger.info(f"Detected watched process: {proc_name}")
                    try:
                        self.watched_processes[proc_name](proc)
                    except Exception as e:
                        self.logger.error(f"Error in process callback for {proc_name}: {e}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Check for processes that have ended
        for proc_name in self.current_processes:
            if proc_name not in new_processes and proc_name in self.watched_processes:
                self.logger.info(f"Watched process ended: {proc_name}")
                # Could add another callback here for process end events

        # Update current processes
        self.current_processes = new_processes
    
    def get_running_processes(self) -> List[str]:
        """
        Get a list of all running process names.
        
        Returns:
            List of process names
        """
        return list(self.current_processes.keys())
    
    def is_process_running(self, process_name: str) -> bool:
        """
        Check if a specific process is currently running.
        
        Args:
            process_name: Name of the process to check
            
        Returns:
            True if the process is running, False otherwise
        """
        return process_name.lower() in self.current_processes