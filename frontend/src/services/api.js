/**
 * API Service
 *
 * Ce service gère les communications avec le backend via Electron IPC.
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

      ipcRenderer.once(responseChannel, (_, response) => {
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

      setTimeout(() => {
        ipcRenderer.removeAllListeners(responseChannel);
        reject(new Error(`Request timeout: ${method} ${endpoint}`));
      }, 30000);
    });
  },

  // Implémentation Web
  async _requestWeb(method, endpoint, data, params) {
    const config = { params };

    switch (method.toLowerCase()) {
      case "get":
        return (await apiClient.get(endpoint, config)).data;
      case "post":
        return (await apiClient.post(endpoint, data, config)).data;
      case "put":
        return (await apiClient.put(endpoint, data, config)).data;
      case "patch":
        return (await apiClient.patch(endpoint, data, config)).data;
      case "delete":
        return (await apiClient.delete(endpoint, config)).data;
      default:
        throw new Error(`Unsupported method: ${method}`);
    }
  },

  // Méthodes spécifiques à ModHub Central
  async getMods() {
    return this.request("get", "/mods");
  },

  async getModById(modId) {
    return this.request("get", `/mods/${modId}`);
  },

  async toggleMod(modId, enabled) {
    return this.request("patch", `/mods/${modId}/toggle`, { enabled });
  },

  async updateModSettings(modId, settings) {
    return this.request("patch", `/mods/${modId}/settings`, settings);
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

  async getSystemStatus() {
    return this.request("get", "/system/info");
  },

  async getRunningProcesses() {
    return this.request("get", "/system/processes");
  },

  async getSettings() {
    return this.request("get", "/settings");
  },

  async updateSettings(settings) {
    return this.request("put", "/settings", settings);
  },
};

export default ApiService;
