import axios from 'axios';

class ApiService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
    this.axiosInstance = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add interceptors for request/response handling
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  // =========== MOD MANAGEMENT ===========

  async getAllMods() {
    try {
      const response = await this.axiosInstance.get('/mods');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch mods:', error);
      throw error;
    }
  }

  async getMod(modId) {
    try {
      const response = await this.axiosInstance.get(`/mods/${modId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch mod with ID ${modId}:`, error);
      throw error;
    }
  }

  async createMod(modData) {
    try {
      const response = await this.axiosInstance.post('/mods', modData);
      return response.data;
    } catch (error) {
      console.error('Failed to create mod:', error);
      throw error;
    }
  }

  async updateMod(modId, modData) {
    try {
      const response = await this.axiosInstance.put(`/mods/${modId}`, modData);
      return response.data;
    } catch (error) {
      console.error(`Failed to update mod with ID ${modId}:`, error);
      throw error;
    }
  }

  async deleteMod(modId) {
    try {
      const response = await this.axiosInstance.delete(`/mods/${modId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to delete mod with ID ${modId}:`, error);
      throw error;
    }
  }

  async activateMod(modId) {
    try {
      const response = await this.axiosInstance.post(`/mods/${modId}/activate`);
      return response.data;
    } catch (error) {
      console.error(`Failed to activate mod with ID ${modId}:`, error);
      throw error;
    }
  }

  async deactivateMod(modId) {
    try {
      const response = await this.axiosInstance.post(`/mods/${modId}/deactivate`);
      return response.data;
    } catch (error) {
      console.error(`Failed to deactivate mod with ID ${modId}:`, error);
      throw error;
    }
  }

  // =========== RULES MANAGEMENT ===========

  async getAllRules() {
    try {
      const response = await this.axiosInstance.get('/rules');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch rules:', error);
      throw error;
    }
  }

  async getRule(ruleId) {
    try {
      const response = await this.axiosInstance.get(`/rules/${ruleId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch rule with ID ${ruleId}:`, error);
      throw error;
    }
  }

  async createRule(ruleData) {
    try {
      const response = await this.axiosInstance.post('/rules', ruleData);
      return response.data;
    } catch (error) {
      console.error('Failed to create rule:', error);
      throw error;
    }
  }

  async updateRule(ruleId, ruleData) {
    try {
      const response = await this.axiosInstance.put(`/rules/${ruleId}`, ruleData);
      return response.data;
    } catch (error) {
      console.error(`Failed to update rule with ID ${ruleId}:`, error);
      throw error;
    }
  }

  async deleteRule(ruleId) {
    try {
      const response = await this.axiosInstance.delete(`/rules/${ruleId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to delete rule with ID ${ruleId}:`, error);
      throw error;
    }
  }

  // =========== SYSTEM STATUS ===========

  async getSystemStatus() {
    try {
      const response = await this.axiosInstance.get('/system/status');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch system status:', error);
      throw error;
    }
  }

  async getActiveProcesses() {
    try {
      const response = await this.axiosInstance.get('/system/processes');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch active processes:', error);
      throw error;
    }
  }

  // =========== SETTINGS ===========

  async getSettings() {
    try {
      const response = await this.axiosInstance.get('/settings');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch settings:', error);
      throw error;
    }
  }

  async updateSettings(settingsData) {
    try {
      const response = await this.axiosInstance.put('/settings', settingsData);
      return response.data;
    } catch (error) {
      console.error('Failed to update settings:', error);
      throw error;
    }
  }

  // =========== EVENT LOGS ===========

  async getEventLogs(limit = 50, offset = 0) {
    try {
      const response = await this.axiosInstance.get(`/events?limit=${limit}&offset=${offset}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch event logs:', error);
      throw error;
    }
  }
}

export default new ApiService();