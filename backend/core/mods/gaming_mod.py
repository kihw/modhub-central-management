from typing import Dict, Any, List, Optional
import logging
from core.mods.mod_base import ModBase

class GamingMod(ModBase):
    def __init__(self):
        super().__init__(
            name="Gaming Mod",
            description="Optimise vos périphériques pour le gaming",
            priority=100
        )
        self.settings = {
            "default_dpi": 800,
            "default_polling_rate": 1000,
            "enable_rgb": True,
            "game_profiles": {},
            "peripherals": {
                "keyboard": {"enabled": True},
                "mouse": {"enabled": True},
                "headset": {"enabled": True},
                "monitor": {"enabled": True}
            }
        }
        self.current_game = None
        self.applied_profile = None
        self.game_processes = {
            "csgo.exe": "Counter-Strike: Global Offensive",
            "valorant.exe": "Valorant", 
            "overwatch.exe": "Overwatch",
            "rocketleague.exe": "Rocket League",
            "gta5.exe": "Grand Theft Auto V",
            "fortniteclient-win64-shipping.exe": "Fortnite",
            "r5apex.exe": "Apex Legends",
            "cyberpunk2077.exe": "Cyberpunk 2077"
        }
        self.logger = logging.getLogger(__name__)

    def activate(self, context: Optional[Dict[str, Any]] = None) -> bool:
        try:
            if not context:
                return self._apply_default_profile()

            detected_game = self._detect_game(context.get("processes", []))
            if detected_game:
                if detected_game == self.current_game and self.is_active:
                    return True
                    
                self.current_game = detected_game
                return self._apply_game_profile(detected_game)

            if context.get("is_gaming_activity", False):
                return self._apply_default_profile()

            return False
        except Exception as e:
            self.logger.error(f"Activation error: {e}")
            return False

    def deactivate(self) -> bool:
        if not self.is_active:
            return True

        try:
            self._reset_peripherals()
            self.is_active = False
            self.current_game = None
            self.applied_profile = None
            self.logger.info("Gaming Mod désactivé avec succès")
            return True
        except Exception as e:
            self.logger.error(f"Désactivation error: {e}")
            return False

    def _detect_game(self, processes: List[Dict[str, Any]]) -> Optional[str]:
        if not processes:
            return None
            
        for process in processes:
            process_name = process.get("name", "").lower()
            for game_process, game_name in self.game_processes.items():
                if game_process.lower() in process_name:
                    return game_name
        return None

    def _apply_game_profile(self, game_name: str) -> bool:
        if not game_name:
            return self._apply_default_profile()
            
        profile = self.settings.get("game_profiles", {}).get(game_name)
        if not profile:
            return self._apply_default_profile()

        try:
            for peripheral, config in self.settings["peripherals"].items():
                if config.get("enabled"):
                    settings = profile.get(peripheral, {})
                    self._apply_peripheral_settings(peripheral, settings)

            self.is_active = True
            self.applied_profile = game_name
            return True
        except Exception as e:
            self.logger.error(f"Game profile error {game_name}: {e}")
            return self._apply_default_profile()

    def _apply_default_profile(self) -> bool:
        try:
            self._apply_mouse_settings(
                self.settings["default_dpi"],
                self.settings["default_polling_rate"]
            )
            self.is_active = True
            self.applied_profile = "default"
            return True
        except Exception as e:
            self.logger.error(f"Default profile error: {e}")
            return False

    def update_game_profile(self, game_name: str, profile: Dict[str, Any]) -> bool:
        if not isinstance(profile, dict) or not game_name:
            self.logger.error("Invalid profile data")
            return False
            
        try:
            self.settings["game_profiles"][game_name] = profile.copy()
            
            if self.is_active and self.current_game == game_name:
                return self._apply_game_profile(game_name)
            return True
        except Exception as e:
            self.logger.error(f"Profile update error {game_name}: {e}")
            return False

    def _apply_peripheral_settings(self, peripheral: str, settings: Dict[str, Any]) -> None:
        if not settings:
            return
            
        if peripheral == "mouse":
            self._apply_mouse_settings(
                settings.get("dpi", self.settings["default_dpi"]),
                settings.get("polling_rate", self.settings["default_polling_rate"])
            )
        elif peripheral == "keyboard":
            self._apply_keyboard_settings(settings)

    def _apply_mouse_settings(self, dpi: int, polling_rate: int) -> None:
        pass

    def _apply_keyboard_settings(self, settings: Dict[str, Any]) -> None:
        pass

    def _reset_peripherals(self) -> None:
        if self.settings["peripherals"]["mouse"]["enabled"]:
            self._apply_mouse_settings(
                self.settings["default_dpi"],
                self.settings["default_polling_rate"]
            )
        if self.settings["peripherals"]["keyboard"]["enabled"]:
            self._apply_keyboard_settings({})