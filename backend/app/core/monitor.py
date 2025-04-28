import asyncio
import psutil
import time
from datetime import datetime
from typing import Dict, List, Set
import logging
from app.core.db import get_db
from app.models.process import Process
from app.models.mod import Mod
from app.core.rule_engine import RuleEngine

logger = logging.getLogger(__name__)

class ProcessMonitor:
    def __init__(self):
        self.running_processes: Dict[int, str] = {}
        self.active_mods: Set[str] = set()
        self.rule_engine = RuleEngine()
        self.refresh_interval = 5  # seconds
        self._monitor_task = None
        
    async def initialize(self):
        """Initialize the process monitor and start monitoring"""
        await self.rule_engine.load_rules()
        self._monitor_task = asyncio.create_task(self._monitor_processes())
        logger.info("Process monitor initialized and started")
        
    async def _monitor_processes(self):
        """Continuously monitor processes and apply rules"""
        while True:
            try:
                # Get current processes
                current_processes = {p.pid: p.name() for p in psutil.process_iter(['pid', 'name'])}
                
                # Check for new processes
                new_processes = set(current_processes.keys()) - set(self.running_processes.keys())
                for pid in new_processes:
                    process_name = current_processes[pid]
                    logger.info(f"New process detected: {process_name} (PID: {pid})")
                    await self._process_detected(process_name, pid)
                
                # Check for ended processes
                ended_processes = set(self.running_processes.keys()) - set(current_processes.keys())
                for pid in ended_processes:
                    process_name = self.running_processes[pid]
                    logger.info(f"Process ended: {process_name} (PID: {pid})")
                    await self._process_ended(process_name, pid)
                
                # Update running processes
                self.running_processes = current_processes
                
                # Check time-based conditions
                await self._check_time_conditions()
                
                # Apply rules based on current state
                await self._apply_rules()
                
                await asyncio.sleep(self.refresh_interval)
            except Exception as e:
                logger.error(f"Error in process monitor: {e}")
                await asyncio.sleep(10)  # Wait longer if error
    
    async def _process_detected(self, process_name: str, pid: int):
        """Handle newly detected process"""
        # Record process in DB
        async with get_db() as db:
            db_process = Process(
                name=process_name,
                pid=pid,
                started_at=datetime.now()
            )
            db.add(db_process)
            await db.commit()
    
    async def _process_ended(self, process_name: str, pid: int):
        """Handle ended process"""
        # Update process in DB
        async with get_db() as db:
            db_process = await db.query(Process).filter(Process.pid == pid).first()
            if db_process:
                db_process.ended_at = datetime.now()
                await db.commit()
    
    async def _check_time_conditions(self):
        """Check time-based conditions (night mode, etc.)"""
        current_hour = datetime.now().hour
        # Example: Enable night mode after 10 PM
        if current_hour >= 22 or current_hour < 6:
            # Check if NightMod should be activated
            night_mode_active = "NightMod" in self.active_mods
            if not night_mode_active:
                await self._activate_mod("NightMod")
        elif "NightMod" in self.active_mods:
            # Deactivate NightMod during day hours
            await self._deactivate_mod("NightMod")
    
    async def _apply_rules(self):
        """Apply rules based on current state"""
        # Get active processes names
        active_process_names = list(self.running_processes.values())
        
        # Apply rules using rule engine
        actions = await self.rule_engine.evaluate_rules(active_process_names)
        
        # Execute actions (activate/deactivate mods)
        for action in actions:
            if action.action_type == "activate_mod":
                await self._activate_mod(action.target)
            elif action.action_type == "deactivate_mod":
                await self._deactivate_mod(action.target)
    
    async def _activate_mod(self, mod_name: str):
        """Activate a specific mod"""
        if mod_name in self.active_mods:
            return
        
        logger.info(f"Activating mod: {mod_name}")
        self.active_mods.add(mod_name)
        
        # Get mod configuration
        async with get_db() as db:
            mod = await db.query(Mod).filter(Mod.name == mod_name).first()
            if not mod:
                logger.warning(f"Mod {mod_name} not found in database")
                return
            
            # Execute mod's activation logic based on its type
            if mod_name == "GamingMod":
                await self._apply_gaming_mod(mod.config)
            elif mod_name == "NightMod":
                await self._apply_night_mod(mod.config)
            elif mod_name == "MediaMod":
                await self._apply_media_mod(mod.config)
            else:
                await self._apply_custom_mod(mod_name, mod.config)
    
    async def _deactivate_mod(self, mod_name: str):
        """Deactivate a specific mod"""
        if mod_name not in self.active_mods:
            return
        
        logger.info(f"Deactivating mod: {mod_name}")
        self.active_mods.remove(mod_name)
        
        # Restore default settings
        # Implementation depends on mod type
        # ...
    
    async def _apply_gaming_mod(self, config: dict):
        """Apply gaming mod settings"""
        # Implement gaming-specific settings
        # Example: Adjust DPI, RGB settings, etc.
        pass
    
    async def _apply_night_mod(self, config: dict):
        """Apply night mod settings"""
        # Implement night mode settings
        # Example: Reduce brightness, activate blue light filter
        pass
    
    async def _apply_media_mod(self, config: dict):
        """Apply media mod settings"""
        # Implement media-specific settings
        # Example: Optimize audio, adjust lighting
        pass
    
    async def _apply_custom_mod(self, mod_name: str, config: dict):
        """Apply custom mod settings"""
        # Apply settings for custom user-defined mods
        pass
    
    async def stop_monitoring(self):
        """Stop the monitoring process"""
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Process monitor stopped")