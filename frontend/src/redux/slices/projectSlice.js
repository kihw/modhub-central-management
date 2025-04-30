import { createSlice } from '@reduxjs/toolkit';

const MOD_TYPES = Object.freeze({
  GAMING: 'gamingMod',
  NIGHT: 'nightMod',
  MEDIA: 'mediaMod',
  CUSTOM: 'customMod'
});

const MAX_LOGS = 1000;

const DEFAULT_MOD_STATE = Object.freeze({
  active: false,
  rules: []
});

const initialState = {
  mods: {
    [MOD_TYPES.GAMING]: {
      ...DEFAULT_MOD_STATE,
      id: MOD_TYPES.GAMING,
      name: 'Gaming Mod',
      description: 'Optimize your peripherals for gaming performance',
      icon: 'gamepad',
      color: '#E74C3C',
      settings: Object.freeze({
        dpiBoost: true,
        rgbMode: 'gaming',
        audioEnhance: true,
        priorityBoost: true
      }),
      rules: [
        { id: 'gaming-rule-1', name: 'Detect games', processPatterns: ['steam.exe', 'epicgames.exe', 'game.exe'], enabled: true },
        { id: 'gaming-rule-2', name: 'Custom DPI settings', enabled: true }
      ]
    },
    [MOD_TYPES.NIGHT]: {
      ...DEFAULT_MOD_STATE,
      id: MOD_TYPES.NIGHT,
      name: 'Night Mod',
      description: 'Optimize display and lighting for evening use',
      icon: 'moon',
      color: '#34495E',
      settings: Object.freeze({
        blueLight: 'reduced',
        brightness: 60,
        rgbMode: 'dim',
        scheduledStart: '22:00',
        scheduledEnd: '07:00'
      }),
      rules: [
        { id: 'night-rule-1', name: 'Time-based activation', timeCondition: true, enabled: true },
        { id: 'night-rule-2', name: 'Inactivity detection', inactivityTrigger: 30, enabled: true }
      ]
    },
    [MOD_TYPES.MEDIA]: {
      ...DEFAULT_MOD_STATE,
      id: MOD_TYPES.MEDIA,
      name: 'Media Mod',
      description: 'Enhanced audio and lighting for media consumption',
      icon: 'film',
      color: '#3498DB',
      settings: Object.freeze({
        audioProfile: 'media',
        surroundSound: true,
        rgbMode: 'ambient',
        enhancedContrast: true
      }),
      rules: [
        { id: 'media-rule-1', name: 'Detect media apps', processPatterns: ['vlc.exe', 'netflix.exe', 'spotify.exe'], enabled: true }
      ]
    },
    [MOD_TYPES.CUSTOM]: {
      ...DEFAULT_MOD_STATE,
      id: MOD_TYPES.CUSTOM,
      name: 'Custom Mod',
      description: 'Your personalized mod configuration',
      icon: 'sliders',
      color: '#9B59B6',
      settings: Object.freeze({
        customSetting1: false,
        customSetting2: 'default',
        rgbMode: 'custom'
      }),
      rules: [
        { id: 'custom-rule-1', name: 'Custom rule', enabled: false }
      ]
    }
  },
  activeProcesses: [],
  systemStatus: {
    timeOfDay: null,
    userActive: true,
    batteryLevel: 100,
    batteryCharging: true,
    cpuUsage: 0,
    ramUsage: 0,
    lastActivity: Date.now()
  },
  logs: [],
  settings: {
    startWithSystem: true,
    notificationsEnabled: true,
    conflictResolution: 'priority',
    dataCollection: false,
    theme: 'system',
    advancedMode: false,
    checkForUpdates: true
  }
};

const createLogEntry = (action, type = 'system') => ({
  id: crypto.randomUUID(),
  timestamp: new Date().toISOString(),
  action,
  type
});

