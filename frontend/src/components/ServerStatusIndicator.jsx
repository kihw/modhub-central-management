import React, { useState, useEffect } from "react";
import axios from "axios";
import { BsCircleFill } from "react-icons/bs";
import { Tooltip } from "@material-tailwind/react";

const ServerStatusIndicator = ({ className = "" }) => {
  const [status, setStatus] = useState("checking");
  const [latency, setLatency] = useState(null);
  const [tooltipContent, setTooltipContent] = useState(
    "Vérification de la connexion au serveur..."
  );

  useEffect(() => {
    const checkServerStatus = async () => {
      try {
        const startTime = Date.now();
        const response = await axios.get("http://localhost:8668/api/health", {
          timeout: 3000,
        });
        const endTime = Date.now();

        if (response.status === 200) {
          setStatus("online");
          setLatency(endTime - startTime);
          setTooltipContent(`Serveur connecté (${endTime - startTime}ms)`);
        } else {
          setStatus("error");
          setTooltipContent("Erreur de connexion au serveur");
        }
      } catch (error) {
        setStatus("offline");
        setTooltipContent("Serveur déconnecté");
      }
    };

    checkServerStatus();
    const interval = setInterval(checkServerStatus, 10000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    switch (status) {
      case "online":
        return "text-green-500";
      case "offline":
        return "text-red-500";
      case "error":
        return "text-amber-500";
      default:
        return "text-gray-400";
    }
  };

  return (
    <Tooltip content={tooltipContent} placement="left">
      <div className={`flex items-center space-x-1 ${className}`}>
        <BsCircleFill
          className={`${getStatusColor()} h-2.5 w-2.5 animate-pulse`}
        />
        <span className="text-xs text-gray-400">
          {status === "online" && latency !== null ? `${latency}ms` : ""}
        </span>
      </div>
    </Tooltip>
  );
};

export default ServerStatusIndicator;
