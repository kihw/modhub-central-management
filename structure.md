# Structure du Projet ModHub Central

## Objectif du projet

Créer un hub centralisé qui regroupe et gère différents mods pour PC (Gaming Mod, NightMod, Media Mod…) avec une automatisation intelligente. Ce hub permet de détecter les processus actifs (jeux, médias…) et d'activer/désactiver automatiquement les mods selon des règles personnalisées. L'interface offre également un éditeur de scénarios permettant à l'utilisateur de créer des automatisations personnalisées (conditions/actions).

## Fonctionnalités principales

### 1. Détection intelligente
- Surveille en temps réel les processus système (jeux, apps multimédias).
- Détecte l'état du PC (heure, activité, veille).
- Active ou désactive les mods en fonction de ces données.

### 2. Gestion centralisée des mods
- **Mods intégrés** :
  - **Gaming Mod** : adapte les périphériques (clavier/souris/DPI/RGB) en fonction du jeu.
  - **NightMod** : ajuste la luminosité, active le mode nuit si l'utilisateur est inactif ou après une certaine heure.
  - **Media Mod** : ajuste le son, l'éclairage en fonction des applications multimédia.
- Ajout possible de nouveaux mods personnalisés.

### 3. Moteur d'automatisation (Automation Engine)
- Permet de créer des règles (conditions + actions).
- Exemple de règle :
  - **Si** : Heure > 22h et aucun jeu détecté
  - **Alors** : Activer NightMod.
- Priorisation entre mods pour éviter les conflits (ex : Gaming Mod prioritaire sur NightMod).

### 4. Interface utilisateur moderne (Electron + React)
- **Dashboard** : vue d'ensemble des mods actifs, infos système.
- **Mods** : gestion et configuration manuelle des mods.
- **Automation** : création/édition de règles avec un éditeur visuel.
- **Logs** : historique des actions et événements.
- **Settings** : réglages globaux du hub (thème, notifications, démarrage auto).

## Architecture technique

### Frontend (interface)
- Electron.js + React.js + TailwindCSS.
- Interface moderne, responsive, dark/light mode.

### Backend (logique métier)
- Python avec FastAPI.
- Gestion des processus système (psutil), périphériques (pynput, pyautogui).
- Moteur d'automatisation (gestion des règles/scénarios).
- Communication avec le frontend via API REST ou WebSocket.

### Stockage des règles/mods
- SQLite ou fichiers JSON/YAML.

## Structure des répertoires

```
modhub-central/
├── frontend/                 # Application Electron + React
│   ├── public/
│   ├── src/
│   │   ├── components/       # Composants React réutilisables
│   │   ├── pages/            # Pages de l'application 
│   │   │   ├── Dashboard/
│   │   │   ├── Mods/
│   │   │   ├── Automation/
│   │   │   ├── Logs/
│   │   │   └── Settings/
│   │   ├── services/         # Services frontend (API, notifications...)
│   │   ├── store/            # État global (Redux/Context)
│   │   ├── utils/            # Fonctions utilitaires
│   │   ├── App.jsx           # Composant principal
│   │   └── index.jsx         # Point d'entrée React
│   ├── electron/             # Code spécifique à Electron
│   ├── package.json
│   └── tailwind.config.js
│
├── backend/                  # Serveur Python + FastAPI
│   ├── api/                  # Routes API
│   │   ├── mods.py
│   │   ├── automation.py
│   │   ├── system.py
│   │   └── settings.py
│   ├── core/                 # Logique métier principale
│   │   ├── process_monitor/  # Surveillance des processus
│   │   ├── mods/            # Implémentation des différents mods
│   │   │   ├── gaming_mod.py
│   │   │   ├── night_mod.py
│   │   │   ├── media_mod.py
│   │   │   └── mod_base.py   # Classe de base pour les mods
│   │   ├── automation/      # Moteur d'automatisation
│   │   │   ├── engine.py     # Évaluation des règles
│   │   │   ├── conditions.py # Types de conditions disponibles
│   │   │   └── actions.py    # Types d'actions disponibles
│   │   └── device_control/  # Contrôle des périphériques
│   ├── db/                  # Gestion de la base de données
│   │   ├── models.py        # Modèles de données
│   │   └── crud.py          # Opérations CRUD
│   ├── main.py              # Point d'entrée de l'API
│   └── requirements.txt     # Dépendances Python
│
├── resources/               # Ressources partagées
│   ├── assets/              # Images, icônes, etc.
│   └── templates/           # Templates de règles, mods...
│
├── data/                    # Données utilisateur (configurations, règles)
│   ├── config.json          # Configuration générale
│   ├── mods/                # Configuration des mods
│   └── rules/               # Règles d'automatisation
│
├── LICENSE
└── README.md
```

## Workflow général

1. Surveillance en continu du système par le backend Python (processus, heure, activité).
2. Évaluation des règles définies dans l'Automation Engine.
3. Activation/Désactivation des mods selon les conditions et priorités.
4. Mise à jour de l'interface Electron (affichage des mods actifs, logs, etc.).
5. Interaction utilisateur via l'interface :
   - Création de règles, gestion des mods, visualisation des logs.