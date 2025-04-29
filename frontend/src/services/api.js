/**
 * API Service
 *
 * Ce service gère les communications avec le backend via Electron IPC ou requêtes HTTP directes.
 * Il encapsule tous les appels API nécessaires pour l'application.
 */
import axios from "axios";

// Déterminer si nous sommes dans Electron
const isElectron = window && window.process && window.process.type;
const ipcRenderer = isElectron ? window.require("electron").ipcRenderer : null;

// Configuration de base axios
const apiClient = axios.create({
  baseURL: "http://localhost:8668/api",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Ajouter les intercepteurs pour gérer les erreurs globalement
apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error("API Error:", error.message || "Unknown error");
    
    // Stocker l'erreur dans le sessionStorage pour le diagnostic
    try {
      const errorLog = JSON.parse(sessionStorage.getItem('api_errors') || '[]');
      errorLog.push({
        timestamp: new Date().toISOString(),
        url: error.config?.url || 'unknown',
        method: error.config?.method || 'unknown',
        status: error.response?.status || 'network_error',
        message: error.message
      });
      
      // Limiter à 20 erreurs récentes
      while (errorLog.length > 20) errorLog.shift();
      
      sessionStorage.setItem('api_errors', JSON.stringify(errorLog));
    } catch (e) {
      // Ignorer les erreurs de storage
    }
    
    return Promise.reject(error);
  }
);

// Service API central qui gère les deux modes (Electron et Web)
const ApiService = {
  // Méthode générique pour toutes les requêtes
  async request(method, endpoint, data = null, params = null) {
    try {
      if (isElectron) {
        // Version Electron utilisant IPC
        return await this._requestElectron(method, endpoint, data, params);
      } else {
        // Version Web utilisant Axios
        return await this._requestWeb(method, endpoint, data, params);
      }
    } catch (error) {
      console.error(`API Error (${method} ${endpoint}):`, error);
      throw error;
    }
  },

  // Implémentation Electron
  async _requestElectron(method, endpoint, data, params) {
    return new Promise((resolve, reject) => {
      const requestId = `req_${Date.now()}_${Math.random()
        .toString(36)
        .substr(2, 9)}`;
      const responseChannel = `api_response_${requestId}`;

      // Définir un timeout en cas de non-réponse
      const timeoutId = setTimeout(() => {
        ipcRenderer.removeAllListeners(responseChannel);
        reject(new Error(`Request timeout: ${method} ${endpoint}`));
      }, 30000);

      ipcRenderer.once(responseChannel, (_, response) => {
        clearTimeout(timeoutId);
        if (response.error) {
          reject(new Error(response.error));
        } else {
          resolve(response.data);
        }
      });

      ipcRenderer.send("api_request", {
        method,
        endpoint,
        data,
        params,
        requestId,
        responseChannel,
      });
    });
  },

  // Implémentation Web avec mécanisme de retry
  async _requestWeb(method, endpoint, data, params, retryCount = 0) {
    const MAX_RETRIES = 2;
    const config = { params };

    try {
      let response;
      
      switch (method.toLowerCase()) {
        case "get":
          response = await apiClient.get(endpoint, config);
          break;
        case "post":
          response = await apiClient.post(endpoint, data, config);
          break;
        case "put":
          response = await apiClient.put(endpoint, data, config);
          break;
        case "patch":
          response = await apiClient.patch(endpoint, data, config);
          break;
        case "delete":
          response = await apiClient.delete(endpoint, config);
          break;
        default:
          throw new Error(`Unsupported method: ${method}`);
      }
      
      return response.data;
    } catch (error) {
      // Si l'erreur est due à un problème réseau et qu'on n'a pas dépassé le nombre de tentatives
      if (error.message && error.message.includes('Network Error') && retryCount < MAX_RETRIES) {
        console.log(`Retrying request (${retryCount + 1}/${MAX_RETRIES}): ${method} ${endpoint}`);
        // Attendre un peu avant de réessayer (backoff exponentiel)
        await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, retryCount)));
        return this._requestWeb(method, endpoint, data, params, retryCount + 1);
      }
      
      throw error;
    }
  },

  // Service de santé du backend
  async getSystemStatus() {
    return this.request("get", "/status");
  },

  // Méthodes spécifiques aux modules de ModHub Central
  async getMods() {
    return this.request("get", "/mods");
  },

  async getModById(modId) {
    return this.request("get", `/mods/${modId}`);
  },

  async toggleMod(modId, enabled) {
    return this.request("post", `/mods/${modId}/toggle`, { enabled });
  },

  async updateModSettings(modId, settings) {
    return this.request("put", `/mods/${modId}/settings`, settings);
  },

  async getRules() {
    return this.request("get", "/automation");
  },

  async createRule(rule) {
    return this.request("post", "/automation", rule);
  },

  async updateRule(ruleId, rule) {
    return this.request("put", `/automation/${ruleId}`, rule);
  },

  async deleteRule(ruleId) {
    return this.request("delete", `/automation/${ruleId}`);
  },

  // Informations système
  async getRunningProcesses() {
    return this.request("get", "/system/processes");
  },

  async getResourceUsage() {
    return this.request("get", "/system/resources");
  },

  // Paramètres de l'application
  async getSettings() {
    return this.request("get", "/settings");
  },

  async updateSettings(settings) {
    return this.request("put", "/settings", settings);
  },

  // Méthode de diagnostic
  getLastErrors() {
    try {
      return JSON.parse(sessionStorage.getItem('api_errors') || '[]');
    } catch (e) {
      return [];
    }
  },

  clearErrorLog() {
    try {
      sessionStorage.removeItem('api_errors');
    } catch (e) {
      // Ignorer les erreurs
    }
  }
};

export default ApiService;