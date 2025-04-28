import React, { useState, useEffect, useRef } from "react";
import {
  FiRefreshCw,
  FiDownload,
  FiSearch,
  FiFilter,
  FiTrash2,
} from "react-icons/fi";
import { format } from "date-fns";
import axios from "axios";

const LOG_LEVELS = {
  DEBUG: { color: "text-gray-500", bgColor: "bg-gray-100" },
  INFO: { color: "text-blue-500", bgColor: "bg-blue-100" },
  WARNING: { color: "text-yellow-500", bgColor: "bg-yellow-100" },
  ERROR: { color: "text-red-500", bgColor: "bg-red-100" },
  CRITICAL: { color: "text-white", bgColor: "bg-red-600" },
};

const Logs = () => {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filters, setFilters] = useState({
    level: "ALL",
    module: "ALL",
    startDate: "",
    endDate: "",
  });
  const [availableModules, setAvailableModules] = useState([]);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const logEndRef = useRef(null);

  // Fetch logs from API
  const fetchLogs = async () => {
    try {
      setLoading(true);
      const response = await axios.get("http://localhost:8668/api/logs");
      setLogs(response.data);

      // Extract unique modules for filtering
      const modules = [...new Set(response.data.map((log) => log.module))];
      setAvailableModules(modules);

      setError(null);
    } catch (err) {
      setError("Failed to fetch logs: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchLogs();
  }, []);

  // Auto-refresh timer
  useEffect(() => {
    let refreshInterval;
    if (autoRefresh) {
      refreshInterval = setInterval(() => {
        fetchLogs();
      }, 5000); // Refresh every 5 seconds
    }

    return () => {
      if (refreshInterval) clearInterval(refreshInterval);
    };
  }, [autoRefresh]);

  // Apply filters and search
  useEffect(() => {
    let result = [...logs];

    // Apply level filter
    if (filters.level !== "ALL") {
      result = result.filter((log) => log.level === filters.level);
    }

    // Apply module filter
    if (filters.module !== "ALL") {
      result = result.filter((log) => log.module === filters.module);
    }

    // Apply date filters
    if (filters.startDate) {
      const startDate = new Date(filters.startDate);
      result = result.filter((log) => new Date(log.timestamp) >= startDate);
    }

    if (filters.endDate) {
      const endDate = new Date(filters.endDate);
      endDate.setHours(23, 59, 59, 999); // End of the day
      result = result.filter((log) => new Date(log.timestamp) <= endDate);
    }

    // Apply search term
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      result = result.filter(
        (log) =>
          log.message.toLowerCase().includes(term) ||
          log.module.toLowerCase().includes(term)
      );
    }

    setFilteredLogs(result);
  }, [logs, filters, searchTerm]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [filteredLogs]);

  // Handle filter changes
  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  // Export logs to CSV
  const exportLogsToCSV = () => {
    const csvContent = [
      ["Timestamp", "Level", "Module", "Message"].join(","),
      ...filteredLogs.map((log) =>
        [
          log.timestamp,
          log.level,
          log.module,
          `"${log.message.replace(/"/g, '""')}"`,
        ].join(",")
      ),
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute(
      "download",
      `modhub_logs_${format(new Date(), "yyyy-MM-dd_HH-mm")}.csv`
    );
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Clear logs
  const clearLogs = async () => {
    if (
      window.confirm(
        "Are you sure you want to clear all logs? This action cannot be undone."
      )
    ) {
      try {
        await axios.delete("http://localhost:8668/api/logs");
        setLogs([]);
        setFilteredLogs([]);
      } catch (err) {
        setError("Failed to clear logs: " + err.message);
      }
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    try {
      return format(new Date(timestamp), "yyyy-MM-dd HH:mm:ss");
    } catch (e) {
      return timestamp;
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="bg-white shadow rounded-lg p-4 mb-4">
        <div className="flex flex-col md:flex-row justify-between items-center mb-4">
          <h1 className="text-2xl font-semibold text-gray-800">System Logs</h1>
          <div className="flex space-x-2 mt-2 md:mt-0">
            <button
              onClick={fetchLogs}
              className="flex items-center px-3 py-2 bg-blue-50 text-blue-600 rounded hover:bg-blue-100"
            >
              <FiRefreshCw className="mr-1" /> Refresh
            </button>
            <button
              onClick={exportLogsToCSV}
              className="flex items-center px-3 py-2 bg-green-50 text-green-600 rounded hover:bg-green-100"
            >
              <FiDownload className="mr-1" /> Export
            </button>
            <button
              onClick={clearLogs}
              className="flex items-center px-3 py-2 bg-red-50 text-red-600 rounded hover:bg-red-100"
            >
              <FiTrash2 className="mr-1" /> Clear
            </button>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="autoRefresh"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="mr-2"
              />
              <label htmlFor="autoRefresh" className="text-sm text-gray-600">
                Auto-refresh
              </label>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <FiSearch className="text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search logs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full pl-10 p-2.5"
            />
          </div>

          <div>
            <select
              value={filters.level}
              onChange={(e) => handleFilterChange("level", e.target.value)}
              className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5"
            >
              <option value="ALL">All Levels</option>
              {Object.keys(LOG_LEVELS).map((level) => (
                <option key={level} value={level}>
                  {level}
                </option>
              ))}
            </select>
          </div>

          <div>
            <select
              value={filters.module}
              onChange={(e) => handleFilterChange("module", e.target.value)}
              className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5"
            >
              <option value="ALL">All Modules</option>
              {availableModules.map((module) => (
                <option key={module} value={module}>
                  {module}
                </option>
              ))}
            </select>
          </div>

          <div className="flex space-x-2">
            <input
              type="date"
              value={filters.startDate}
              onChange={(e) => handleFilterChange("startDate", e.target.value)}
              className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5"
            />
            <input
              type="date"
              value={filters.endDate}
              onChange={(e) => handleFilterChange("endDate", e.target.value)}
              className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5"
            />
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 text-red-700 p-4 rounded-lg mb-4">
          {error}
        </div>
      )}

      <div className="flex-1 bg-white shadow rounded-lg overflow-hidden">
        {loading && logs.length === 0 ? (
          <div className="flex justify-center items-center h-40">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="flex flex-col justify-center items-center h-40 text-gray-500">
            <FiFilter className="text-2xl mb-2" />
            <p>No logs found with the current filters</p>
          </div>
        ) : (
          <div className="overflow-auto h-full max-h-[calc(100vh-300px)]">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50 sticky top-0">
                <tr>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Timestamp
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Level
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Module
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    Message
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredLogs.map((log, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatTimestamp(log.timestamp)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          LOG_LEVELS[log.level]?.bgColor
                        } ${LOG_LEVELS[log.level]?.color}`}
                      >
                        {log.level}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {log.module}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 break-words max-w-md">
                      {log.message}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div ref={logEndRef} />
          </div>
        )}
      </div>

      <div className="mt-4 text-gray-500 text-sm">
        Showing {filteredLogs.length} of {logs.length} logs
        {autoRefresh && <span> • Auto-refreshing every 5 seconds</span>}
      </div>
    </div>
  );
};

export default Logs;
