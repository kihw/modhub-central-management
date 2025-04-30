import React, { useState, useEffect } from "react";
import {
  FaGamepad,
  FaMoon,
  FaMusic,
  FaPlus,
  FaCog,
  FaHistory,
  FaTachometerAlt,
  FaExclamationTriangle,
} from "react-icons/fa";
import { NavLink } from "react-router-dom";
import logo from "../../assets/modhub-logo.png";
import axios from "axios";

const Sidebar = (props) => {
  const { collapsed, setCollapsed = () => {} } = props;

  const [activeModCount, setActiveModCount] = useState(0);
  const [fetchError, setFetchError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Fetch active mods count from API with error handling
    const fetchActiveModsCount = async () => {
      try {
        // Utilisez le chemin relatif avec le préfixe /api
        const response = await axios.get("/api/mods/active/count", {
          timeout: 5000,
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
        });

        setActiveModCount(response.data.count);
        setFetchError(false);
      } catch (error) {
        console.error("Failed to fetch active mods count:", error);
        // Ajoutez plus de détails de débogage
        console.error("Full error details:", {
          message: error.message,
          response: error.response,
          request: error.request,
          config: error.config,
        });
        setFetchError(true);
        setActiveModCount(0);
      }
    };

    fetchActiveModsCount();

    // Set interval for periodic updates with cleanup
    const interval = setInterval(fetchActiveModsCount, 10000); // Update every 10 seconds

    // Cleanup interval on component unmount
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { path: "/", icon: <FaTachometerAlt />, label: "Dashboard" },
    { path: "/mods/gaming", icon: <FaGamepad />, label: "Gaming Mod" },
    { path: "/mods/night", icon: <FaMoon />, label: "Night Mod" },
    { path: "/mods/media", icon: <FaMusic />, label: "Media Mod" },
    { path: "/mods/custom", icon: <FaPlus />, label: "Custom Mods" },
    { path: "/settings", icon: <FaCog />, label: "Settings" },
    { path: "/history", icon: <FaHistory />, label: "Activity Log" },
  ];

  return (
    <div
      className={`bg-gray-900 text-white flex flex-col transition-all duration-500 ease-in-out ${
        collapsed ? "w-16" : "w-64"
      } h-screen fixed left-0 top-0 z-10 shadow-lg`}
    >
      <div className="flex items-center justify-between p-4">
        {!collapsed && (
          <div className="flex items-center">
            <img src={logo} alt="ModHub Logo" className="h-8 w-8 mr-2" />
            <span className="font-bold text-lg">ModHub Central</span>
          </div>
        )}
        {collapsed && (
          <img src={logo} alt="ModHub Logo" className="h-8 w-8 mx-auto" />
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="text-gray-400 hover:text-white"
        >
          {collapsed ? ">" : "<"}
        </button>
      </div>

      <div className="p-4 mb-2">
        <div
          className={`${
            fetchError ? "bg-red-800" : "bg-green-800"
          } rounded-lg p-2 ${
            collapsed ? "text-center" : "flex justify-between items-center"
          }`}
        >
          {collapsed ? (
            <div className="text-xs font-semibold">
              {fetchError ? (
                <FaExclamationTriangle className="mx-auto text-yellow-400" />
              ) : (
                activeModCount
              )}
            </div>
          ) : (
            <>
              <span className="text-sm">
                {fetchError ? "Connection Error" : "Active Mods"}
              </span>
              {fetchError ? (
                <span className="bg-red-700 px-2 py-1 rounded text-xs font-semibold text-yellow-400">
                  <FaExclamationTriangle className="inline mr-1" />
                  Error
                </span>
              ) : (
                <span className="bg-green-700 px-2 py-1 rounded text-xs font-semibold">
                  {isLoading ? "..." : activeModCount}
                </span>
              )}
            </>
          )}
        </div>
      </div>

      <nav className="flex-1">
        <ul className="space-y-2 px-2">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center p-2 rounded-lg hover:bg-gray-700 ${
                    isActive ? "bg-gray-700" : ""
                  } ${collapsed ? "justify-center" : ""}`
                }
              >
                <span className="text-lg">{item.icon}</span>
                {!collapsed && <span className="ml-3">{item.label}</span>}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className="p-4">
        <div
          className={`text-gray-400 text-xs ${collapsed ? "text-center" : ""}`}
        >
          {!collapsed && <p>ModHub Central v0.1.0</p>}
          {collapsed && <p>v0.1.0</p>}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
