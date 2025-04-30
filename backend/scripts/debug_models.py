# scripts/debug_models.py
import sys
import os

# Ajouter le chemin du projet au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import configure_mappers
from db.models import Base, Mod, User
from db.database import engine

def debug_models():
    try:
        # Configurez explicitement les mappeurs
        configure_mappers()
        
        # Vérifiez les métadonnées
        print("Tables dans les métadonnées:")
        for table in Base.metadata.tables:
            print(f"- {table}")
        
        # Inspectez le modèle Mod
        mod_mapper = Mod.__mapper__
        print("\nRelations du modèle Mod:")
        for rel in mod_mapper.relationships:
            print(f"- {rel.key}: {rel}")
        
        print("\nColonnes du modèle Mod:")
        for col in mod_mapper.columns:
            print(f"- {col.key}")
    
    except Exception as e:
        print(f"Erreur lors du débogage des modèles : {e}")

def main():
    debug_models()

if __name__ == "__main__":
    main()