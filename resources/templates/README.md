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