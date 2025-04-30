import { combineReducers } from 'redux';
import type { StateFromReducersMapObject } from 'redux';
import modsReducer from './slices/modsSlice';
import settingsReducer from './slices/settingsSlice';
import themeReducer from './slices/themeSlice';
import uiReducer from './slices/uiSlice';
import notificationReducer from './slices/notificationSlice';

const reducers = {
  mods: modsReducer,
  settings: settingsReducer,
  theme: themeReducer,
  ui: uiReducer,
  notifications: notificationReducer
} as const;

export type RootState = StateFromReducersMapObject<typeof reducers>;

export default combineReducers<RootState>(reducers);