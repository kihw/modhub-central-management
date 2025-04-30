from typing import Dict, Any, Optional, List
import logging
import time
from core.mods.mod_base import ModBase

class MediaMod(ModBase):
    def __init__(self):
        super().__init__(
            name="Media Mod",
            description="Optimise les paramètres audio et d'éclairage pour le multimédia",
            priority=75
        )
        self.settings = {
            "enable_audio_enhancement": True,
            "enable_lighting_effects": True,
            "content_profiles": {
                "movie": {
                    "audio": {
                        "equalizer": "movie",
                        "surround": True,
                        "volume_boost": 10
                    },
                    "display": {
                        "brightness": 70,
                        "contrast": 110,
                        "saturation": 110,
                        "ambient_lighting": "dynamic"
                    }
                },
                "music": {
                    "audio": {
                        "equalizer": "music",
                        "surround": False,
                        "volume_boost": 5
                    },
                    "display": {
                        "ambient_lighting": "rhythm"
                    }
                },
                "videoconf": {
                    "audio": {
                        "equalizer": "voice",
                        "noise_cancellation": True,
                        "volume_boost": 15
                    },
                    "display": {
                        "brightness": 85,
                        "ambient_lighting": "soft"
                    }
                }
            },
            "default_audio_device": "auto",
            "audio_transition_speed": "medium"
        }
        self.current_content_type = None
        self.applied_profile = None
        self.logger = logging.getLogger(__name__)

    def activate(self, context: Optional[Dict[str, Any]] = None) -> bool:
        try:
            if not context:
                return self._apply_default_profile()

            content_type = self._detect_media_content(context.get("processes", []))
            
            if content_type:
                self.current_content_type = content_type
                if self._apply_content_profile(content_type):
                    self.is_active = True
                    self.logger.info(f"Media Mod activé pour: {content_type}")
                    return True

            if context.get("is_media_activity"):
                return self._apply_default_profile()

            return self.deactivate() if self.is_active else False
        except Exception as e:
            self.logger.error(f"Erreur lors de l'activation: {e}")
            return False

    def deactivate(self) -> bool:
        if not self.is_active:
            return True

        try:
            self._restore_default_settings()
            self.is_active = False
            self.current_content_type = None
            self.applied_profile = None
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la désactivation: {e}")
            return False

    def _detect_media_content(self, processes: List[Dict[str, Any]]) -> Optional[str]:
        if not processes:
            return None

        media_apps = {
            "movie": ["vlc", "mpc-hc", "netflix", "primevideo", "disneyplus", "mpv", "iina", "plex"],
            "music": ["spotify", "music.ui", "itunes", "foobar2000", "winamp", "tidal", "deezer"],
            "videoconf": ["zoom", "teams", "skype", "discord", "webex", "slack", "meet"]
        }

        for process in processes:
            process_name = process.get("name", "").lower().strip().replace(".exe", "")
            for content_type, apps in media_apps.items():
                if any(app in process_name for app in apps):
                    return content_type
        return None

    def _apply_content_profile(self, content_type: str) -> bool:
        profile = self.settings.get("content_profiles", {}).get(content_type)
        if not profile:
            return self._apply_default_profile()

        try:
            if self.settings["enable_audio_enhancement"] and "audio" in profile:
                self._apply_audio_settings(profile["audio"])

            if self.settings["enable_lighting_effects"] and "display" in profile:
                self._apply_display_settings(profile["display"])

            self.applied_profile = content_type
            return True
        except Exception as e:
            self.logger.error(f"Erreur d'application du profil: {e}")
            return False

    def _apply_default_profile(self) -> bool:
        try:
            default_settings = {"audio": {}, "display": {}}
            if self.settings["enable_audio_enhancement"]:
                self._apply_audio_settings(default_settings["audio"])
            if self.settings["enable_lighting_effects"]:
                self._apply_display_settings(default_settings["display"])
            
            self.is_active = True
            self.applied_profile = "default"
            return True
        except Exception as e:
            self.logger.error(f"Erreur profil par défaut: {e}")
            return False

    def _apply_audio_settings(self, settings: Dict[str, Any]) -> None:
        if not isinstance(settings, dict):
            raise ValueError("Invalid audio settings format")

    def _apply_display_settings(self, settings: Dict[str, Any]) -> None:
        if not isinstance(settings, dict):
            raise ValueError("Invalid display settings format")

    def _restore_default_settings(self) -> None:
        self._apply_audio_settings({})
        self._apply_display_settings({})

    def update_content_profile(self, content_type: str, profile: Dict[str, Any]) -> bool:
        if not isinstance(profile, dict) or not content_type:
            return False

        try:
            self.settings["content_profiles"][content_type] = profile.copy()
            
            if self.is_active and self.current_content_type == content_type:
                return self._apply_content_profile(content_type)
            return True
        except Exception as e:
            self.logger.error(f"Erreur mise à jour profil: {e}")
            return False