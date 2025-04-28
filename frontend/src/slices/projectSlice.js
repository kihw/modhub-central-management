import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  mods: {
    gamingMod: {
      id: 'gamingMod',
      name: 'Gaming Mod',
      description: 'Optimize your peripherals for gaming performance',
      icon: 'gamepad',
      active: false,
      color: '#E74C3C',
      settings: {
        dpiBoost: true,
        rgbMode: 'gaming',
        audioEnhance: true,
        priorityBoost: true
      },
      rules: [
        { id: 'rule1', name: 'Detect games', processPatterns: ['steam.exe', 'epicgames.exe', 'game.exe'], enabled: true },
        { id: 'rule2', name: 'Custom DPI settings', enabled: true }
      ]
    },
    nightMod: {
      id: 'nightMod',
      name: 'Night Mod',
      description: 'Optimize display and lighting for evening use',
      icon: 'moon',
      active: false,
      color: '#34495E',
      settings: {
        blueLight: 'reduced',
        brightness: 60,
        rgbMode: 'dim',
        scheduledStart: '22:00',
        scheduledEnd: '07:00'
      },
      rules: [
        { id: 'rule1', name: 'Time-based activation', timeCondition: true, enabled: true },
        { id: 'rule2', name: 'Inactivity detection', inactivityTrigger: 30, enabled: true }
      ]
    },
    mediaMod: {
      id: 'mediaMod',
      name: 'Media Mod',
      description: 'Enhanced audio and lighting for media consumption',
      icon: 'film',
      active: false,
      color: '#3498DB',
      settings: {
        audioProfile: 'media',
        surroundSound: true,
        rgbMode: 'ambient',
        enhancedContrast: true
      },
      rules: [
        { id: 'rule1', name: 'Detect media apps', processPatterns: ['vlc.exe', 'netflix.exe', 'spotify.exe'], enabled: true }
      ]
    },
    customMod: {
      id: 'customMod',
      name: 'Custom Mod',
      description: 'Your personalized mod configuration',
      icon: 'sliders',
      active: false,
      color: '#9B59B6',
      settings: {
        customSetting1: false,
        customSetting2: 'default',
        rgbMode: 'custom'
      },
      rules: [
        { id: 'rule1', name: 'Custom rule', enabled: false }
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
    conflictResolution: 'priority', // priority, manual, last-wins
    dataCollection: false,
    theme: 'system', // light, dark, system
    advancedMode: false,
    checkForUpdates: true
  }
};

export const projectSlice = createSlice({
  name: 'project',
  initialState,
  reducers: {
    toggleMod: (state, action) => {
      const modId = action.payload;
      state.mods[modId].active = !state.mods[modId].active;
      
      // Log the action
      state.logs.push({
        timestamp: new Date().toISOString(),
        action: `${state.mods[modId].active ? 'Activated' : 'Deactivated'} ${state.mods[modId].name}`,
        type: 'user'
      });
    },
    
    updateModSettings: (state, action) => {
      const { modId, settings } = action.payload;
      state.mods[modId].settings = {
        ...state.mods[modId].settings,
        ...settings
      };
      
      state.logs.push({
        timestamp: new Date().toISOString(),
        action: `Updated settings for ${state.mods[modId].name}`,
        type: 'user'
      });
    },
    
    updateModRule: (state, action) => {
      const { modId, ruleId, ruleData } = action.payload;
      const ruleIndex = state.mods[modId].rules.findIndex(rule => rule.id === ruleId);
      
      if (ruleIndex !== -1) {
        state.mods[modId].rules[ruleIndex] = {
          ...state.mods[modId].rules[ruleIndex],
          ...ruleData
        };
        
        state.logs.push({
          timestamp: new Date().toISOString(),
          action: `Updated rule "${state.mods[modId].rules[ruleIndex].name}" for ${state.mods[modId].name}`,
          type: 'user'
        });
      }
    },
    
    addModRule: (state, action) => {
      const { modId, rule } = action.payload;
      state.mods[modId].rules.push(rule);
      
      state.logs.push({
        timestamp: new Date().toISOString(),
        action: `Added new rule "${rule.name}" to ${state.mods[modId].name}`,
        type: 'user'
      });
    },
    
    removeModRule: (state, action) => {
      const { modId, ruleId } = action.payload;
      const ruleIndex = state.mods[modId].rules.findIndex(rule => rule.id === ruleId);
      
      if (ruleIndex !== -1) {
        const ruleName = state.mods[modId].rules[ruleIndex].name;
        state.mods[modId].rules.splice(ruleIndex, 1);
        
        state.logs.push({
          timestamp: new Date().toISOString(),
          action: `Removed rule "${ruleName}" from ${state.mods[modId].name}`,
          type: 'user'
        });
      }
    },
    
    updateActiveProcesses: (state, action) => {
      state.activeProcesses = action.payload;
    },
    
    updateSystemStatus: (state, action) => {
      state.systemStatus = {
        ...state.systemStatus,
        ...action.payload
      };
    },
    
    addLog: (state, action) => {
      state.logs.push({
        timestamp: new Date().toISOString(),
        ...action.payload
      });
      
      // Keep only the last 1000 logs
      if (state.logs.length > 1000) {
        state.logs = state.logs.slice(-1000);
      }
    },
    
    updateSettings: (state, action) => {
      state.settings = {
        ...state.settings,
        ...action.payload
      };
      
      state.logs.push({
        timestamp: new Date().toISOString(),
        action: 'Updated application settings',
        type: 'system'
      });
    },
    
    createCustomMod: (state, action) => {
      const { id, name, description, icon, color, settings, rules } = action.payload;
      
      state.mods[id] = {
        id,
        name,
        description,
        icon,
        active: false,
        color,
        settings,
        rules: rules || []
      };
      
      state.logs.push({
        timestamp: new Date().toISOString(),
        action: `Created new custom mod: ${name}`,
        type: 'user'
      });
    },
    
    deleteMod: (state, action) => {
      const modId = action.payload;
      
      // Only allow deletion of custom mods
      if (modId !== 'gamingMod' && modId !== 'nightMod' && modId !== 'mediaMod' && state.mods[modId]) {
        const modName = state.mods[modId].name;
        delete state.mods[modId];
        
        state.logs.push({
          timestamp: new Date().toISOString(),
          action: `Deleted mod: ${modName}`,
          type: 'user'
        });
      }
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