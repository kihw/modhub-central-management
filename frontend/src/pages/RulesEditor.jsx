import React, { useState, useEffect } from "react";
import {
  FaPlus,
  FaEdit,
  FaTrash,
  FaToggleOn,
  FaToggleOff,
  FaArrowUp,
  FaArrowDown,
} from "react-icons/fa";

const RulesEditor = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingRule, setEditingRule] = useState(null);

  useEffect(() => {
    // Fonction pour charger les règles
    const fetchRules = async () => {
      try {
        setLoading(true);
        // Dans une implémentation réelle, vous feriez un appel API
        // const response = await fetch('/api/rules');
        // const data = await response.json();

        // Pour l'instant, utilisons des données factices
        setTimeout(() => {
          const mockRules = [
            {
              id: 1,
              name: "Activer Gaming Mod pour les jeux",
              description: "Active Gaming Mod quand un jeu est détecté",
              active: true,
              priority: 10,
              conditions: [
                { type: "process", operation: "running", value: "game.exe" },
              ],
              actions: [{ type: "mod", action: "activate", target: "gaming" }],
            },
            {
              id: 2,
              name: "Mode Nuit automatique",
              description: "Active Night Mod après 22h",
              active: true,
              priority: 5,
              conditions: [
                { type: "time", operation: "after", value: "22:00" },
              ],
              actions: [{ type: "mod", action: "activate", target: "night" }],
            },
            {
              id: 3,
              name: "Mode Média pour applications multimédias",
              description:
                "Active Media Mod lorsque des applications multimédias sont utilisées",
              active: false,
              priority: 7,
              conditions: [
                { type: "process", operation: "running", value: "vlc.exe" },
                { type: "process", operation: "running", value: "spotify.exe" },
              ],
              actions: [{ type: "mod", action: "activate", target: "media" }],
            },
          ];

          setRules(mockRules);
          setLoading(false);
        }, 500);
      } catch (err) {
        setError(
          "Impossible de charger les règles. Veuillez réessayer plus tard."
        );
        setLoading(false);
        console.error("Erreur lors du chargement des règles:", err);
      }
    };

    fetchRules();
  }, []);

  const handleToggleRule = (ruleId) => {
    setRules((prevRules) =>
      prevRules.map((rule) =>
        rule.id === ruleId ? { ...rule, active: !rule.active } : rule
      )
    );
  };

  const handleDeleteRule = (ruleId) => {
    if (window.confirm("Êtes-vous sûr de vouloir supprimer cette règle ?")) {
      setRules((prevRules) => prevRules.filter((rule) => rule.id !== ruleId));
    }
  };

  const handleEditRule = (rule) => {
    setEditingRule(rule);
    setShowAddModal(true);
  };

  const handleMovePriority = (ruleId, direction) => {
    setRules((prevRules) => {
      const newRules = [...prevRules];
      const index = newRules.findIndex((rule) => rule.id === ruleId);

      if (direction === "up" && index > 0) {
        // Échange avec la règle précédente
        const temp = newRules[index];
        newRules[index] = newRules[index - 1];
        newRules[index - 1] = temp;
      } else if (direction === "down" && index < newRules.length - 1) {
        // Échange avec la règle suivante
        const temp = newRules[index];
        newRules[index] = newRules[index + 1];
        newRules[index + 1] = temp;
      }

      return newRules;
    });
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
        <h1 className="text-2xl font-bold">Éditeur de Règles</h1>
        <button
          onClick={() => {
            setEditingRule(null);
            setShowAddModal(true);
          }}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          <FaPlus className="mr-2" /> Nouvelle règle
        </button>
      </div>

      {rules.length === 0 ? (
        <div className="bg-gray-100 p-6 text-center rounded-lg">
          <p className="text-gray-500">
            Aucune règle d'automatisation définie.
          </p>
          <p className="text-gray-500 mt-2">
            Cliquez sur "Nouvelle règle" pour commencer à automatiser vos mods.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {rules.map((rule) => (
            <div
              key={rule.id}
              className="bg-white rounded-lg shadow-md overflow-hidden"
            >
              <div className="p-4 flex flex-wrap justify-between items-center">
                <div className="flex-1 min-w-0 mr-4">
                  <h2 className="text-lg font-semibold truncate">
                    {rule.name}
                  </h2>
                  <p className="text-gray-500 text-sm mt-1">
                    {rule.description}
                  </p>

                  <div className="mt-2 flex flex-wrap gap-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      Priorité: {rule.priority}
                    </span>

                    {rule.conditions.map((condition, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
                      >
                        {condition.type === "process"
                          ? `Process: ${condition.value}`
                          : ""}
                        {condition.type === "time"
                          ? `Time: ${condition.operation} ${condition.value}`
                          : ""}
                      </span>
                    ))}

                    {rule.actions.map((action, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                      >
                        {`${action.action} ${action.target}`}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center space-x-2 mt-2 sm:mt-0">
                  <button
                    onClick={() => handleMovePriority(rule.id, "up")}
                    className="text-gray-500 hover:text-gray-700"
                    title="Augmenter la priorité"
                  >
                    <FaArrowUp />
                  </button>
                  <button
                    onClick={() => handleMovePriority(rule.id, "down")}
                    className="text-gray-500 hover:text-gray-700"
                    title="Diminuer la priorité"
                  >
                    <FaArrowDown />
                  </button>
                  <button
                    onClick={() => handleToggleRule(rule.id)}
                    className={
                      rule.active
                        ? "text-green-500 hover:text-green-700"
                        : "text-gray-400 hover:text-gray-600"
                    }
                    title={rule.active ? "Désactiver" : "Activer"}
                  >
                    {rule.active ? (
                      <FaToggleOn size={20} />
                    ) : (
                      <FaToggleOff size={20} />
                    )}
                  </button>
                  <button
                    onClick={() => handleEditRule(rule)}
                    className="text-blue-500 hover:text-blue-700"
                    title="Modifier"
                  >
                    <FaEdit />
                  </button>
                  <button
                    onClick={() => handleDeleteRule(rule.id)}
                    className="text-red-500 hover:text-red-700"
                    title="Supprimer"
                  >
                    <FaTrash />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Ici, vous devriez ajouter un modal pour ajouter/éditer des règles */}
      {/* Pour l'instant, ce code est simplifié et n'inclut pas l'implémentation du modal */}
    </div>
  );
};

export default RulesEditor;
