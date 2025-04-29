# ModHub Central - Hub Centralisé de Gestion de Mods PC

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Status](https://img.shields.io/badge/status-en%20développement-yellow)

## 📋 Présentation

ModHub Central est une application permettant de gérer de façon centralisée différents "mods" pour PC (Gaming Mod, NightMod, Media Mod...) avec une automatisation intelligente. Le hub détecte les processus actifs et adapte automatiquement votre environnement selon vos préférences.

## 🚀 Fonctionnalités principales

### 🔍 Détection intelligente
- Surveillance en temps réel des processus système (jeux, applications multimédia)
- Détection de l'état du PC (heure, activité utilisateur, mode veille)
- Activation/désactivation automatique des mods selon le contexte

### 🎮 Gestion centralisée des mods
- **Gaming Mod** : optimise vos périphériques (clavier, souris, DPI, RGB) en fonction du jeu détecté
- **NightMod** : ajuste la luminosité et active le mode nuit en période d'inactivité ou après certaines heures
- **Media Mod** : optimise les paramètres audio et d'éclairage pour les applications multimédia
- Possibilité d'ajouter vos propres mods personnalisés

### ⚙️ Moteur d'automatisation
- Création de règles personnalisées (conditions + actions)
- Système de priorités pour éviter les conflits entre mods
- Éditeur visuel pour créer facilement vos scénarios d'automatisation

### 🖥️ Interface utilisateur moderne
- Dashboard intuitif avec vue d'ensemble des mods actifs
- Gestion détaillée de chaque mod
- Éditeur de règles d'automatisation
- Historique des événements et actions
- Personnalisation complète des préférences

## 🛠️ Technologies utilisées

### Frontend
- Electron.js
- React.js
- TailwindCSS

### Backend
- Python avec FastAPI
- psutil pour la surveillance des processus
- pynput et pyautogui pour la gestion des périphériques

### Stockage
- SQLite / JSON / YAML pour les configurations et règles

## 🔧 Installation

### Prérequis
- Python 3.8 ou supérieur
- Node.js 14 ou supérieur
- npm 6 ou supérieur

### Étapes d'installation

1. **Cloner le dépôt :**
```bash
git clone https://github.com/kihw/modhub-central-management.git
cd modhub-central-management
```

2. **Lancer l'application avec le script automatisé :**
```bash
python run.py
```

Le script `run.py` va automatiquement :
- Créer un environnement virtuel Python
- Installer les dépendances backend et frontend
- Démarrer le serveur backend (FastAPI)
- Lancer l'interface frontend (Electron/React)

### Installation manuelle (si nécessaire)

Si vous préférez installer les composants séparément :

1. **Configurer le backend :**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configurer le frontend :**
```bash
cd frontend
npm install
```

3. **Démarrer les services séparément :**
```bash
# Terminal 1 (Backend)
cd backend
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
python main.py

# Terminal 2 (Frontend)
cd frontend
npm start
```

## 🔍 Dépannage

### Problème de connexion au backend

Si vous rencontrez des erreurs de connexion au backend (`ERR_CONNECTION_REFUSED`), vérifiez les points suivants :

1. **Vérifier que le backend est bien démarré :**
   - Le terminal exécutant le backend devrait afficher : "ModHub Central backend service started successfully"
   - Le service devrait être accessible à l'adresse http://localhost:8668/
   - Essayez d'accéder à http://localhost:8668/docs pour voir la documentation de l'API

2. **Vérifier les ports :**
   - Assurez-vous que le port 8668 n'est pas déjà utilisé par une autre application
   - Si vous devez changer le port, modifiez-le dans les fichiers :
     - `backend/main.py` (valeur du port)
     - `frontend/src/context/BackendContext.jsx` (URL du backend)

3. **Redémarrer complètement l'application :**
   - Arrêtez tous les services en cours (Ctrl+C dans les terminaux)
   - Réexécutez le script `run.py`

### Problèmes de dépendances

1. **Erreurs d'importation Python :**
   - Vérifiez que toutes les dépendances sont installées : `pip install -r backend/requirements.txt`
   - Assurez-vous que vous utilisez l'environnement virtuel correct

2. **Erreurs NPM :**
   - Essayez de nettoyer le cache npm : `npm cache clean --force`
   - Supprimez le dossier node_modules et réinstallez : `rm -rf node_modules && npm install`

## 📝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou soumettre une pull request.

### Directives pour contribuer

1. Fork le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add some amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## 📜 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

⭐ Si ce projet vous intéresse, n'hésitez pas à lui donner une étoile sur GitHub !
