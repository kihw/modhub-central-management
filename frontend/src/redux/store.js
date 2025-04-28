import { configureStore } from "@reduxjs/toolkit";
import modsReducer from "./slices/modsSlice";
import settingsReducer from "./slices/settingsSlice";

export const store = configureStore({
  reducer: {
    mods: modsReducer,
    settings: settingsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore ces actions non-sérialisables si nécessaire
        // ignoredActions: ['some/action'],
      },
    }),
  devTools: process.env.NODE_ENV !== "production",
});

export default store;
