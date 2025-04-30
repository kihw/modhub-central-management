import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer, FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import rootReducer from './rootReducer';

const persistConfig = {
  key: 'modhub-central',
  storage,
  whitelist: ['settings', 'theme', 'mods', 'rules'],
  version: 1,
  timeout: 2000,
  migrate: (state) => Promise.resolve(state),
  blacklist: ['temp', 'cache'],
  debug: process.env.NODE_ENV === 'development',
};

const persistedReducer = persistReducer(persistConfig, rootReducer);

const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
        warnAfter: 128,
        ignoreState: false,
      },
      immutableCheck: { warnAfter: 128 },
    }),
  devTools: process.env.NODE_ENV === 'development',
});

const persistor = persistStore(store, undefined, () => {
  store.dispatch({ type: 'PERSIST_LOADED' });
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export { store, persistor };
export default store;