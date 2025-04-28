import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  notifications: [],
  unreadCount: 0,
};

export const notificationSlice = createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    addNotification: (state, action) => {
      const notification = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        read: false,
        ...action.payload,
      };
      state.notifications.unshift(notification);
      state.unreadCount += 1;
    },
    removeNotification: (state, action) => {
      const index = state.notifications.findIndex(
        (notification) => notification.id === action.payload
      );
      if (index !== -1) {
        const wasUnread = !state.notifications[index].read;
        state.notifications.splice(index, 1);
        if (wasUnread) {
          state.unreadCount = Math.max(0, state.unreadCount - 1);
        }
      }
    },
    markAsRead: (state, action) => {
      const notification = state.notifications.find(
        (notification) => notification.id === action.payload
      );
      if (notification && !notification.read) {
        notification.read = true;
        state.unreadCount = Math.max(0, state.unreadCount - 1);
      }
    },
    markAllAsRead: (state) => {
      state.notifications.forEach((notification) => {
        notification.read = true;
      });
      state.unreadCount = 0;
    },
    clearAllNotifications: (state) => {
      state.notifications = [];
      state.unreadCount = 0;
    },
    // Action pour les notifications de changement d'état d'un mod
    modStateChanged: (state, action) => {
      const { modId, modName, enabled, timestamp } = action.payload;
      const notification = {
        id: Date.now(),
        type: 'MOD_STATE',
        title: `${modName} ${enabled ? 'activé' : 'désactivé'}`,
        message: `Le mod ${modName} a été ${enabled ? 'activé' : 'désactivé'}`,
        modId,
        timestamp: timestamp || new Date().toISOString(),
        read: false,
      };
      state.notifications.unshift(notification);
      state.unreadCount += 1;
    },
    // Action pour les notifications de détection d'application
    applicationDetected: (state, action) => {
      const { appName, modName, action: modAction } = action.payload;
      const notification = {
        id: Date.now(),
        type: 'APP_DETECTED',
        title: `${appName} détecté`,
        message: `${modName} a été ${modAction} suite à la détection de ${appName}`,
        timestamp: new Date().toISOString(),
        read: false,
      };
      state.notifications.unshift(notification);
      state.unreadCount += 1;
    },
    // Action pour les notifications systèmes
    systemNotification: (state, action) => {
      const notification = {
        id: Date.now(),
        type: 'SYSTEM',
        timestamp: new Date().toISOString(),
        read: false,
        ...action.payload,
      };
      state.notifications.unshift(notification);
      state.unreadCount += 1;
    },
  },
});

export const {
  addNotification,
  removeNotification,
  markAsRead,
  markAllAsRead,
  clearAllNotifications,
  modStateChanged,
  applicationDetected,
  systemNotification,
} = notificationSlice.actions;

// Selectors
export const selectNotifications = (state) => state.notifications.notifications;
export const selectUnreadCount = (state) => state.notifications.unreadCount;

export default notificationSlice.reducer;