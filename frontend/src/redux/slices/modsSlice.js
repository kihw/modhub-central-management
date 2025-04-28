import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// API calls
export const fetchMods = createAsyncThunk(
  'mods/fetchMods',
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get('/api/mods');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const toggleMod = createAsyncThunk(
  'mods/toggleMod',
  async ({ modId, enabled }, { rejectWithValue }) => {
    try {
      const response = await axios.patch(`/api/mods/${modId}/toggle`, { enabled });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const updateModSettings = createAsyncThunk(
  'mods/updateModSettings',
  async ({ modId, settings }, { rejectWithValue }) => {
    try {
      const response = await axios.patch(`/api/mods/${modId}/settings`, settings);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const createCustomMod = createAsyncThunk(
  'mods/createCustomMod',
  async (modData, { rejectWithValue }) => {
    try {
      const response = await axios.post('/api/mods', modData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

export const deleteMod = createAsyncThunk(
  'mods/deleteMod',
  async (modId, { rejectWithValue }) => {
    try {
      await axios.delete(`/api/mods/${modId}`);
      return modId;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

const initialState = {
  mods: [],
  activeMods: [],
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null,
  modHistory: [], // keeps track of mod activation/deactivation events
};

const modsSlice = createSlice({
  name: 'mods',
  initialState,
  reducers: {
    setActiveMod: (state, action) => {
      const { modId, isActive } = action.payload;
      
      if (isActive) {
        if (!state.activeMods.includes(modId)) {
          state.activeMods.push(modId);
        }
      } else {
        state.activeMods = state.activeMods.filter(id => id !== modId);
      }
      
      // Add to history
      state.modHistory.push({
        modId,
        action: isActive ? 'activated' : 'deactivated',
        timestamp: new Date().toISOString(),
      });
      
      // Keep history limited to 100 entries
      if (state.modHistory.length > 100) {
        state.modHistory.shift();
      }
    },
    clearModHistory: (state) => {
      state.modHistory = [];
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Mods
      .addCase(fetchMods.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchMods.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.mods = action.payload;
        // Initialize activeMods based on enabled status
        state.activeMods = action.payload
          .filter(mod => mod.enabled)
          .map(mod => mod.id);
      })
      .addCase(fetchMods.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || 'Failed to fetch mods';
      })
      
      // Toggle Mod
      .addCase(toggleMod.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(toggleMod.fulfilled, (state, action) => {
        state.status = 'succeeded';
        const { id, enabled } = action.payload;
        const mod = state.mods.find(mod => mod.id === id);
        if (mod) {
          mod.enabled = enabled;
        }
        
        // Update active mods list
        if (enabled) {
          if (!state.activeMods.includes(id)) {
            state.activeMods.push(id);
          }
        } else {
          state.activeMods = state.activeMods.filter(modId => modId !== id);
        }
        
        // Add to history
        state.modHistory.push({
          modId: id,
          action: enabled ? 'activated' : 'deactivated',
          timestamp: new Date().toISOString(),
          source: 'user',
        });
        
        // Keep history limited
        if (state.modHistory.length > 100) {
          state.modHistory.shift();
        }
      })
      .addCase(toggleMod.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || 'Failed to toggle mod';
      })
      
      // Update Mod Settings
      .addCase(updateModSettings.fulfilled, (state, action) => {
        const updatedMod = action.payload;
        const index = state.mods.findIndex(mod => mod.id === updatedMod.id);
        if (index !== -1) {
          state.mods[index] = updatedMod;
        }
      })
      
      // Create Custom Mod
      .addCase(createCustomMod.fulfilled, (state, action) => {
        state.mods.push(action.payload);
        // If the new mod is enabled, add it to active mods
        if (action.payload.enabled) {
          state.activeMods.push(action.payload.id);
        }
      })
      
      // Delete Mod
      .addCase(deleteMod.fulfilled, (state, action) => {
        state.mods = state.mods.filter(mod => mod.id !== action.payload);
        state.activeMods = state.activeMods.filter(id => id !== action.payload);
      });
  },
});

export const { setActiveMod, clearModHistory } = modsSlice.actions;

// Selectors
export const selectAllMods = state => state.mods.mods;
export const selectActiveMods = state => state.mods.activeMods;
export const selectModById = (state, modId) => 
  state.mods.mods.find(mod => mod.id === modId);
export const selectModStatus = state => state.mods.status;
export const selectModError = state => state.mods.error;
export const selectModHistory = state => state.mods.modHistory;

export default modsSlice.reducer;