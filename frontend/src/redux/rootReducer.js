import { combineReducers } from 'redux';
import modsReducer from './slices/modsSlice';
import settingsReducer from './slices/settingsSlice';
import themeReducer from './slices/themeSlice';
import uiReducer from './slices/uiSlice';
import notificationReducer from './slices/notificationSlice';

const rootReducer = combineReducers({
  mods: modsReducer,
  settings: settingsReducer,
  theme: themeReducer,
  ui: uiReducer,
  notifications: notificationReducer,
});

export default rootReducer;