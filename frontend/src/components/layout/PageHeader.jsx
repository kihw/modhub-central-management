import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBell, faCog, faQuestionCircle, faUser } from '@fortawesome/free-solid-svg-icons';
import { useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';

const PageHeader = ({ title, subtitle, icon }) => {
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const location = useLocation();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [activeProcesses, setActiveProcesses] = useState([]);

  // Update time every minute
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);

    // Mock active processes data
    setActiveProcesses(['chrome.exe', 'spotify.exe', 'discord.exe']);

    // Mock notifications data
    setNotifications([
      { id: 1, title: 'Gaming Mod Activated', message: 'Detected CS:GO running', time: '2 min ago', read: false },
      { id: 2, title: 'Night Mode', message: 'Scheduled to activate in 30 minutes', time: '15 min ago', read: true },
    ]);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (date) => {
    return date.toLocaleDateString([], { weekday: 'long', month: 'short', day: 'numeric' });
  };

  const toggleNotifications = () => {
    setShowNotifications(!showNotifications);
  };

  const markAllAsRead = () => {
    setNotifications(notifications.map(notif => ({ ...notif, read: true })));
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <header className="sticky top-0 z-10 bg-gray-900 shadow-lg border-b border-gray-700">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Left section: Page title and breadcrumbs */}
          <div className="flex items-center space-x-3">
            {icon && (
              <div className="text-blue-400 text-xl">
                <FontAwesomeIcon icon={icon} />
              </div>
            )}
            <div>
              <h1 className="text-xl font-bold text-white">{title}</h1>
              {subtitle && <p className="text-sm text-gray-400">{subtitle}</p>}
            </div>
          </div>

          {/* Right section: System info and actions */}
          <div className="flex items-center space-x-6">
            {/* System time and date */}
            <div className="hidden md:flex flex-col items-end">
              <span className="text-white font-semibold">{formatTime(currentTime)}</span>
              <span className="text-xs text-gray-400">{formatDate(currentTime)}</span>
            </div>

            {/* Active processes indicator */}
            <div className="hidden lg:flex items-center">
              <div className="px-3 py-1 bg-gray-800 rounded-full flex items-center">
                <span className="relative flex h-2 w-2 mr-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
                <span className="text-xs text-gray-300">{activeProcesses.length} processes</span>
              </div>
            </div>

            {/* Notifications */}
            <div className="relative">
              <button 
                onClick={toggleNotifications}
                className="text-gray-300 hover:text-white p-2 rounded-full hover:bg-gray-700 transition-colors duration-200"
              >
                <FontAwesomeIcon icon={faBell} />
                {unreadCount > 0 && (
                  <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-500 rounded-full">
                    {unreadCount}
                  </span>
                )}
              </button>

              {/* Notification dropdown */}
              {showNotifications && (
                <motion.div 
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="absolute right-0 mt-2 w-80 bg-gray-800 rounded-md shadow-lg py-1 z-50 border border-gray-700"
                >
                  <div className="px-4 py-2 border-b border-gray-700 flex justify-between items-center">
                    <h3 className="text-sm font-medium text-white">Notifications</h3>
                    <button 
                      onClick={markAllAsRead}
                      className="text-xs text-blue-400 hover:text-blue-300"
                    >
                      Mark all as read
                    </button>
                  </div>
                  <div className="max-h-80 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <div className="px-4 py-6 text-center text-gray-400">
                        <p>No notifications</p>
                      </div>
                    ) : (
                      notifications.map(notification => (
                        <div 
                          key={notification.id} 
                          className={`px-4 py-3 hover:bg-gray-700 cursor-pointer border-l-2 ${notification.read ? 'border-transparent' : 'border-blue-500'}`}
                        >
                          <div className="flex justify-between">
                            <p className="text-sm font-medium text-white">{notification.title}</p>
                            <span className="text-xs text-gray-400">{notification.time}</span>
                          </div>
                          <p className="text-xs text-gray-400 mt-1">{notification.message}</p>
                        </div>
                      ))
                    )}
                  </div>
                  <div className="px-4 py-2 border-t border-gray-700 text-center">
                    <button className="text-xs text-blue-400 hover:text-blue-300">
                      View all notifications
                    </button>
                  </div>
                </motion.div>
              )}
            </div>

            {/* Settings */}
            <button className="text-gray-300 hover:text-white p-2 rounded-full hover:bg-gray-700 transition-colors duration-200">
              <FontAwesomeIcon icon={faCog} />
            </button>

            {/* Help */}
            <button className="text-gray-300 hover:text-white p-2 rounded-full hover:bg-gray-700 transition-colors duration-200">
              <FontAwesomeIcon icon={faQuestionCircle} />
            </button>

            {/* User profile */}
            <button className="text-gray-300 hover:text-white p-2 rounded-full hover:bg-gray-700 transition-colors duration-200">
              <FontAwesomeIcon icon={faUser} />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default PageHeader;