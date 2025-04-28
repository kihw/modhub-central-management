import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import { combineReducers } from 'redux';
import thunk from 'redux-thunk';

// Import reducers (these will need to be created separately)
import modsReducer from './slices/modsSlice';
import processesReducer from './slices/processesSlice';
import settingsReducer from './slices/settingsSlice';
import automationReducer from './slices/automationSlice';
import uiReducer from './slices/uiSlice';

// Configure Redux Persist
const persistConfig = {
  key: 'root',
  storage,
  whitelist: ['settings', 'mods', 'automation'], // Only persist these reducers
};

const rootReducer = combineReducers({
  mods: modsReducer,
  processes: processesReducer,
  settings: settingsReducer,
  automation: automationReducer,
  ui: uiReducer,
});

const persistedReducer = persistReducer(persistConfig, rootReducer);

// Configure store with middleware
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
        // Ignore these field paths in all actions
        ignoredActionPaths: ['meta.arg', 'payload.timestamp'],
        // Ignore these paths in the state
        ignoredPaths: ['items.dates'],
      },
    }).concat(thunk),
  devTools: process.env.NODE_ENV !== 'production',
});

export const persistor = persistStore(store);

export default { store, persistor };