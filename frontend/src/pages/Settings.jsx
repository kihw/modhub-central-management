import React, { useState, useEffect } from "react";
import {
  FiSave,
  FiRefreshCw,
  FiHardDrive,
  FiCpu,
  FiThermometer,
  FiUserPlus,
  FiAlertCircle,
  FiMoon,
  FiSun,
  FiMonitor,
  FiDownload,
  FiUpload,
} from "react-icons/fi";
import { toast } from "react-toastify";

// Custom components
const SettingsToggle = ({
  label,
  description,
  checked,
  onChange,
  icon: Icon,
}) => (
  <div className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-all">
    <div className="flex items-center space-x-4">
      {Icon && <Icon className="w-6 h-6 text-blue-500" />}
      <div>
        <h3 className="text-lg font-medium text-gray-800 dark:text-gray-200">
          {label}
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
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
        />
        <div
          className={`w-10 h-4 ${
            checked ? "bg-blue-400" : "bg-gray-400"
          } rounded-full shadow-inner`}
        ></div>
        <div
          className={`
          dot absolute -left-1 -top-1 bg-white w-6 h-6 rounded-full shadow 
          transition transform ${checked ? "translate-x-full" : ""}
        `}
        ></div>
      </div>
    </label>
  </div>
);

const Settings = () => {
  const [settings, setSettings] = useState({
    // General Settings
    autoStartWithSystem: false,
    minimizeToTray: true,
    showNotifications: true,

    // Performance Settings
    performanceMode: "balanced",
    resourceMonitoring: true,

    // Theme Settings
    theme: "system",

    // Advanced Settings
    debugMode: false,
    scanInterval: 5000,

    // Resource Thresholds
    resourceWarningThresholds: {
      cpu: 85,
      memory: 80,
      temperature: 80,
    },
  });

  const [unsavedChanges, setUnsavedChanges] = useState(false);

  // Update settings and track changes
  const updateSetting = (key, value) => {
    setSettings((prev) => ({
      ...prev,
      [key]: value,
    }));
    setUnsavedChanges(true);
  };

  // Update nested settings
  const updateNestedSetting = (parentKey, childKey, value) => {
    setSettings((prev) => ({
      ...prev,
      [parentKey]: {
        ...prev[parentKey],
        [childKey]: value,
      },
    }));
    setUnsavedChanges(true);
  };

  // Save settings
  const saveSettings = () => {
    try {
      // In a real app, this would call an API to save settings
      localStorage.setItem("modhub-settings", JSON.stringify(settings));
      toast.success("Paramètres sauvegardés avec succès !", {
        position: "bottom-right",
        autoClose: 3000,
      });
      setUnsavedChanges(false);
    } catch (error) {
      toast.error("Erreur lors de la sauvegarde des paramètres", {
        position: "bottom-right",
        autoClose: 3000,
      });
    }
  };

  // Reset to default settings
  const resetToDefaults = () => {
    const defaultSettings = {
      autoStartWithSystem: false,
      minimizeToTray: true,
      showNotifications: true,
      performanceMode: "balanced",
      resourceMonitoring: true,
      theme: "system",
      debugMode: false,
      scanInterval: 5000,
      resourceWarningThresholds: {
        cpu: 85,
        memory: 80,
        temperature: 80,
      },
    };

    setSettings(defaultSettings);
    setUnsavedChanges(true);
    toast.info("Paramètres réinitialisés aux valeurs par défaut", {
      position: "bottom-right",
      autoClose: 3000,
    });
  };

  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-200">
            Paramètres de ModHub Central
          </h1>
          <div className="flex space-x-3">
            {unsavedChanges && (
              <button
                onClick={resetToDefaults}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition"
              >
                Réinitialiser
              </button>
            )}
            <button
              onClick={saveSettings}
              disabled={!unsavedChanges}
              className={`
                px-4 py-2 rounded-md transition flex items-center space-x-2
                ${
                  unsavedChanges
                    ? "bg-blue-600 text-white hover:bg-blue-700"
                    : "bg-gray-300 text-gray-500 cursor-not-allowed"
                }
              `}
            >
              <FiSave className="w-5 h-5" />
              <span>Enregistrer</span>
            </button>
          </div>
        </div>

        {/* General Settings */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">
            Paramètres Généraux
          </h2>
          <div className="space-y-4">
            <SettingsToggle
              label="Démarrage automatique"
              description="Lancez ModHub Central au démarrage du système"
              checked={settings.autoStartWithSystem}
              onChange={(value) => updateSetting("autoStartWithSystem", value)}
              icon={FiUserPlus}
            />
            <SettingsToggle
              label="Réduire dans la barre d'état système"
              description="Minimiser l'application plutôt que de la fermer"
              checked={settings.minimizeToTray}
              onChange={(value) => updateSetting("minimizeToTray", value)}
              icon={FiHardDrive}
            />
            <SettingsToggle
              label="Notifications"
              description="Afficher les notifications système"
              checked={settings.showNotifications}
              onChange={(value) => updateSetting("showNotifications", value)}
              icon={FiAlertCircle}
            />
          </div>
        </div>

        {/* Theme Settings */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">
            Apparence
          </h2>
          <div className="grid grid-cols-3 gap-4">
            {[
              {
                value: "system",
                label: "Système",
                icon: FiMonitor,
              },
              {
                value: "light",
                label: "Clair",
                icon: FiSun,
              },
              {
                value: "dark",
                label: "Sombre",
                icon: FiMoon,
              },
            ].map((themeOption) => (
              <div
                key={themeOption.value}
                onClick={() => updateSetting("theme", themeOption.value)}
                className={`
                  cursor-pointer p-4 rounded-lg flex flex-col items-center space-y-2
                  ${
                    settings.theme === themeOption.value
                      ? "bg-blue-100 dark:bg-blue-900 border-2 border-blue-500"
                      : "bg-gray-100 dark:bg-gray-700 border-2 border-transparent"
                  } hover:bg-blue-50 dark:hover:bg-blue-800 transition
                `}
              >
                <themeOption.icon
                  className={`w-8 h-8 ${
                    settings.theme === themeOption.value
                      ? "text-blue-600"
                      : "text-gray-500"
                  }`}
                />
                <span
                  className={`
                  text-sm font-medium 
                  ${
                    settings.theme === themeOption.value
                      ? "text-blue-600"
                      : "text-gray-600 dark:text-gray-300"
                  }
                `}
                >
                  {themeOption.label}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Performance Settings */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">
            Performance
          </h2>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="col-span-2">
                <label
                  htmlFor="performanceMode"
                  className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                >
                  Mode Performance
                </label>
                <select
                  id="performanceMode"
                  value={settings.performanceMode}
                  onChange={(e) =>
                    updateSetting("performanceMode", e.target.value)
                  }
                  className="w-full border border-gray-300 dark:border-gray-700 rounded-md p-2 bg-white dark:bg-gray-700 dark:text-gray-200"
                >
                  <option value="power-saving">Économie d'énergie</option>
                  <option value="balanced">Équilibré</option>
                  <option value="performance">Performances</option>
                </select>
              </div>
              <div>
                <label
                  htmlFor="scanInterval"
                  className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                >
                  Intervalle de scan (ms)
                </label>
                <input
                  type="number"
                  id="scanInterval"
                  value={settings.scanInterval}
                  onChange={(e) =>
                    updateSetting("scanInterval", parseInt(e.target.value))
                  }
                  min="1000"
                  max="30000"
                  step="1000"
                  className="w-full border border-gray-300 dark:border-gray-700 rounded-md p-2 bg-white dark:bg-gray-700 dark:text-gray-200"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Seuil CPU
                </label>
                <input
                  type="range"
                  value={settings.resourceWarningThresholds.cpu}
                  onChange={(e) =>
                    updateNestedSetting(
                      "resourceWarningThresholds",
                      "cpu",
                      e.target.value
                    )
                  }
                  min="50"
                  max="95"
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>50%</span>
                  <span>{settings.resourceWarningThresholds.cpu}%</span>
                  <span>95%</span>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Seuil Mémoire
                </label>
                <input
                  type="range"
                  value={settings.resourceWarningThresholds.memory}
                  onChange={(e) =>
                    updateNestedSetting(
                      "resourceWarningThresholds",
                      "memory",
                      e.target.value
                    )
                  }
                  min="50"
                  max="95"
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>50%</span>
                  <span>{settings.resourceWarningThresholds.memory}%</span>
                  <span>95%</span>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Seuil Température
                </label>
                <input
                  type="range"
                  value={settings.resourceWarningThresholds.temperature}
                  onChange={(e) =>
                    updateNestedSetting(
                      "resourceWarningThresholds",
                      "temperature",
                      e.target.value
                    )
                  }
                  min="50"
                  max="95"
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>50°C</span>
                  <span>
                    {settings.resourceWarningThresholds.temperature}°C
                  </span>
                  <span>95°C</span>
                </div>
              </div>
            </div>

            <SettingsToggle
              label="Surveillance des ressources"
              description="Surveiller et alerter en cas de dépassement des seuils"
              checked={settings.resourceMonitoring}
              onChange={(value) => updateSetting("resourceMonitoring", value)}
              icon={FiCpu}
            />
          </div>
        </div>

        {/* Advanced Settings */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">
            Paramètres Avancés
          </h2>
          <SettingsToggle
            label="Mode Débogage"
            description="Active les journaux détaillés pour le dépannage"
            checked={settings.debugMode}
            onChange={(value) => updateSetting("debugMode", value)}
            icon={FiAlertCircle}
          />
        </div>

        {/* Diagnostic Information */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">
            Informations du Système
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
              <h3 className="text-md font-medium text-gray-700 dark:text-gray-300 mb-2">
                Version de l'Application
              </h3>
              <p className="text-gray-800 dark:text-gray-200">0.1.0</p>
            </div>
            <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
              <h3 className="text-md font-medium text-gray-700 dark:text-gray-300 mb-2">
                Système d'Exploitation
              </h3>
              <p className="text-gray-800 dark:text-gray-200">
                {/* In a real app, this would be dynamically detected */}
                Windows 10 Pro
              </p>
            </div>
            <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
              <h3 className="text-md font-medium text-gray-700 dark:text-gray-300 mb-2">
                Version du Backend
              </h3>
              <p className="text-gray-800 dark:text-gray-200">1.0.0</p>
            </div>
            <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
              <h3 className="text-md font-medium text-gray-700 dark:text-gray-300 mb-2">
                Architecture
              </h3>
              <p className="text-gray-800 dark:text-gray-200">x64</p>
            </div>
          </div>
        </div>

        {/* Export and Import Settings */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">
            Configuration
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
                Exporter la Configuration
              </h3>
              <button
                onClick={() => {
                  const configJson = JSON.stringify(settings, null, 2);
                  const blob = new Blob([configJson], {
                    type: "application/json",
                  });
                  const url = URL.createObjectURL(blob);
                  const link = document.createElement("a");
                  link.href = url;
                  link.download = `modhub-settings-${
                    new Date().toISOString().split("T")[0]
                  }.json`;
                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                  URL.revokeObjectURL(url);
                  toast.success("Configuration exportée avec succès", {
                    position: "bottom-right",
                    autoClose: 3000,
                  });
                }}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition flex items-center justify-center space-x-2"
              >
                <FiDownload className="w-5 h-5" />
                <span>Exporter</span>
              </button>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
                Importer la Configuration
              </h3>
              <input
                type="file"
                accept=".json"
                className="hidden"
                id="import-config"
                onChange={(e) => {
                  const file = e.target.files[0];
                  if (file) {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                      try {
                        const importedSettings = JSON.parse(
                          event.target.result
                        );
                        setSettings(importedSettings);
                        setUnsavedChanges(true);
                        toast.success("Configuration importée avec succès", {
                          position: "bottom-right",
                          autoClose: 3000,
                        });
                      } catch (error) {
                        toast.error(
                          "Erreur lors de l'importation de la configuration",
                          {
                            position: "bottom-right",
                            autoClose: 3000,
                          }
                        );
                      }
                    };
                    reader.readAsText(file);
                  }
                }}
              />
              <label
                htmlFor="import-config"
                className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition flex items-center justify-center space-x-2 cursor-pointer"
              >
                <FiUpload className="w-5 h-5" />
                <span>Importer</span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
