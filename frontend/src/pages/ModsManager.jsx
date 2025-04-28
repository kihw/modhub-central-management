import React, { useState, useEffect } from "react";
import {
  FaCogs,
  FaGamepad,
  FaMoon,
  FaMusic,
  FaPlus,
  FaTrash,
  FaPencilAlt,
  FaToggleOn,
  FaToggleOff,
} from "react-icons/fa";

const ModsManager = () => {
  const [mods, setMods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fonction pour charger les mods
    const fetchMods = async () => {
      try {
        setLoading(true);
        // Ici, vous feriez normalement un appel API
        // const response = await fetch('/api/mods');
        // const data = await response.json();

        // Pour l'instant, utilisons des données factices
        const mockData = [
          {
            id: "gaming",
            name: "Gaming Mod",
            description: "Optimise vos périphériques pour le gaming",
            active: false,
            icon: FaGamepad,
            color: "bg-red-600",
          },
          {
            id: "night",
            name: "Night Mod",
            description: "Ajuste la luminosité et active le mode nuit",
            active: false,
            icon: FaMoon,
            color: "bg-blue-800",
          },
          {
            id: "media",
            name: "Media Mod",
            description: "Optimise les paramètres audio et d'éclairage",
            active: false,
            icon: FaMusic,
            color: "bg-green-600",
          },
        ];

        setMods(mockData);
        setError(null);
      } catch (err) {
        setError(
          "Impossible de charger les mods. Veuillez réessayer plus tard."
        );
        console.error("Erreur lors du chargement des mods:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchMods();
  }, []);

  const toggleMod = (modId) => {
    setMods((prevMods) =>
      prevMods.map((mod) =>
        mod.id === modId ? { ...mod, active: !mod.active } : mod
      )
    );
  };

  if (loading) {
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
        <h1 className="text-2xl font-bold">Gestionnaire de Mods</h1>
        <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          <FaPlus className="mr-2" /> Ajouter un mod personnalisé
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mods.map((mod) => (
          <div
            key={mod.id}
            className="bg-white rounded-lg shadow-md overflow-hidden"
          >
            <div
              className={`${mod.color} p-4 flex justify-between items-center`}
            >
              <div className="flex items-center">
                <mod.icon className="text-white text-xl mr-2" />
                <h2 className="text-white text-lg font-semibold">{mod.name}</h2>
              </div>
              <button
                onClick={() => toggleMod(mod.id)}
                className="text-white text-xl"
              >
                {mod.active ? <FaToggleOn /> : <FaToggleOff />}
              </button>
            </div>
            <div className="p-4">
              <p className="text-gray-600 mb-4">{mod.description}</p>
              <div className="flex justify-end">
                <button className="p-2 text-blue-600 hover:text-blue-800">
                  <FaPencilAlt />
                </button>
                <button className="p-2 text-red-600 hover:text-red-800">
                  <FaTrash />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ModsManager;
