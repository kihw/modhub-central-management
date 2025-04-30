import { configureStore } from '@reduxjs/toolkit';
import { combineReducers } from 'redux';
import { persistStore, persistReducer, FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import thunk from 'redux-thunk';

import authReducer from '@/slices/authSlice';
import projectReducer from '@/slices/projectSlice';
import uiReducer from '@/slices/uiSlice';
import settingsReducer from '@/slices/settingsSlice';
import notificationReducer from '@/slices/notificationSlice';

const persistConfig = {
  key: 'modhub-central',
  version: 1,
  storage,
  whitelist: ['auth', 'settings'],
  blacklist: ['ui', 'notification', 'project'],
  migrate: (state) => Promise.resolve(state),
  timeout: 2000,
  throttle: 1000,
  debug: process.env.NODE_ENV !== 'production',
};

const rootReducer = combineReducers({
  auth: authReducer,
  project: projectReducer,
  ui: uiReducer,
  settings: settingsReducer,
  notification: notificationReducer,
});

const persistedReducer = persistReducer(persistConfig, rootReducer);

const middleware = (getDefaultMiddleware) =>
  getDefaultMiddleware({
    serializableCheck: {
      ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      ignoredPaths: [
        'ui.temporaryData',
        'notification.queue',
        'project.cache',
        'auth.session'
      ],
      warnAfter: 200,
    },
    immutableCheck: {
      warnAfter: 200,
      ignoredPaths: ['notification.queue'],
    },
  }).concat(thunk);

export const store = configureStore({
  reducer: persistedReducer,
  middleware,
  devTools: process.env.NODE_ENV !== 'production',
  preloadedState: undefined,
});

export const persistor = persistStore(store, null, () => {
  store.dispatch({ type: 'PERSIST_READY' });
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export default store;