# ✅ TODO List – ModHub Central Management

Ce fichier recense les **tâches restantes** pour rendre ce projet **100% fonctionnel**, basé sur l’analyse réelle du code existant.

---

## 🧩 Intégration & Structure Générale

- [ ] Ajouter une interface CLI ou des options dans `run.py` pour le lancement.
- [ ] Gérer les variables d’environnement via `.env` et `python-dotenv`.
- [ ] Ajouter un système de migration de base de données (ex: Alembic).
- [ ] Ajouter une documentation automatique de l’API (Swagger/OpenAPI via FastAPI).
- [ ] Vérifier l’enregistrement de toutes les routes dans `main.py`.

---

## 🧪 Tests & Robustesse

- [ ] Créer une suite de tests unitaires (utiliser `pytest`, `httpx`, etc.).
- [ ] Ajouter un répertoire `tests/` et tester chaque route d’API.
- [ ] Tester les gestionnaires d’exceptions définis dans `main.py`.
- [ ] Ajouter des tests pour les fonctions critiques comme `apply_mod` ou `toggle_rule_status`.

---

## 🔐 Sécurité

- [ ] Ajouter une authentification (clé API, OAuth2 ou JWT).
- [ ] Limiter l'accès à certaines routes critiques via permissions/roles.

---

## 🔄 Cohérence & Refactorisation

- [ ] Corriger la double définition de `get_active_mods_count` dans `mods.py`.
- [ ] Nettoyer les fonctions redondantes dans `settings.py` (`get` vs `get_setting`, etc.).
- [ ] Extraire les schémas de données Pydantic dans un module `schemas/`.
- [ ] Factoriser les opérations CRUD répétitives entre modules.

---

## ⚙️ DevOps & Déploiement

- [ ] Ajouter un `Dockerfile` pour conteneuriser l’application.
- [ ] Créer un `docker-compose.yml` pour orchestrer les services liés (DB, backend).
- [ ] Mettre en place une CI/CD minimale (lint, tests, build) via GitHub Actions ou GitLab CI.

---

## 📚 Documentation

- [ ] Compléter `README.md` : installation, utilisation, endpoints disponibles.
- [ ] Ajouter une carte de l’architecture (déjà esquissée avec `.mmd`).
- [ ] Ajouter des exemples d’utilisation de l’API (ex: via `curl`, Postman).

---

## 📦 Dépendances & Qualité

- [ ] Vérifier le contenu de `requirements.txt` (manques potentiels).
- [ ] Ajouter un linter (flake8, black) + formatage automatique.
- [ ] Documenter les conventions de nommage et structure de projet.
