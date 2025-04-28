import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  language: "fr", // Langue par défaut (français)
};

const languageSlice = createSlice({
  name: "language",
  initialState,
  reducers: {
    setLanguage: (state, action) => {
      state.language = action.payload;
    },
  },
});

export const { setLanguage } = languageSlice.actions;
export default languageSlice.reducer;
