import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_ENDPOINTS = {
  MODS: '/api/mods',
  MOD_TOGGLE: (id) => `/api/mods/${id}/toggle`,
  MOD_SETTINGS: (id) => `/api/mods/${id}/settings`,
};

const MAX_HISTORY_ENTRIES = 100;
const STATUS = Object.freeze({
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCEEDED: 'succeeded',
  FAILED: 'failed',
});

const handleAsyncRequest = async (request, rejectWithValue) => {
  try {
    const { data } = await request();
    return data;
  } catch (error) {
    return rejectWithValue(error.response?.data ?? 'An error occurred');
  }
};

export const fetchMods = createAsyncThunk(
  'mods/fetchMods',
  async (_, { rejectWithValue }) => handleAsyncRequest(
    () => axios.get(API_ENDPOINTS.MODS),
    rejectWithValue
  )
);

export const toggleMod = createAsyncThunk(
  'mods/toggleMod',
  async ({ modId, enabled }, { rejectWithValue }) => handleAsyncRequest(
    () => axios.patch(API_ENDPOINTS.MOD_TOGGLE(modId), { enabled }),
    rejectWithValue
  )
);

export const updateModSettings = createAsyncThunk(
  'mods/updateModSettings',
  async ({ modId, settings }, { rejectWithValue }) => handleAsyncRequest(
    () => axios.patch(API_ENDPOINTS.MOD_SETTINGS(modId), settings),
    rejectWithValue
  )
);

export const createCustomMod = createAsyncThunk(
  'mods/createCustomMod',
  async (modData, { rejectWithValue }) => handleAsyncRequest(
    () => axios.post(API_ENDPOINTS.MODS, modData),
    rejectWithValue
  )
);

export const deleteMod = createAsyncThunk(
  'mods/deleteMod',
  async (modId, { rejectWithValue }) => handleAsyncRequest(
    () => axios.delete(`${API_ENDPOINTS.MODS}/${modId}`).then(() => modId),
    rejectWithValue
  )
);

const initialState = {
  mods: [],
  activeMods: new Set(),
  status: STATUS.IDLE,
  error: null,
  modHistory: [],
};

const addToHistory = (state, modId, action, source = 'system') => {
  state.modHistory = [
    {
      modId,
      action,
      timestamp: new Date().toISOString(),
      source,
    },
    ...state.modHistory.slice(0, MAX_HISTORY_ENTRIES - 1),
  ];
};

const updateModState = (state, id, enabled) => {
  if (enabled) {
    state.activeMods.add(id);
  } else {
    state.activeMods.delete(id);
  }
};

const modsSlice = createSlice({
  name: 'mods',
  initialState,
  reducers: {
    setActiveMod: (state, action) => {
      const { modId, isActive } = action.payload;
      updateModState(state, modId, isActive);
      addToHistory(state, modId, isActive ? 'activated' : 'deactivated');
    },
    clearModHistory: (state) => {
      state.modHistory = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMods.pending, (state) => {
        state.status = STATUS.LOADING;
        state.error = null;
      })
      .addCase(fetchMods.fulfilled, (state, action) => {
        state.status = STATUS.SUCCEEDED;
        state.mods = action.payload;
        state.activeMods = new Set(action.payload.filter(mod => mod.enabled).map(mod => mod.id));
      })
      .addCase(fetchMods.rejected, (state, action) => {
        state.status = STATUS.FAILED;
        state.error = action.payload || 'Failed to fetch mods';
      })
      .addCase(toggleMod.pending, (state) => {
        state.status = STATUS.LOADING;
        state.error = null;
      })
      .addCase(toggleMod.fulfilled, (state, action) => {
        state.status = STATUS.SUCCEEDED;
        const { id, enabled } = action.payload;
        const modIndex = state.mods.findIndex(mod => mod.id === id);
        
        if (modIndex !== -1) {
          state.mods[modIndex] = { ...state.mods[modIndex], enabled };
          updateModState(state, id, enabled);
          addToHistory(state, id, enabled ? 'activated' : 'deactivated', 'user');
        }
      })
      .addCase(toggleMod.rejected, (state, action) => {
        state.status = STATUS.FAILED;
        state.error = action.payload || 'Failed to toggle mod';
      })
      .addCase(updateModSettings.fulfilled, (state, action) => {
        const updatedMod = action.payload;
        state.mods = state.mods.map(mod => 
          mod.id === updatedMod.id ? { ...mod, ...updatedMod } : mod
        );
      })
      .addCase(createCustomMod.fulfilled, (state, action) => {
        state.mods.push(action.payload);
        if (action.payload.enabled) {
          updateModState(state, action.payload.id, true);
        }
      })
      .addCase(deleteMod.fulfilled, (state, action) => {
        state.mods = state.mods.filter(mod => mod.id !== action.payload);
        updateModState(state, action.payload, false);
      });
  },
});

export const { setActiveMod, clearModHistory } = modsSlice.actions;

export const selectAllMods = state => state.mods.mods;
export const selectActiveMods = state => Array.from(state.mods.activeMods);
export const selectModById = (state, modId) => state.mods.mods.find(mod => mod.id === modId);
export const selectModStatus = state => state.mods.status;
export const selectModError = state => state.mods.error;
export const selectModHistory = state => state.mods.modHistory;

export default modsSlice.reducer;