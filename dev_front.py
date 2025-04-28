import anthropic
import os
import re

# Configuration de l'API Claude
client = anthropic.Client(api_key="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")

# Chemin du dossier output
output_dir = "output"

# System prompt pour Claude
system_prompt = """
Tu es une IA experte en développement frontend. Ta mission est de générer, corriger et optimiser le code React/Electron du projet.

Consignes :
- Si le fichier est existant, optimise et corrige le code (lisibilité, bonnes pratiques, performance).
- Si le fichier est manquant, génère-le entièrement en respectant les conventions du projet React/Electron.
- Ne modifie pas la logique métier globale du projet.
- Fournis uniquement le bloc de code corrigé ou généré dans le bon format (avec le chemin du fichier en première ligne suivi du bloc de code dans ```).
"""

# Fonction pour extraire le bloc de code corrigé
def extract_code_blocks(text):
    pattern = r'^\s*([\w./-]+\.\w+)\s*\n```(?:\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
    return [(file_path.strip(), code.strip()) for file_path, code in matches]

# Fichiers attendus (frontend React/Electron)
expected_files = [
    "frontend/package.json",
    "frontend/tailwind.config.js",
    "frontend/postcss.config.js",
    "frontend/vite.config.js", 
    "frontend/public/index.html",
    "frontend/electron/main.js",
    "frontend/src/index.jsx",
    "frontend/src/App.jsx",
    "frontend/src/components/Navbar.jsx",
    "frontend/src/pages/Dashboard.jsx",
    "frontend/src/pages/Mods.jsx",
    "frontend/src/pages/Automation.jsx",
    "frontend/src/pages/Logs.jsx",
    "frontend/src/pages/Settings.jsx",
    "frontend/src/services/api.js",
    "frontend/src/store/index.js",
    "frontend/src/utils/helpers.js"
]


# Boucle fichier par fichier
iteration = 1
for file_path in expected_files:
    print(f"\n--- Itération {iteration} ---")
    print(f"Fichier à traiter : {file_path}")

    full_path = os.path.join(output_dir, file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    if os.path.exists(full_path):
        # Lire le contenu du fichier existant
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Préparer le prompt pour correction
        file_ext = file_path.split('.')[-1]
        user_prompt = f"""
Corrige et optimise le fichier frontend React/Electron suivant : `{file_path}`.

Voici son contenu actuel :

```{file_ext}
{content}
```

Consignes :
- Ne modifie pas la structure globale du fichier.
- Optimise et améliore si nécessaire (lisibilité, performance, bonnes pratiques).
- Fournis uniquement le code corrigé dans le format suivant :

{file_path}
```{file_ext}
<code corrigé ici>
```
"""
    else:
        # Préparer le prompt pour génération complète
        file_ext = file_path.split('.')[-1]
        user_prompt = f"""
Le fichier `{file_path}` est manquant dans le projet frontend React/Electron.
Génère ce fichier entièrement en respectant la structure du projet, les conventions React/Electron et les meilleures pratiques actuelles.

Fournis uniquement le code généré dans le format suivant :

{file_path}
```{file_ext}
<code généré ici>
```
"""

    # Appel à Claude
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=4000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    output = response.content[0].text
    print("Réponse de Claude :\n", output)

    # Extraire le fichier corrigé ou généré
    files = extract_code_blocks(output)
    corrected_files = [f for f in files if f[0] == file_path]

    if not corrected_files:
        print(f"Aucune modification détectée pour {file_path}, le fichier reste inchangé.")
    else:
        # Écrire la version corrigée ou générée
        _, corrected_code = corrected_files[0]
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(corrected_code)
        print(f"Fichier mis à jour : {full_path}")

    iteration += 1

print("\n✅ Revue et génération des fichiers frontend terminée !")
