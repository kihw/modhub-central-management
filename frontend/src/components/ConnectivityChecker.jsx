import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FiWifi, FiWifiOff, FiRefreshCw } from 'react-icons/fi';

/**
 * ConnectivityChecker - Component to monitor and display the backend connectivity status
 * 
 * @param {Object} props
 * @param {number} props.checkInterval - Interval in ms between connectivity checks (default: 30000)
 * @param {Function} props.onStatusChange - Callback when connectivity status changes
 * @param {boolean} props.showMiniDisplay - Whether to show a mini status indicator
 * @param {string} props.className - Additional CSS classes
 */
const ConnectivityChecker = ({ 
  checkInterval = 30000, 
  onStatusChange = () => {}, 
  showMiniDisplay = false,
  className = "" 
}) => {
  const [isConnected, setIsConnected] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const [lastChecked, setLastChecked] = useState(null);
  const [isChecking, setIsChecking] = useState(false);
  const [backendInfo, setBackendInfo] = useState(null);

  // Function to check backend connectivity
  const checkConnectivity = async () => {
    if (isChecking) return;
    
    setIsChecking(true);
    try {
      const response = await axios.get('/api/health', {
        timeout: 5000
      });
      
      const wasConnected = isConnected;
      setIsConnected(true);
      setBackendInfo(response.data);
      setLastChecked(new Date());
      setRetryCount(0);
      
      // Call the status change callback if the status changed
      if (wasConnected === false || wasConnected === null) {
        onStatusChange(true, response.data);
      }
      
    } catch (error) {
      console.error('Backend connectivity check failed:', error);
      
      const wasConnected = isConnected;
      setIsConnected(false);
      setRetryCount(prev => prev + 1);
      setLastChecked(new Date());
      
      // Call the status change callback if the status changed
      if (wasConnected === true || wasConnected === null) {
        onStatusChange(false, { error: error.message });
      }
    } finally {
      setIsChecking(false);
    }
  };

  // Initial check and setup periodic checks
  useEffect(() => {
    // Initial check
    checkConnectivity();
    
    // Set up periodic checks
    const intervalId = setInterval(checkConnectivity, checkInterval);
    
    // Cleanup
    return () => clearInterval(intervalId);
  }, [checkInterval]);

  if (showMiniDisplay) {
    return (
      <div className={`inline-flex items-center ${className}`}>
        {isConnected === null ? (
          <span className="text-gray-500">
            <FiRefreshCw className="animate-spin" />
          </span>
        ) : isConnected ? (
          <span className="text-green-500" title="Connected to backend">
            <FiWifi />
          </span>
        ) : (
          <span className="text-red-500" title="Backend connection error">
            <FiWifiOff />
          </span>
        )}
      </div>
    );
  }

  return (
    <div className={`p-4 rounded-lg shadow-sm ${className} ${
      isConnected === null ? 'bg-gray-100' : 
      isConnected ? 'bg-green-50' : 'bg-red-50'
    }`}>
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium">Backend Connectivity</h3>
        <button 
          onClick={checkConnectivity}
          disabled={isChecking}
          className="p-2 rounded-full hover:bg-gray-200 disabled:opacity-50"
        >
          <FiRefreshCw className={`${isChecking ? 'animate-spin' : ''}`} />
        </button>
      </div>
      
      <div className="mt-2">
        <div className="flex items-center">
          <div className={`w-3 h-3 rounded-full mr-2 ${
            isConnected === null ? 'bg-gray-400' : 
            isConnected ? 'bg-green-500' : 'bg-red-500'
          }`}></div>
          <span>
            {isConnected === null ? 'Checking connection...' : 
             isConnected ? 'Connected to backend' : 'Connection error'}
          </span>
        </div>
        
        {lastChecked && (
          <div className="mt-1 text-xs text-gray-500">
            Last checked: {lastChecked.toLocaleTimeString()}
          </div>
        )}
        
        {!isConnected && retryCount > 0 && (
          <div className="mt-2 text-sm text-red-600">
            Failed connection attempts: {retryCount}
          </div>
        )}
        
        {isConnected && backendInfo && (
          <div className="mt-2 text-xs space-y-1">
            <div>Server version: {backendInfo.version || 'Unknown'}</div>
            <div>Uptime: {formatUptime(backendInfo.uptime)}</div>
            <div>Environment: {backendInfo.environment || 'Unknown'}</div>
          </div>
        )}
      </div>
    </div>
  );
};

// Helper function to format uptime in a human-readable way
const formatUptime = (seconds) => {
  if (!seconds && seconds !== 0) return 'Unknown';
  
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  
  if (days > 0) {
    return `${days}d ${hours}h ${minutes}m`;
  } else if (hours > 0) {
    return `${hours}h ${minutes}m ${remainingSeconds}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`;
  } else {
    return `${remainingSeconds}s`;
  }
};

export default ConnectivityChecker;
