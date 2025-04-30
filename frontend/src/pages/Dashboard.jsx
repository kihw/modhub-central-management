import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  FiCpu,
  FiMoon,
  FiMusic,
  FiPlus,
  FiRefreshCw,
  FiSettings,
  FiActivity,
} from "react-icons/fi";
import { GiConsoleController } from "react-icons/gi";
import { IoMdPulse } from "react-icons/io";

const Dashboard = () => {
  const [mods, setMods] = useState([]);
  const [systemResources, setSystemResources] = useState({
    cpu: 0,
    memory: 0,
    disk: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fonction pour récupérer les mods depuis l'API
  const fetchMods = async () => {
    try {
      setLoading(true);
      const response = await axios.get("/api/mods");

      // Mappage des données de l'API au format attendu par l'interface
      const modsData = response.data.map((mod) => ({
        id: mod.id,
        name: mod.name,
        description: mod.description,
        active: mod.active || false,
        icon: getIconForModType(mod.type),
        color: getColorForModType(mod.type),
      }));

      setMods(modsData);
      setError(null);
    } catch (err) {
      console.error("Erreur lors du chargement des mods:", err);
      setError("Impossible de charger les mods. Veuillez réessayer plus tard.");
    } finally {
      setLoading(false);
    }
  };

  // Fonction pour récupérer les ressources système depuis l'API
  const fetchSystemResources = async () => {
    try {
      const response = await axios.get("/api/system/resources/current");
      setSystemResources({
        cpu: response.data.cpu_percent || 0,
        memory: response.data.memory_usage || 0,
        disk: response.data.disk_usage || 0,
      });
    } catch (err) {
      console.error("Erreur lors du chargement des ressources système:", err);
    }
  };

  // Fonction utilitaire pour obtenir l'icône correspondant au type de mod
  const getIconForModType = (type) => {
    switch (type) {
      case "gaming":
        return GiConsoleController;
      case "night":
        return FiMoon;
      case "media":
        return FiMusic;
      default:
        return FiPlus;
    }
  };

  // Fonction utilitaire pour obtenir la couleur correspondant au type de mod
  const getColorForModType = (type) => {
    switch (type) {
      case "gaming":
        return "text-red-500";
      case "night":
        return "text-blue-500";
      case "media":
        return "text-green-500";
      default:
        return "text-purple-500";
    }
  };

  // Chargement initial des données
  useEffect(() => {
    fetchMods();
    fetchSystemResources();

    // Actualisation périodique des ressources système
    const intervalId = setInterval(fetchSystemResources, 5000);

    return () => clearInterval(intervalId);
  }, []);

  // Fonction pour basculer l'activation d'un mod
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

      // Call API to update mod status
      await axios.post(`/api/mods/${modId}/toggle`, {
        enabled: !modToUpdate.active,
      });

      // Refresh mods to get accurate state
      fetchMods();
    } catch (error) {
      console.error(`Erreur lors du basculement du mod ${modId}:`, error);

      // Revert optimistic update on error
      setMods((prevMods) =>
        prevMods.map((mod) =>
          mod.id === modId ? { ...mod, active: !mod.active } : mod
        )
      );

      // Show error to user (could use a toast notification here)
    }
  };

  const refreshSystemResources = () => {
    // In a real app, this would call an API to get current system resources
    setSystemResources({
      cpu: Math.floor(Math.random() * 70 + 30),
      memory: Math.floor(Math.random() * 70 + 30),
      disk: Math.floor(Math.random() * 70 + 30),
    });
  };

  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-200">
            ModHub Central Dashboard
          </h1>
          <div className="flex items-center space-x-3">
            <button
              onClick={refreshSystemResources}
              className="flex items-center space-x-2 bg-white dark:bg-gray-800 border dark:border-gray-700 rounded-md px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
            >
              <FiRefreshCw className="w-5 h-5" />
              <span>Actualiser</span>
            </button>
            <button className="flex items-center space-x-2 bg-blue-600 text-white rounded-md px-3 py-2 hover:bg-blue-700 transition">
              <FiSettings className="w-5 h-5" />
              <span>Paramètres</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {mods.map((mod) => (
            <ModStatusCard
              key={mod.id}
              {...mod}
              onToggle={() => toggleMod(mod.id)}
            />
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <SystemResourceCard
            title="CPU"
            icon={FiCpu}
            usage={systemResources.cpu}
            color="text-blue-500 bg-blue-500"
          />
          <SystemResourceCard
            title="Mémoire"
            icon={FiPlus}
            usage={systemResources.memory}
            color="text-green-500 bg-green-500"
          />
          <SystemResourceCard
            title="Disque"
            icon={IoMdPulse}
            usage={systemResources.disk}
            color="text-purple-500 bg-purple-500"
          />
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                Activité récente
              </h3>
              <FiActivity className="w-6 h-6 text-gray-500" />
            </div>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li className="border-b pb-2 dark:border-gray-700">
                <span className="font-medium">Gaming Mod</span> activé
                automatiquement
              </li>
              <li className="border-b pb-2 dark:border-gray-700">
                <span className="font-medium">Night Mod</span> programmé pour
                22h
              </li>
              <li>
                <span className="font-medium">Processus</span> CS:GO détecté
              </li>
            </ul>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                Processus Actifs
              </h3>
              <FiSettings className="w-6 h-6 text-gray-500" />
            </div>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              {["chrome.exe", "spotify.exe", "discord.exe", "steam.exe"].map(
                (process) => (
                  <li
                    key={process}
                    className="flex justify-between items-center border-b pb-2 dark:border-gray-700"
                  >
                    <span>{process}</span>
                    <span className="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-2 py-1 rounded-full text-xs">
                      Actif
                    </span>
                  </li>
                )
              )}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
