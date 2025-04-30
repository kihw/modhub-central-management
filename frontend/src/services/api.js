import axios from "axios";

const isElectron = window?.process?.type;
const ipcRenderer = isElectron ? window.require("electron").ipcRenderer : null;

const API_TIMEOUT = 10000;
const ELECTRON_TIMEOUT = 30000;
const MAX_ERROR_LOG = 20;
const MAX_RETRIES = 2;
const RETRY_DELAY_BASE = 1000;
const API_BASE_URL = "http://localhost:8668/api";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    "Content-Type": "application/json",
  },
});

const handleError = (error) => {
  const errorLog = JSON.parse(sessionStorage.getItem('api_errors') || '[]');
  errorLog.unshift({
    timestamp: new Date().toISOString(),
    url: error.config?.url,
    method: error.config?.method,
    status: error.response?.status || 'network_error',
    message: error.message
  });
  errorLog.length = Math.min(errorLog.length, MAX_ERROR_LOG);
  sessionStorage.setItem('api_errors', JSON.stringify(errorLog));
  return Promise.reject(error);
};

apiClient.interceptors.response.use(response => response, handleError);

const ApiService = {
  async request(method, endpoint, data = null, params = null) {
    if (!endpoint.startsWith('/')) endpoint = '/' + endpoint;
    return isElectron 
      ? this._requestElectron(method, endpoint, data, params)
      : this._requestWeb(method, endpoint, data, params);
  },

  async _requestElectron(method, endpoint, data, params) {
    const requestId = `${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
    const responseChannel = `api_response_${requestId}`;

    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        ipcRenderer?.removeAllListeners(responseChannel);
        reject(new Error(`Request timeout: ${method} ${endpoint}`));
      }, ELECTRON_TIMEOUT);

      ipcRenderer?.once(responseChannel, (_, response) => {
        clearTimeout(timeoutId);
        if (response.error) {
          reject(new Error(response.error));
        } else {
          resolve(response.data);
        }
      });

      ipcRenderer?.send("api_request", {
        method,
        endpoint,
        data,
        params,
        requestId,
        responseChannel,
      });
    });
  },

  async _requestWeb(method, endpoint, data, params, retryCount = 0) {
    try {
      const config = { params };
      const isGetOrDelete = ['get', 'delete'].includes(method.toLowerCase());
      const response = await apiClient[method.toLowerCase()](
        endpoint,
        isGetOrDelete ? config : data,
        isGetOrDelete ? undefined : config
      );
      return response.data;
    } catch (error) {
      if (error.message?.includes('Network Error') && retryCount < MAX_RETRIES) {
        const delay = RETRY_DELAY_BASE * (2 ** retryCount);
        await new Promise(resolve => setTimeout(resolve, delay));
        return this._requestWeb(method, endpoint, data, params, retryCount + 1);
      }
      throw error;
    }
  },

  getSystemStatus: () => ApiService.request("get", "status"),
  getMods: () => ApiService.request("get", "mods"),
  getModById: (modId) => ApiService.request("get", `mods/${modId}`),
  toggleMod: (modId, enabled) => ApiService.request("post", `mods/${modId}/toggle`, { enabled }),
  updateModSettings: (modId, settings) => ApiService.request("put", `mods/${modId}/settings`, settings),
  getRules: () => ApiService.request("get", "automation"),
  createRule: (rule) => ApiService.request("post", "automation", rule),
  updateRule: (ruleId, rule) => ApiService.request("put", `automation/${ruleId}`, rule),
  deleteRule: (ruleId) => ApiService.request("delete", `automation/${ruleId}`),
  getRunningProcesses: () => ApiService.request("get", "system/processes"),
  getResourceUsage: () => ApiService.request("get", "system/resources"),
  getSettings: () => ApiService.request("get", "settings"),
  updateSettings: (settings) => ApiService.request("put", "settings", settings),

  getLastErrors() {
    try {
      return JSON.parse(sessionStorage.getItem('api_errors') || '[]');
    } catch {
      return [];
    }
  },

  clearErrorLog() {
    sessionStorage.removeItem('api_errors');
  }
};

export default ApiService;