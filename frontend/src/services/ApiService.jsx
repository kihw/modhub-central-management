import axios from "axios";

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:5000/api", // Ajuste selon ton backend
  timeout: 10000, // 10 sec timeout
});

/**
 * Optionnel : Interceptors pour ajouter des headers (ex: Auth)
 */
// apiClient.interceptors.request.use((config) => {
//   // Exemple : Ajouter un token
//   const token = localStorage.getItem('token');
//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`;
//   }
//   return config;
// });

/**
 * Méthodes génériques
 */
const ApiService = {
  get: (url, config = {}) => apiClient.get(url, config),
  post: (url, data, config = {}) => apiClient.post(url, data, config),
  put: (url, data, config = {}) => apiClient.put(url, data, config),
  delete: (url, config = {}) => apiClient.delete(url, config),

  /**
   * Endpoints spécifiques (à ajuster selon ton backend)
   */
  getStatus: () => apiClient.get("/status"),
  getMods: () => apiClient.get("/mods"),
  getAutomations: () => apiClient.get("/automations"),
  createAutomation: (data) => apiClient.post("/automations", data),
};

export default ApiService;
