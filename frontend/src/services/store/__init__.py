"""
Store initialization module for ModHub Central.

This module initializes the central store that manages state across
the application. It integrates with the backend API to fetch and update
mod configurations, system status, and user preferences.
"""

from .store import create_store, get_store
from .actions import (
    set_active_mods,
    toggle_mod,
    update_mod_settings,
    set_system_status,
    set_user_preferences,
    add_event_to_history,
    clear_history,
    register_automation_rule,
    remove_automation_rule,
    update_automation_rule
)

__all__ = [
    'create_store',
    'get_store',
    'set_active_mods',
    'toggle_mod',
    'update_mod_settings',
    'set_system_status',
    'set_user_preferences',
    'add_event_to_history',
    'clear_history',
    'register_automation_rule',
    'remove_automation_rule',
    'update_automation_rule'
]