const projectSlice = createSlice({
  name: 'project',
  initialState,
  reducers: {
    toggleMod: (state, { payload: modId }) => {
      const mod = state.mods[modId];
      if (!mod) return;
      
      mod.active = !mod.active;
      state.logs = [createLogEntry(`${mod.active ? 'Activated' : 'Deactivated'} ${mod.name}`, 'user'), ...state.logs].slice(0, MAX_LOGS);
    },
    
    updateModSettings: (state, { payload: { modId, settings } }) => {
      const mod = state.mods[modId];
      if (!mod) return;

      mod.settings = { ...mod.settings, ...settings };
      state.logs = [createLogEntry(`Updated settings for ${mod.name}`, 'user'), ...state.logs].slice(0, MAX_LOGS);
    },
    
    updateModRule: (state, { payload: { modId, ruleId, ruleData } }) => {
      const mod = state.mods[modId];
      if (!mod) return;

      const ruleIndex = mod.rules.findIndex(rule => rule.id === ruleId);
      if (ruleIndex === -1) return;

      mod.rules[ruleIndex] = { ...mod.rules[ruleIndex], ...ruleData };
      state.logs = [createLogEntry(`Updated rule "${mod.rules[ruleIndex].name}" for ${mod.name}`, 'user'), ...state.logs].slice(0, MAX_LOGS);
    },
    
    addModRule: (state, { payload: { modId, rule } }) => {
      const mod = state.mods[modId];
      if (!mod) return;

      const newRule = { ...rule, id: `${modId}-rule-${crypto.randomUUID()}` };
      mod.rules.push(newRule);
      state.logs = [createLogEntry(`Added new rule "${rule.name}" to ${mod.name}`, 'user'), ...state.logs].slice(0, MAX_LOGS);
    },
    
    removeModRule: (state, { payload: { modId, ruleId } }) => {
      const mod = state.mods[modId];
      if (!mod) return;

      const ruleIndex = mod.rules.findIndex(rule => rule.id === ruleId);
      if (ruleIndex === -1) return;

      const ruleName = mod.rules[ruleIndex].name;
      mod.rules = mod.rules.filter(rule => rule.id !== ruleId);
      state.logs = [createLogEntry(`Removed rule "${ruleName}" from ${mod.name}`, 'user'), ...state.logs].slice(0, MAX_LOGS);
    },
    
    updateActiveProcesses: (state, { payload }) => {
      state.activeProcesses = Array.isArray(payload) ? payload : [];
    },
    
    updateSystemStatus: (state, { payload }) => {
      state.systemStatus = { ...state.systemStatus, ...payload, lastActivity: Date.now() };
    },
    
    addLog: (state, { payload: { action, type } }) => {
      state.logs = [createLogEntry(action, type), ...state.logs].slice(0, MAX_LOGS);
    },
    
    updateSettings: (state, { payload }) => {
      state.settings = { ...state.settings, ...payload };
      state.logs = [createLogEntry('Updated application settings'), ...state.logs].slice(0, MAX_LOGS);
    },
    
    createCustomMod: (state, { payload }) => {
      const { id } = payload;
      if (state.mods[id] || Object.values(MOD_TYPES).includes(id)) return;

      state.mods[id] = {
        ...DEFAULT_MOD_STATE,
        ...payload,
        rules: payload.rules?.map(rule => ({ ...rule, id: `${id}-rule-${crypto.randomUUID()}` })) || []
      };
      state.logs = [createLogEntry(`Created new custom mod: ${payload.name}`, 'user'), ...state.logs].slice(0, MAX_LOGS);
    },
    
    deleteMod: (state, { payload: modId }) => {
      if (Object.values(MOD_TYPES).includes(modId) || !state.mods[modId]) return;

      const modName = state.mods[modId].name;
      delete state.mods[modId];
      state.logs = [createLogEntry(`Deleted mod: ${modName}`, 'user'), ...state.logs].slice(0, MAX_LOGS);
    },
    
    clearLogs: (state) => {
      state.logs = [];
    }
  }
});

export const {
  toggleMod,
  updateModSettings,
  updateModRule,
  addModRule,
  removeModRule,
  updateActiveProcesses,
  updateSystemStatus,
  addLog,
  updateSettings,
  createCustomMod,
  deleteMod,
  clearLogs
} = projectSlice.actions;

export default projectSlice.reducer;