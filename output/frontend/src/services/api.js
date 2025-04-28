/**
 * API Service
 * 
 * Ce service gère les communications avec le backend via Electron IPC.
 * Il encapsule tous les appels API nécessaires pour l'application.
 */

const { ipcRenderer } = window.require('electron');

/**
 * Classe pour la gestion des appels API
 */
class ApiService {
  /**
   * Envoie une requête au backend via IPC et retourne une promesse
   * @param {string} channel - Le canal IPC à utiliser
   * @param {any} data - Les données à envoyer (facultatif)
   * @returns {Promise<any>} - Promesse contenant la réponse
   */
  static send(channel, data = null) {
    return new Promise((resolve, reject) => {
      // Génération d'un ID unique pour cette requête
      const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      // Canal de réponse unique pour cette requête
      const responseChannel = `${channel}_response_${requestId}`;
      
      // Écoute de la réponse une seule fois
      ipcRenderer.once(responseChannel, (_, response) => {
        if (response.error) {
          reject(new Error(response.error));
        } else {
          resolve(response.data);
        }
      });
      
      // Envoi de la requête
      ipcRenderer.send(channel, { data, requestId, responseChannel });
      
      // Timeout de sécurité après 30 secondes
      setTimeout(() => {
        ipcRenderer.removeAllListeners(responseChannel);
        reject(new Error(`La requête vers ${channel} a expiré après 30 secondes`));
      }, 30000);
    });
  }

  // ===== Méthodes pour les fichiers =====
  
  /**
   * Ouvre un fichier
   * @param {string} filePath - Chemin du fichier à ouvrir
   * @returns {Promise<Object>} - Promesse contenant les données du fichier
   */
  static openFile(filePath) {
    return this.send('file:open', { filePath });
  }
  
  /**
   * Sauvegarde un fichier
   * @param {string} filePath - Chemin du fichier
   * @param {Object} content - Contenu à sauvegarder
   * @returns {Promise<boolean>} - Promesse indiquant le succès
   */
  static saveFile(filePath, content) {
    return this.send('file:save', { filePath, content });
  }
  
  /**
   * Ouvre une boîte de dialogue pour sélectionner un fichier
   * @param {Object} options - Options de la boîte de dialogue
   * @returns {Promise<string>} - Promesse contenant le chemin du fichier sélectionné
   */
  static showOpenDialog(options = {}) {
    return this.send('dialog:open', options);
  }
  
  /**
   * Ouvre une boîte de dialogue pour sauvegarder un fichier
   * @param {Object} options - Options de la boîte de dialogue
   * @returns {Promise<string>} - Promesse contenant le chemin du fichier
   */
  static showSaveDialog(options = {}) {
    return this.send('dialog:save', options);
  }

  // ===== Méthodes pour la base de données =====
  
  /**
   * Récupère les catégories
   * @returns {Promise<Array>} - Promesse contenant les catégories
   */
  static getCategories() {
    return this.send('db:getCategories');
  }
  
  /**
   * Ajoute une catégorie
   * @param {Object} category - Données de la catégorie
   * @returns {Promise<Object>} - Promesse contenant la catégorie créée
   */
  static addCategory(category) {
    return this.send('db:addCategory', category);
  }
  
  /**
   * Met à jour une catégorie
   * @param {Object} category - Données de la catégorie
   * @returns {Promise<Object>} - Promesse contenant la catégorie mise à jour
   */
  static updateCategory(category) {
    return this.send('db:updateCategory', category);
  }
  
  /**
   * Supprime une catégorie
   * @param {number} categoryId - ID de la catégorie
   * @returns {Promise<boolean>} - Promesse indiquant le succès
   */
  static deleteCategory(categoryId) {
    return this.send('db:deleteCategory', { categoryId });
  }
  
  /**
   * Récupère les questions d'une catégorie
   * @param {number} categoryId - ID de la catégorie
   * @returns {Promise<Array>} - Promesse contenant les questions
   */
  static getQuestions(categoryId) {
    return this.send('db:getQuestions', { categoryId });
  }
  
  /**
   * Ajoute une question
   * @param {Object} question - Données de la question
   * @returns {Promise<Object>} - Promesse contenant la question créée
   */
  static addQuestion(question) {
    return this.send('db:addQuestion', question);
  }
  
  /**
   * Met à jour une question
   * @param {Object} question - Données de la question
   * @returns {Promise<Object>} - Promesse contenant la question mise à jour
   */
  static updateQuestion(question) {
    return this.send('db:updateQuestion', question);
  }
  
  /**
   * Supprime une question
   * @param {number} questionId - ID de la question
   * @returns {Promise<boolean>} - Promesse indiquant le succès
   */
  static deleteQuestion(questionId) {
    return this.send('db:deleteQuestion', { questionId });
  }
  
  // ===== Méthodes pour le jeu =====
  
  /**
   * Commence une nouvelle partie
   * @param {Object} gameSettings - Paramètres de la partie
   * @returns {Promise<Object>} - Promesse contenant les données de la partie
   */
  static startGame(gameSettings) {
    return this.send('game:start', gameSettings);
  }
  
  /**
   * Soumet une réponse
   * @param {Object} answerData - Données de la réponse
   * @returns {Promise<Object>} - Promesse contenant le résultat
   */
  static submitAnswer(answerData) {
    return this.send('game:submitAnswer', answerData);
  }
  
  /**
   * Termine une partie
   * @param {number} gameId - ID de la partie
   * @returns {Promise<Object>} - Promesse contenant les statistiques de la partie
   */
  static endGame(gameId) {
    return this.send('game:end', { gameId });
  }
  
  // ===== Méthodes pour les statistiques =====
  
  /**
   * Récupère les statistiques de jeu
   * @returns {Promise<Object>} - Promesse contenant les statistiques
   */
  static getStatistics() {
    return this.send('stats:get');
  }
  
  /**
   * Réinitialise les statistiques
   * @returns {Promise<boolean>} - Promesse indiquant le succès
   */
  static resetStatistics() {
    return this.send('stats:reset');
  }
}

export default ApiService;