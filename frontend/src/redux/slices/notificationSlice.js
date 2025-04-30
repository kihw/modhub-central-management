import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  notifications: [],
  unreadCount: 0,
  maxNotifications: 100
};

const createNotification = (type, payload) => ({
  id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
  timestamp: payload.timestamp || new Date().toISOString(),
  read: false,
  type,
  priority: payload.priority || 'normal',
  ...payload
});

const removeOldestNotification = (state) => {
  const oldestUnreadIndex = state.notifications.findIndex(n => !n.read);
  if (oldestUnreadIndex !== -1) {
    state.notifications.splice(oldestUnreadIndex, 1);
  } else {
    state.notifications.pop();
  }
};

const addNotificationHelper = (state, notification) => {
  if (state.notifications.length >= state.maxNotifications) {
    removeOldestNotification(state);
  }
  state.notifications.unshift(notification);
  state.unreadCount++;
};

export const notificationSlice = createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    addNotification: (state, action) => {
      addNotificationHelper(state, createNotification('GENERIC', action.payload));
    },
    removeNotification: (state, action) => {
      const index = state.notifications.findIndex(n => n.id === action.payload);
      if (index !== -1) {
        const wasUnread = !state.notifications[index].read;
        state.notifications.splice(index, 1);
        if (wasUnread) {
          state.unreadCount = Math.max(0, state.unreadCount - 1);
        }
      }
    },
    markAsRead: (state, action) => {
      const notification = state.notifications.find(n => n.id === action.payload);
      if (notification && !notification.read) {
        notification.read = true;
        state.unreadCount = Math.max(0, state.unreadCount - 1);
      }
    },
    markAllAsRead: (state) => {
      state.notifications.forEach(n => { n.read = true; });
      state.unreadCount = 0;
    },
    clearAllNotifications: (state) => {
      state.notifications = [];
      state.unreadCount = 0;
    },
    modStateChanged: (state, action) => {
      const { modId, modName, enabled, timestamp } = action.payload;
      addNotificationHelper(state, createNotification('MOD_STATE', {
        title: `${modName} ${enabled ? 'activé' : 'désactivé'}`,
        message: `Le mod ${modName} a été ${enabled ? 'activé' : 'désactivé'}`,
        modId,
        timestamp,
        priority: 'high'
      }));
    },
    applicationDetected: (state, action) => {
      const { appName, modName, action: modAction } = action.payload;
      addNotificationHelper(state, createNotification('APP_DETECTED', {
        title: `${appName} détecté`,
        message: `${modName} a été ${modAction} suite à la détection de ${appName}`,
        priority: 'medium'
      }));
    },
    systemNotification: (state, action) => {
      addNotificationHelper(state, createNotification('SYSTEM', {
        ...action.payload,
        priority: action.payload.priority || 'high'
      }));
    },
    setMaxNotifications: (state, action) => {
      const newMax = Math.max(1, Math.floor(action.payload));
      state.maxNotifications = newMax;
      while (state.notifications.length > newMax) {
        const removed = state.notifications.pop();
        if (!removed.read) {
          state.unreadCount = Math.max(0, state.unreadCount - 1);
        }
      }
    }
  }
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
  setMaxNotifications
} = notificationSlice.actions;

export const selectNotifications = state => state.notifications.notifications;
export const selectUnreadCount = state => state.notifications.unreadCount;
export const selectMaxNotifications = state => state.notifications.maxNotifications;

export default notificationSlice.reducer;