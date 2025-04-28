import React, { useState, useEffect } from "react";
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

// Mod status card component
const ModStatusCard = ({
  name,
  icon: Icon,
  color,
  active,
  description,
  onToggle,
}) => (
  <div
    className={`bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 relative overflow-hidden ${
      active ? "border-l-4 border-l-green-500" : "border-l-4 border-l-gray-300"
    }`}
  >
    <div className="flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className={`p-2 rounded-full ${color} bg-opacity-20`}>
          <Icon className={`w-6 h-6 ${color}`} />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            {name}
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {description}
          </p>
        </div>
      </div>
      <label className="flex items-center cursor-pointer">
        <div className="relative">
          <input
            type="checkbox"
            className="sr-only"
            checked={active}
            onChange={onToggle}
          />
          <div
            className={`w-10 h-4 ${
              active ? "bg-green-400" : "bg-gray-400"
            } rounded-full shadow-inner`}
          ></div>
          <div
            className={`
            dot absolute -left-1 -top-1 bg-white w-6 h-6 rounded-full shadow 
            transition transform ${active ? "translate-x-full" : ""}
          `}
          ></div>
        </div>
      </label>
    </div>
    <div className={`absolute bottom-0 left-0 h-1 ${color} w-full`}></div>
  </div>
);

// System Resource Card
const SystemResourceCard = ({ title, icon: Icon, usage, color }) => (
  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 flex flex-col">
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center space-x-3">
        <div className={`p-2 rounded-full ${color} bg-opacity-20`}>
          <Icon className={`w-6 h-6 ${color}`} />
        </div>
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
          {title}
        </h3>
      </div>
      <span className="text-xl font-bold text-gray-800 dark:text-gray-200">
        {usage}%
      </span>
    </div>
    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
      <div
        className={`${color} h-2.5 rounded-full`}
        style={{ width: `${usage}%` }}
      ></div>
    </div>
  </div>
);

const Dashboard = () => {
  const [mods, setMods] = useState([
    {
      id: "gaming",
      name: "Gaming Mod",
      icon: GiConsoleController,
      color: "text-red-500",
      active: false,
      description: "Optimise les paramètres pour le gaming",
    },
    {
      id: "night",
      name: "Night Mod",
      icon: FiMoon,
      color: "text-blue-500",
      active: false,
      description: "Mode nuit avec luminosité réduite",
    },
    {
      id: "media",
      name: "Media Mod",
      icon: FiMusic,
      color: "text-green-500",
      active: false,
      description: "Optimisation audio et vidéo",
    },
  ]);

  const [systemResources, setSystemResources] = useState({
    cpu: 35,
    memory: 62,
    disk: 45,
  });

  const toggleMod = (modId) => {
    setMods((prevMods) =>
      prevMods.map((mod) =>
        mod.id === modId ? { ...mod, active: !mod.active } : mod
      )
    );
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
