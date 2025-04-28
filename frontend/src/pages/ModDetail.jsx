import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  FaArrowLeft,
  FaToggleOn,
  FaToggleOff,
  FaCog,
  FaList,
  FaHistory,
  FaSave,
  FaTrash,
} from "react-icons/fa";

const ModDetail = () => {
  const { modId } = useParams();
  const navigate = useNavigate();
  const [mod, setMod] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("settings");

  useEffect(() => {
    // Fonction pour charger les détails du mod
    const fetchModDetails = async () => {
      try {
        setLoading(true);
        // Dans une implémentation réelle, vous feriez un appel API
        // const response = await fetch(`/api/mods/${modId}`);
        // const data = await response.json();

        // Pour l'instant, utilisons des données factices
        setTimeout(() => {
          // Simuler un délai de chargement
          const mockMod = {
            id: modId,
            name:
              modId === "gaming"
                ? "Gaming Mod"
                : modId === "night"
                ? "Night Mod"
                : modId === "media"
                ? "Media Mod"
                : "Custom Mod",
            description: "Description détaillée du mod...",
            active: false,
            priority: 5,
            settings: {
              enabled: true,
              autoStart: true,
              notifications: true,
            },
            processes: [
              { name: "game1.exe", active: true },
              { name: "game2.exe", active: false },
            ],
            logs: [
              {
                timestamp: "2023-05-15T10:30:00",
                action: "Mod activé",
                details: "Activation manuelle",
              },
              {
                timestamp: "2023-05-15T11:45:00",
                action: "Mod désactivé",
                details: "Désactivation automatique",
              },
            ],
          };

          setMod(mockMod);
          setLoading(false);
        }, 500);
      } catch (err) {
        setError(
          "Impossible de charger les détails du mod. Veuillez réessayer plus tard."
        );
        setLoading(false);
        console.error("Erreur lors du chargement du mod:", err);
      }
    };

    fetchModDetails();
  }, [modId]);

  const handleToggleMod = () => {
    if (mod) {
      setMod({ ...mod, active: !mod.active });
    }
  };

  const handleBack = () => {
    navigate("/mods");
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error || !mod) {
    return (
      <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded shadow-md">
        <p className="font-bold">Erreur</p>
        <p>{error || "Mod non trouvé"}</p>
        <button
          onClick={handleBack}
          className="mt-4 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
        >
          Retour
        </button>
      </div>
    );
  }

  return (
    <div className="p-6">
      <button
        onClick={handleBack}
        className="flex items-center mb-6 text-gray-600 hover:text-gray-800"
      >
        <FaArrowLeft className="mr-2" /> Retour à la liste des mods
      </button>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="bg-blue-600 p-4 flex justify-between items-center">
          <h1 className="text-white text-xl font-bold">{mod.name}</h1>
          <button onClick={handleToggleMod} className="text-white text-2xl">
            {mod.active ? <FaToggleOn /> : <FaToggleOff />}
          </button>
        </div>

        <div className="p-4">
          <p className="text-gray-600 mb-6">{mod.description}</p>

          <div className="flex border-b mb-4">
            <button
              className={`pb-2 px-4 font-medium ${
                activeTab === "settings"
                  ? "text-blue-600 border-b-2 border-blue-600"
                  : "text-gray-500"
              }`}
              onClick={() => setActiveTab("settings")}
            >
              <FaCog className="inline mr-2" /> Paramètres
            </button>
            <button
              className={`pb-2 px-4 font-medium ${
                activeTab === "processes"
                  ? "text-blue-600 border-b-2 border-blue-600"
                  : "text-gray-500"
              }`}
              onClick={() => setActiveTab("processes")}
            >
              <FaList className="inline mr-2" /> Processus
            </button>
            <button
              className={`pb-2 px-4 font-medium ${
                activeTab === "logs"
                  ? "text-blue-600 border-b-2 border-blue-600"
                  : "text-gray-500"
              }`}
              onClick={() => setActiveTab("logs")}
            >
              <FaHistory className="inline mr-2" /> Historique
            </button>
          </div>

          {activeTab === "settings" && (
            <div>
              <h2 className="text-lg font-semibold mb-4">Configuration</h2>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-700">Priorité</span>
                  <div className="w-64">
                    <input
                      type="range"
                      min="1"
                      max="10"
                      value={mod.priority}
                      className="w-full"
                      onChange={(e) =>
                        setMod({ ...mod, priority: parseInt(e.target.value) })
                      }
                    />
                    <div className="flex justify-between">
                      <span className="text-xs text-gray-500">Faible</span>
                      <span className="text-xs text-gray-500">Élevée</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-gray-700">Démarrage automatique</span>
                  <label className="switch">
                    <input
                      type="checkbox"
                      checked={mod.settings.autoStart}
                      onChange={(e) =>
                        setMod({
                          ...mod,
                          settings: {
                            ...mod.settings,
                            autoStart: e.target.checked,
                          },
                        })
                      }
                    />
                    <span className="slider round"></span>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-gray-700">Notifications</span>
                  <label className="switch">
                    <input
                      type="checkbox"
                      checked={mod.settings.notifications}
                      onChange={(e) =>
                        setMod({
                          ...mod,
                          settings: {
                            ...mod.settings,
                            notifications: e.target.checked,
                          },
                        })
                      }
                    />
                    <span className="slider round"></span>
                  </label>
                </div>
              </div>

              <div className="flex justify-end mt-6">
                <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center">
                  <FaSave className="mr-2" /> Sauvegarder
                </button>
              </div>
            </div>
          )}

          {activeTab === "processes" && (
            <div>
              <h2 className="text-lg font-semibold mb-4">
                Processus surveillés
              </h2>

              <table className="min-w-full border-collapse">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="px-4 py-2 text-left">Nom du processus</th>
                    <th className="px-4 py-2 text-left">État</th>
                    <th className="px-4 py-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {mod.processes.map((process, index) => (
                    <tr key={index} className="border-t">
                      <td className="px-4 py-2">{process.name}</td>
                      <td className="px-4 py-2">
                        <span
                          className={`px-2 py-1 rounded text-xs ${
                            process.active
                              ? "bg-green-100 text-green-800"
                              : "bg-gray-100 text-gray-800"
                          }`}
                        >
                          {process.active ? "Actif" : "Inactif"}
                        </span>
                      </td>
                      <td className="px-4 py-2">
                        <button className="text-red-600 hover:text-red-800">
                          <FaTrash />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <div className="flex items-center mt-4">
                <input
                  type="text"
                  placeholder="Ajouter un processus..."
                  className="flex-1 border rounded px-3 py-2"
                />
                <button className="ml-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                  Ajouter
                </button>
              </div>
            </div>
          )}

          {activeTab === "logs" && (
            <div>
              <h2 className="text-lg font-semibold mb-4">
                Historique d'activité
              </h2>

              <div className="overflow-auto max-h-96">
                {mod.logs.map((log, index) => {
                  const date = new Date(log.timestamp);
                  const formattedDate = date.toLocaleDateString();
                  const formattedTime = date.toLocaleTimeString();

                  return (
                    <div key={index} className="mb-3 pb-3 border-b">
                      <div className="flex justify-between items-start">
                        <span className="font-medium">{log.action}</span>
                        <span className="text-xs text-gray-500">
                          {formattedDate} {formattedTime}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {log.details}
                      </p>
                    </div>
                  );
                })}
              </div>

              {mod.logs.length === 0 && (
                <p className="text-gray-500 italic">
                  Aucun historique disponible
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ModDetail;
