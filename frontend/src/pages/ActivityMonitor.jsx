import React, { useState, useEffect } from "react";
import {
  FiRefreshCw,
  FiCpu,
  FiHardDrive,
  FiClock,
  FiActivity,
} from "react-icons/fi";

const ActivityMonitor = () => {
  const [systemData, setSystemData] = useState({
    processes: [],
    resources: {
      cpu: 0,
      memory: 0,
      disk: 0,
    },
    activeMods: [],
    activeTime: {
      gaming: 0,
      night: 0,
      media: 0,
    },
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(false);

  useEffect(() => {
    // Fonction pour charger les données d'activité
    const fetchActivityData = async () => {
      try {
        setLoading(true);
        // Dans une implémentation réelle, vous feriez un appel API
        // const response = await fetch('/api/system/activity');
        // const data = await response.json();

        // Pour l'instant, utilisons des données factices
        setTimeout(() => {
          const mockProcesses = [
            { name: "chrome.exe", cpu: 12.5, memory: 450, active: true },
            { name: "spotify.exe", cpu: 3.2, memory: 120, active: true },
            { name: "discord.exe", cpu: 2.1, memory: 180, active: true },
            { name: "explorer.exe", cpu: 0.5, memory: 85, active: true },
            { name: "modhub.exe", cpu: 1.8, memory: 65, active: true },
          ];

          const mockSystemData = {
            processes: mockProcesses,
            resources: {
              cpu: 22.3,
              memory: 42.8,
              disk: 5.2,
            },
            activeMods: ["night"],
            activeTime: {
              gaming: 120, // minutes
              night: 345,
              media: 78,
            },
          };

          setSystemData(mockSystemData);
          setLoading(false);
          setError(null);
        }, 500);
      } catch (err) {
        setError(
          "Impossible de charger les données d'activité. Veuillez réessayer plus tard."
        );
        setLoading(false);
        console.error("Erreur lors du chargement des données d'activité:", err);
      }
    };

    // Charger les données initiales
    fetchActivityData();

    // Configurer l'actualisation automatique si activée
    let intervalId;
    if (autoRefresh) {
      intervalId = setInterval(fetchActivityData, 5000); // toutes les 5 secondes
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [autoRefresh]);

  // Formater le temps en heures et minutes
  const formatTime = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  if (loading && !systemData.processes.length) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded shadow-md">
        <p className="font-bold">Erreur</p>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Moniteur d'Activité</h1>
        <div className="flex items-center">
          <div className="mr-4 flex items-center">
            <input
              type="checkbox"
              id="autoRefresh"
              checked={autoRefresh}
              onChange={() => setAutoRefresh(!autoRefresh)}
              className="mr-2"
            />
            <label htmlFor="autoRefresh" className="text-sm text-gray-600">
              Actualisation auto
            </label>
          </div>
          <button
            onClick={() => {
              setLoading(true);
              setTimeout(() => setLoading(false), 500);
            }}
            className="flex items-center px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
          >
            <FiRefreshCw className="mr-1" /> Actualiser
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {/* CPU Usage */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center mb-4">
            <FiCpu className="text-blue-500 mr-2" size={20} />
            <h2 className="text-lg font-semibold">Utilisation CPU</h2>
          </div>
          <div className="flex items-center justify-center">
            <div className="relative h-36 w-36">
              <svg className="h-full w-full" viewBox="0 0 36 36">
                <circle
                  cx="18"
                  cy="18"
                  r="16"
                  fill="none"
                  stroke="#e5e7eb"
                  strokeWidth="2"
                />
                <circle
                  cx="18"
                  cy="18"
                  r="16"
                  fill="none"
                  stroke="#3b82f6"
                  strokeWidth="2"
                  strokeDasharray={`${systemData.resources.cpu} 100`}
                  strokeLinecap="round"
                  transform="rotate(-90 18 18)"
                />
                <text
                  x="18"
                  y="18"
                  dominantBaseline="middle"
                  textAnchor="middle"
                  fontSize="0.7rem"
                  fontWeight="bold"
                  fill="#3b82f6"
                >
                  {systemData.resources.cpu}%
                </text>
              </svg>
            </div>
          </div>
        </div>

        {/* Memory Usage */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center mb-4">
            <FiHardDrive className="text-green-500 mr-2" size={20} />
            <h2 className="text-lg font-semibold">Utilisation Mémoire</h2>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4 mb-2">
            <div
              className="bg-green-500 h-4 rounded-full"
              style={{ width: `${systemData.resources.memory}%` }}
            ></div>
          </div>
          <div className="text-right text-sm text-gray-500">
            {systemData.resources.memory}% utilisé
          </div>
        </div>

        {/* Mods Active Time */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center mb-4">
            <FiClock className="text-purple-500 mr-2" size={20} />
            <h2 className="text-lg font-semibold">Temps d'Activité des Mods</h2>
          </div>
          <div className="space-y-2">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Gaming Mod</span>
                <span>{formatTime(systemData.activeTime.gaming)}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-red-500 h-2 rounded-full"
                  style={{
                    width: `${
                      (systemData.activeTime.gaming /
                        (systemData.activeTime.gaming +
                          systemData.activeTime.night +
                          systemData.activeTime.media)) *
                      100
                    }%`,
                  }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Night Mod</span>
                <span>{formatTime(systemData.activeTime.night)}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full"
                  style={{
                    width: `${
                      (systemData.activeTime.night /
                        (systemData.activeTime.gaming +
                          systemData.activeTime.night +
                          systemData.activeTime.media)) *
                      100
                    }%`,
                  }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Media Mod</span>
                <span>{formatTime(systemData.activeTime.media)}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{
                    width: `${
                      (systemData.activeTime.media /
                        (systemData.activeTime.gaming +
                          systemData.activeTime.night +
                          systemData.activeTime.media)) *
                      100
                    }%`,
                  }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="flex items-center p-4 border-b">
          <FiActivity className="text-blue-500 mr-2" size={20} />
          <h2 className="text-lg font-semibold">Processus Actifs</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Nom
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  CPU
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Mémoire (MB)
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  État
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {systemData.processes.map((process, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {process.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {process.cpu}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {process.memory} MB
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        process.active
                          ? "bg-green-100 text-green-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {process.active ? "Actif" : "Inactif"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ActivityMonitor;
