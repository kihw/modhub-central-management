import { createSlice } from '@reduxjs/toolkit';

const MAX_NOTIFICATIONS = 50;
const MOBILE_BREAKPOINT = 768;

const getInitialState = () => ({
  sidebarOpen: window.innerWidth >= MOBILE_BREAKPOINT,
  sidebarMinimized: false,
  darkMode: window.matchMedia('(prefers-color-scheme: dark)').matches,
  accentColor: '#3b82f6',
  currentView: 'dashboard',
  notifications: [],
  activeModal: null,
  modalData: null,
  showTourGuide: true,
  tourStep: 0,
  settingsPanelOpen: false,
  isMobileView: window.innerWidth < MOBILE_BREAKPOINT,
  isLoading: false,
  loadingMessage: ''
});

const updateDarkMode = (darkMode) => {
  document.documentElement.classList.toggle('dark', darkMode);
};

const uiSlice = createSlice({
  name: 'ui',
  initialState: getInitialState(),
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, { payload }) => {
      state.sidebarOpen = Boolean(payload);
    },
    toggleSidebarMinimized: (state) => {
      state.sidebarMinimized = !state.sidebarMinimized;
    },
    toggleDarkMode: (state) => {
      state.darkMode = !state.darkMode;
      updateDarkMode(state.darkMode);
    },
    setDarkMode: (state, { payload }) => {
      state.darkMode = Boolean(payload);
      updateDarkMode(state.darkMode);
    },
    setAccentColor: (state, { payload }) => {
      state.accentColor = payload;
      document.documentElement.style.setProperty('--accent-color', payload);
    },
    setCurrentView: (state, { payload }) => {
      state.currentView = String(payload);
    },
    addNotification: (state, { payload }) => {
      const notification = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        ...payload
      };
      state.notifications = [notification, ...state.notifications].slice(0, MAX_NOTIFICATIONS);
    },
    removeNotification: (state, { payload }) => {
      state.notifications = state.notifications.filter(n => n.id !== payload);
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },
    openModal: (state, { payload: { type, data = null } }) => {
      state.activeModal = type;
      state.modalData = data;
    },
    closeModal: (state) => {
      state.activeModal = null;
      state.modalData = null;
    },
    setTourStep: (state, { payload }) => {
      state.tourStep = Number(payload);
    },
    completeTour: (state) => {
      state.showTourGuide = false;
      state.tourStep = 0;
    },
    toggleSettingsPanel: (state) => {
      state.settingsPanelOpen = !state.settingsPanelOpen;
    },
    setSettingsPanelOpen: (state, { payload }) => {
      state.settingsPanelOpen = Boolean(payload);
    },
    setMobileView: (state, { payload }) => {
      const isMobile = Boolean(payload);
      state.isMobileView = isMobile;
      if (isMobile && state.sidebarOpen) {
        state.sidebarOpen = false;
      }
    },
    setLoading: (state, { payload: { isLoading, message = '' } }) => {
      state.isLoading = Boolean(isLoading);
      state.loadingMessage = String(message);
    },
    resetState: () => getInitialState()
  }
});

export const {
  toggleSidebar,
  setSidebarOpen,
  toggleSidebarMinimized,
  toggleDarkMode,
  setDarkMode,
  setAccentColor,
  setCurrentView,
  addNotification,
  removeNotification,
  clearNotifications,
  openModal,
  closeModal,
  setTourStep,
  completeTour,
  toggleSettingsPanel,
  setSettingsPanelOpen,
  setMobileView,
  setLoading,
  resetState
} = uiSlice.actions;

export const selectUI = state => state.ui;
export const selectSidebarOpen = state => state.ui.sidebarOpen;
export const selectSidebarMinimized = state => state.ui.sidebarMinimized;
export const selectDarkMode = state => state.ui.darkMode;
export const selectAccentColor = state => state.ui.accentColor;
export const selectCurrentView = state => state.ui.currentView;
export const selectNotifications = state => state.ui.notifications;
export const selectActiveModal = state => state.ui.activeModal;
export const selectModalData = state => state.ui.modalData;
export const selectTourGuide = state => ({
  show: state.ui.showTourGuide,
  step: state.ui.tourStep
});
export const selectSettingsPanelOpen = state => state.ui.settingsPanelOpen;
export const selectIsMobileView = state => state.ui.isMobileView;
export const selectLoadingState = state => ({
  isLoading: state.ui.isLoading,
  message: state.ui.loadingMessage
});

export default uiSlice.reducer;