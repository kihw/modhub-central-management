import React, { useState, useEffect } from "react";
import {
  FaGamepad,
  FaMoon,
  FaMusic,
  FaPlus,
  FaCog,
  FaHistory,
  FaTachometerAlt,
} from "react-icons/fa";
import { NavLink } from "react-router-dom";
import logo from "../../assets/modhub-logo.png";

const Sidebar = ({ collapsed, setCollapsed }) => {
  const [activeModCount, setActiveModCount] = useState(0);

  useEffect(() => {
    // Fetch active mods count from API
    const fetchActiveModsCount = async () => {
      try {
        const response = await fetch(
          "http://localhost:8000/api/mods/active/count"
        );
        const data = await response.json();
        setActiveModCount(data.count);
      } catch (error) {
        console.error("Failed to fetch active mods count:", error);
      }
    };

    fetchActiveModsCount();
    const interval = setInterval(fetchActiveModsCount, 10000); // Update every 10 seconds

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
      className={`bg-gray-900 text-white flex flex-col transition-all duration-300 ${
        collapsed ? "w-16" : "w-64"
      } h-screen fixed left-0 top-0 z-10`}
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
          className={`bg-green-800 rounded-lg p-2 ${
            collapsed ? "text-center" : "flex justify-between items-center"
          }`}
        >
          {collapsed ? (
            <div className="text-xs font-semibold">{activeModCount}</div>
          ) : (
            <>
              <span className="text-sm">Active Mods</span>
              <span className="bg-green-700 px-2 py-1 rounded text-xs font-semibold">
                {activeModCount}
              </span>
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
