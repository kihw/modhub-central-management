import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  // Sidebar state
  sidebarOpen: true,
  sidebarMinimized: false,
  
  // Theme settings
  darkMode: window.matchMedia('(prefers-color-scheme: dark)').matches,
  accentColor: '#3b82f6', // Default blue
  
  // Layout
  currentView: 'dashboard',
  
  // Notification system
  notifications: [],
  
  // Modal management
  activeModal: null,
  modalData: null,
  
  // Tour guide for first-time users
  showTourGuide: true,
  tourStep: 0,
  
  // Settings panel
  settingsPanelOpen: false,
  
  // Mobile view detection
  isMobileView: window.innerWidth < 768,
  
  // Loading states
  isLoading: false,
  loadingMessage: '',
};

export const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action) => {
      state.sidebarOpen = action.payload;
    },
    toggleSidebarMinimized: (state) => {
      state.sidebarMinimized = !state.sidebarMinimized;
    },
    toggleDarkMode: (state) => {
      state.darkMode = !state.darkMode;
      document.documentElement.classList.toggle('dark', state.darkMode);
    },
    setDarkMode: (state, action) => {
      state.darkMode = action.payload;
      document.documentElement.classList.toggle('dark', state.darkMode);
    },
    setAccentColor: (state, action) => {
      state.accentColor = action.payload;
      document.documentElement.style.setProperty('--accent-color', action.payload);
    },
    setCurrentView: (state, action) => {
      state.currentView = action.payload;
    },
    addNotification: (state, action) => {
      const id = Date.now();
      state.notifications.push({
        id,
        ...action.payload,
        timestamp: new Date().toISOString(),
      });
      
      // Auto-remove notifications after 5 seconds if they're not persistent
      if (!action.payload.persistent) {
        setTimeout(() => {
          const index = state.notifications.findIndex(n => n.id === id);
          if (index !== -1) {
            state.notifications.splice(index, 1);
          }
        }, 5000);
      }
    },
    removeNotification: (state, action) => {
      state.notifications = state.notifications.filter(
        notification => notification.id !== action.payload
      );
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },
    openModal: (state, action) => {
      state.activeModal = action.payload.type;
      state.modalData = action.payload.data || null;
    },
    closeModal: (state) => {
      state.activeModal = null;
      state.modalData = null;
    },
    setTourStep: (state, action) => {
      state.tourStep = action.payload;
    },
    completeTour: (state) => {
      state.showTourGuide = false;
      state.tourStep = 0;
    },
    toggleSettingsPanel: (state) => {
      state.settingsPanelOpen = !state.settingsPanelOpen;
    },
    setSettingsPanelOpen: (state, action) => {
      state.settingsPanelOpen = action.payload;
    },
    setMobileView: (state, action) => {
      state.isMobileView = action.payload;
      // Auto-close sidebar on mobile if it's currently open
      if (action.payload && state.sidebarOpen) {
        state.sidebarOpen = false;
      }
    },
    setLoading: (state, action) => {
      state.isLoading = action.payload.isLoading;
      state.loadingMessage = action.payload.message || '';
    }
  },
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
  setLoading
} = uiSlice.actions;

// Selectors
export const selectSidebarOpen = (state) => state.ui.sidebarOpen;
export const selectSidebarMinimized = (state) => state.ui.sidebarMinimized;
export const selectDarkMode = (state) => state.ui.darkMode;
export const selectAccentColor = (state) => state.ui.accentColor;
export const selectCurrentView = (state) => state.ui.currentView;
export const selectNotifications = (state) => state.ui.notifications;
export const selectActiveModal = (state) => state.ui.activeModal;
export const selectModalData = (state) => state.ui.modalData;
export const selectTourGuide = (state) => ({
  show: state.ui.showTourGuide,
  step: state.ui.tourStep
});
export const selectSettingsPanelOpen = (state) => state.ui.settingsPanelOpen;
export const selectIsMobileView = (state) => state.ui.isMobileView;
export const selectLoadingState = (state) => ({
  isLoading: state.ui.isLoading,
  message: state.ui.loadingMessage
});

export default uiSlice.reducer;