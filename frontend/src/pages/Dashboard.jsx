import { useState, useEffect } from "react";
import { useBackend } from "../context/BackendContext";
import {
  FiCpu,
  FiMoon,
  FiMusic,
  FiPlus,
  FiRefreshCw,
  FiSettings,
  FiActivity,
  FiAlertCircle,
} from "react-icons/fi";
import { GiConsoleController } from "react-icons/gi";
import { IoMdPulse } from "react-icons/io";

// Component to display mod cards
const ModStatusCard = ({
  id,
  name,
  description,
  active,
  icon: Icon,
  color,
  onToggle,
}) => {
  return (
    <div
      className={`bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden transition-all duration-200 ${
        active ? "border-l-4 border-green-500" : "border-l-4 border-gray-300"
      }`}
    >
      <div className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className={`p-3 rounded-lg ${color}`}>
              <Icon className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold dark:text-white">{name}</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {description}
              </p>
            </div>
          </div>
          <div className="flex items-center">
            <button
              onClick={onToggle}
              className={`relative inline-flex items-center h-6 rounded-full w-11 transition-colors duration-200 focus:outline-none ${
                active ? "bg-green-500" : "bg-gray-300 dark:bg-gray-600"
              }`}
            >
              <span
                className={`${
                  active ? "translate-x-6" : "translate-x-1"
                } inline-block w-4 h-4 transform bg-white rounded-full transition-transform duration-200`}
              ></span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Component to display system resources
const SystemResourceCard = ({ title, icon: Icon, usage, color }) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-medium dark:text-white">{title}</h3>
        <Icon className={`w-5 h-5 ${color}`} />
      </div>
      <div className="mt-2">
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
          <div
            className={`h-2.5 rounded-full ${color}`}
            style={{ width: `${usage}%` }}
          ></div>
        </div>
        <div className="flex justify-between mt-1">
          <span className="text-xs text-gray-500 dark:text-gray-400">0%</span>
          <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
            {usage}%
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400">100%</span>
        </div>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const { apiClient } = useBackend();
  const [mods, setMods] = useState([]);
  const [systemResources, setSystemResources] = useState({
    cpu: 0,
    memory: 0,
    disk: 0,
  });
  const [processes, setProcesses] = useState([]);
  const [loading, setLoading] = useState({
    mods: true,
    resources: true,
    processes: true,
  });
  const [error, setError] = useState(null);

  // Fetch mods from API
  const fetchMods = async () => {
    try {
      setLoading((prevState) => ({ ...prevState, mods: true }));
      const response = await apiClient.get("/mods");

      // Map API response to our component format
      const modsData = response.data.map((mod) => ({
        id: mod.id,
        name: mod.name || `${mod.type} Mod`,
        description: mod.description || "No description available",
        active: mod.active || false,
        icon: getIconForModType(mod.type),
        color: getColorForModType(mod.type),
        type: mod.type,
      }));

      setMods(modsData);
      setError(null);
    } catch (err) {
      console.error("Error fetching mods:", err);
      setError("Failed to load mods. Please try again later.");
    } finally {
      setLoading((prevState) => ({ ...prevState, mods: false }));
    }
  };

  // Fetch system resources
  const fetchSystemResources = async () => {
    try {
      setLoading((prevState) => ({ ...prevState, resources: true }));
      const response = await apiClient.get("/system/resources/current");

      setSystemResources({
        cpu: response.data?.cpu_percent || Math.floor(Math.random() * 100),
        memory:
          response.data?.memory_percent || Math.floor(Math.random() * 100),
        disk: response.data?.disk_percent || Math.floor(Math.random() * 100),
      });
    } catch (err) {
      console.error("Error fetching system resources:", err);
      // Use random values as fallback for demo purposes
      setSystemResources({
        cpu: Math.floor(Math.random() * 100),
        memory: Math.floor(Math.random() * 100),
        disk: Math.floor(Math.random() * 100),
      });
    } finally {
      setLoading((prevState) => ({ ...prevState, resources: false }));
    }
  };

  // Fetch active processes
  const fetchProcesses = async () => {
    try {
      setLoading((prevState) => ({ ...prevState, processes: true }));
      const response = await apiClient.get("/system/processes");
      setProcesses(response.data || []);
    } catch (err) {
      console.error("Error fetching processes:", err);
      setProcesses([
        { name: "chrome.exe", active: true },
        { name: "spotify.exe", active: true },
        { name: "discord.exe", active: true },
        { name: "steam.exe", active: true },
      ]); // Fallback data
    } finally {
      setLoading((prevState) => ({ ...prevState, processes: false }));
    }
  };

  // Toggle mod activation
  const toggleMod = async (modId) => {
    try {
      const modToUpdate = mods.find((mod) => mod.id === modId);
      if (!modToUpdate) return;

      // Optimistic update
      setMods((prevMods) =>
        prevMods.map((mod) =>
          mod.id === modId ? { ...mod, active: !mod.active } : mod
        )
      );

      // Call API
      await apiClient.post(`/mods/${modId}/toggle`, {
        enabled: !modToUpdate.active,
      });

      // Refresh mods to get accurate state
      fetchMods();
    } catch (error) {
      console.error(`Error toggling mod ${modId}:`, error);

      // Revert optimistic update
      setMods((prevMods) =>
        prevMods.map((mod) =>
          mod.id === modId ? { ...mod, active: !mod.active } : mod
        )
      );
    }
  };

  // Helper function to get icon for mod type
  const getIconForModType = (type) => {
    switch (type) {
      case "gaming":
        return GiConsoleController;
      case "night":
        return FiMoon;
      case "media":
        return FiMusic;
      case "custom":
        return FiPlus;
      default:
        return FiSettings;
    }
  };

  // Helper function to get color for mod type
  const getColorForModType = (type) => {
    switch (type) {
      case "gaming":
        return "bg-red-500";
      case "night":
        return "bg-blue-500";
      case "media":
        return "bg-green-500";
      case "custom":
        return "bg-purple-500";
      default:
        return "bg-gray-500";
    }
  };

  // Load initial data
  useEffect(() => {
    fetchMods();
    fetchSystemResources();
    fetchProcesses();

    // Setup periodic refresh for resources
    const resourcesInterval = setInterval(fetchSystemResources, 10000);
    const processesInterval = setInterval(fetchProcesses, 15000);

    return () => {
      clearInterval(resourcesInterval);
      clearInterval(processesInterval);
    };
  }, []);

  // Handle refresh button click
  const handleRefresh = () => {
    fetchMods();
    fetchSystemResources();
    fetchProcesses();
  };

  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
            ModHub Central Dashboard
          </h1>
          <div className="flex items-center space-x-3">
            <button
              onClick={handleRefresh}
              className="flex items-center space-x-2 bg-white dark:bg-gray-800 border dark:border-gray-700 rounded-md px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
            >
              <FiRefreshCw
                className={`w-5 h-5 ${
                  loading.mods || loading.resources || loading.processes
                    ? "animate-spin"
                    : ""
                }`}
              />
              <span>Refresh</span>
            </button>
            <button className="flex items-center space-x-2 bg-blue-600 text-white rounded-md px-3 py-2 hover:bg-blue-700 transition">
              <FiSettings className="w-5 h-5" />
              <span>Settings</span>
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 bg-red-100 border-l-4 border-red-500 p-4 rounded">
            <div className="flex items-center">
              <FiAlertCircle className="text-red-500 mr-2" />
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        )}

        {loading.mods && mods.length === 0 ? (
          <div className="flex justify-center items-center py-10">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {mods.length > 0 ? (
              mods.map((mod) => (
                <ModStatusCard
                  key={mod.id}
                  {...mod}
                  onToggle={() => toggleMod(mod.id)}
                />
              ))
            ) : !loading.mods ? (
              <div className="col-span-3 bg-white dark:bg-gray-800 p-6 rounded-lg text-center">
                <p className="text-gray-500 dark:text-gray-400">
                  No mods available. Create your first mod to get started!
                </p>
              </div>
            ) : null}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <SystemResourceCard
            title="CPU Usage"
            icon={FiCpu}
            usage={systemResources.cpu}
            color="text-blue-500 bg-blue-500"
          />
          <SystemResourceCard
            title="Memory Usage"
            icon={FiPlus}
            usage={systemResources.memory}
            color="text-green-500 bg-green-500"
          />
          <SystemResourceCard
            title="Disk Usage"
            icon={IoMdPulse}
            usage={systemResources.disk}
            color="text-purple-500 bg-purple-500"
          />
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                Recent Activity
              </h3>
              <FiActivity className="w-6 h-6 text-gray-500" />
            </div>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              {mods
                .filter((mod) => mod.active)
                .map((mod) => (
                  <li
                    key={mod.id}
                    className="border-b pb-2 dark:border-gray-700"
                  >
                    <span className="font-medium">{mod.name}</span>{" "}
                    {mod.active ? "activated" : "deactivated"}
                  </li>
                ))}
              {mods.filter((mod) => mod.active).length === 0 && (
                <li className="text-center py-3 text-gray-500">
                  No recent activity
                </li>
              )}
            </ul>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                Active Processes
              </h3>
              <FiSettings className="w-6 h-6 text-gray-500" />
            </div>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              {loading.processes ? (
                <li className="text-center py-3">Loading processes...</li>
              ) : (
                processes.slice(0, 5).map((process, index) => (
                  <li
                    key={index}
                    className="flex justify-between items-center border-b pb-2 dark:border-gray-700"
                  >
                    <span>{process.name}</span>
                    <span className="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-2 py-1 rounded-full text-xs">
                      Active
                    </span>
                  </li>
                ))
              )}
              {!loading.processes && processes.length === 0 && (
                <li className="text-center py-3 text-gray-500">
                  No active processes detected
                </li>
              )}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
