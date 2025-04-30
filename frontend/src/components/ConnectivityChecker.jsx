import { useState, useEffect, useCallback } from "react";
import {
  FiWifi,
  FiWifiOff,
  FiRefreshCw,
  FiServer,
  FiAlertTriangle,
  FiCheckCircle,
} from "react-icons/fi";
import axios from "axios";

/**
 * ConnectivityChecker - Composant amélioré pour surveiller et afficher l'état de connexion au backend
 *
 * @param {Object} props
 * @param {number} props.checkInterval - Intervalle en ms entre les vérifications de connectivité (défaut: 30000)
 * @param {Function} props.onStatusChange - Callback lorsque l'état de connectivité change
 * @param {boolean} props.showMiniDisplay - Afficher uniquement un indicateur de statut compact
 * @param {string} props.className - Classes CSS additionnelles
 */
const ConnectivityChecker = ({
  checkInterval = 30000,
  onStatusChange = () => {},
  showMiniDisplay = false,
  className = "",
}) => {
  const [isConnected, setIsConnected] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const [lastChecked, setLastChecked] = useState(null);
  const [isChecking, setIsChecking] = useState(false);
  const [backendInfo, setBackendInfo] = useState(null);
  const [lastError, setLastError] = useState(null);
  const [services, setServices] = useState({
    modEngine: false,
    processMonitor: false,
    database: false,
  });

  // Fonction pour vérifier la connectivité au backend
  const checkConnectivity = useCallback(async () => {
    if (isChecking) return;

    setIsChecking(true);
    try {
      const response = await axios.get("/api/health", {
        timeout: 5000,
      });

      const wasConnected = isConnected;
      setIsConnected(true);
      setBackendInfo(response.data);
      setLastChecked(new Date());
      setRetryCount(0);
      setLastError(null);

      // Mise à jour des services si disponible dans la réponse
      if (response.data?.services) {
        setServices(response.data.services);
      } else {
        // Valeurs par défaut si non disponible
        setServices({
          modEngine: true,
          processMonitor: true,
          database: true,
        });
      }

      // Appel du callback si l'état a changé
      if (wasConnected === false || wasConnected === null) {
        onStatusChange(true, response.data);
      }
    } catch (error) {
      console.error("Backend connectivity check failed:", error);

      const wasConnected = isConnected;
      setIsConnected(false);
      setRetryCount((prev) => prev + 1);
      setLastChecked(new Date());
      setLastError(error.message || "Connection failed");

      // Appel du callback si l'état a changé
      if (wasConnected === true || wasConnected === null) {
        onStatusChange(false, { error: error.message });
      }
    } finally {
      setIsChecking(false);
    }
  }, [isConnected, isChecking, onStatusChange]);

  // Vérification initiale et configuration des vérifications périodiques
  useEffect(() => {
    // Vérification initiale
    checkConnectivity();

    // Configuration des vérifications périodiques
    const intervalId = setInterval(checkConnectivity, checkInterval);

    // Nettoyage
    return () => clearInterval(intervalId);
  }, [checkInterval, checkConnectivity]);

  // Version minimale (icône uniquement)
  if (showMiniDisplay) {
    return (
      <div className={`inline-flex items-center ${className}`}>
        {isConnected === null ? (
          <div className="text-gray-500" title="Vérification de la connexion">
            <FiRefreshCw className="animate-spin" />
          </div>
        ) : isConnected ? (
          <div
            className="text-green-500 flex items-center gap-1"
            title="Connecté au backend"
          >
            <FiWifi />
            <span className="text-xs">
              {backendInfo?.uptime ? formatUptime(backendInfo.uptime) : ""}
            </span>
          </div>
        ) : (
          <div
            className="text-red-500 animate-pulse"
            title="Erreur de connexion au backend"
          >
            <FiWifiOff />
          </div>
        )}
      </div>
    );
  }

  // Version complète avec détails
  return (
    <div
      className={`p-4 rounded-lg shadow-md ${className} ${
        isConnected === null
          ? "bg-gray-100 dark:bg-gray-800"
          : isConnected
          ? "bg-green-50 dark:bg-green-900/20"
          : "bg-red-50 dark:bg-red-900/20"
      }`}
    >
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium flex items-center gap-2">
          <FiServer />
          <span>État du Backend</span>
        </h3>
        <button
          onClick={checkConnectivity}
          disabled={isChecking}
          className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-50 transition-colors"
          title="Vérifier maintenant"
        >
          <FiRefreshCw className={`${isChecking ? "animate-spin" : ""}`} />
        </button>
      </div>

      <div className="mt-3">
        <div className="flex items-center">
          <div
            className={`w-3 h-3 rounded-full mr-2 ${
              isConnected === null
                ? "bg-gray-400"
                : isConnected
                ? "bg-green-500"
                : "bg-red-500"
            }`}
          ></div>
          <span className="font-medium">
            {isConnected === null
              ? "Vérification de la connexion..."
              : isConnected
              ? "Connecté au backend"
              : "Erreur de connexion"}
          </span>
        </div>

        {lastChecked && (
          <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Dernière vérification: {lastChecked.toLocaleTimeString()}
          </div>
        )}

        {!isConnected && retryCount > 0 && (
          <div className="mt-2 text-sm text-red-600 dark:text-red-400 flex items-center">
            <FiAlertTriangle className="mr-1" />
            <span>Tentatives échouées: {retryCount}</span>
          </div>
        )}

        {lastError && !isConnected && (
          <div className="mt-2 p-2 bg-red-100 dark:bg-red-900/30 rounded text-xs text-red-800 dark:text-red-300 font-mono">
            {lastError}
          </div>
        )}

        {isConnected && backendInfo && (
          <div className="mt-3 space-y-2">
            <div className="text-sm flex flex-col gap-1">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">
                  Version:
                </span>
                <span className="font-medium">
                  {backendInfo.version || "Inconnue"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">
                  Uptime:
                </span>
                <span className="font-medium">
                  {formatUptime(backendInfo.uptime)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">
                  Environnement:
                </span>
                <span className="font-medium">
                  {backendInfo.environment || "Production"}
                </span>
              </div>
            </div>

            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
              <h4 className="text-sm font-medium mb-2">Services:</h4>
              <div className="grid grid-cols-2 gap-2">
                <div className="flex items-center">
                  <div
                    className={`w-2 h-2 rounded-full mr-2 ${
                      services.modEngine ? "bg-green-500" : "bg-red-500"
                    }`}
                  ></div>
                  <span className="text-xs">Mod Engine</span>
                </div>
                <div className="flex items-center">
                  <div
                    className={`w-2 h-2 rounded-full mr-2 ${
                      services.processMonitor ? "bg-green-500" : "bg-red-500"
                    }`}
                  ></div>
                  <span className="text-xs">Processus</span>
                </div>
                <div className="flex items-center">
                  <div
                    className={`w-2 h-2 rounded-full mr-2 ${
                      services.database ? "bg-green-500" : "bg-red-500"
                    }`}
                  ></div>
                  <span className="text-xs">Base de données</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Fonction utilitaire pour formater la durée d'activité
const formatUptime = (seconds) => {
  if (!seconds && seconds !== 0) return "Inconnu";

  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = Math.floor(seconds % 60);

  if (days > 0) {
    return `${days}j ${hours}h ${minutes}m`;
  } else if (hours > 0) {
    return `${hours}h ${minutes}m ${remainingSeconds}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`;
  } else {
    return `${remainingSeconds}s`;
  }
};

export default ConnectivityChecker;
