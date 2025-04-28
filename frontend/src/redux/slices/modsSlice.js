import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// Exemple d'action asynchrone pour charger les mods
export const fetchMods = createAsyncThunk(
  "mods/fetchMods",
  async (_, { rejectWithValue }) => {
    try {
      // Remplacer par votre vraie API call
      const response = await fetch("/api/mods");
      const data = await response.json();
      return data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  items: [],
  activeModId: null,
  status: "idle", // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null,
};

const modsSlice = createSlice({
  name: "mods",
  initialState,
  reducers: {
    setActiveMod: (state, action) => {
      state.activeModId = action.payload;
    },
    addMod: (state, action) => {
      state.items.push(action.payload);
    },
    removeMod: (state, action) => {
      state.items = state.items.filter((mod) => mod.id !== action.payload);
      if (state.activeModId === action.payload) {
        state.activeModId = null;
      }
    },
    updateMod: (state, action) => {
      const index = state.items.findIndex(
        (mod) => mod.id === action.payload.id
      );
      if (index !== -1) {
        state.items[index] = { ...state.items[index], ...action.payload };
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMods.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchMods.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.items = action.payload;
      })
      .addCase(fetchMods.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
      });
  },
});

export const { setActiveMod, addMod, removeMod, updateMod } = modsSlice.actions;

// Sélecteurs
export const selectAllMods = (state) => state.mods.items;
export const selectActiveMod = (state) =>
  state.mods.items.find((mod) => mod.id === state.mods.activeModId);
export const selectModsStatus = (state) => state.mods.status;
export const selectModsError = (state) => state.mods.error;

export default modsSlice.reducer;
