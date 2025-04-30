# scripts/create_initial_mods.py
import sys
import os

# Ajouter le chemin du projet au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from db.models import Mod, User
from sqlalchemy.orm import Session

def create_initial_mods(db: Session):
    # Vérifiez d'abord s'il existe un utilisateur
    user = db.query(User).first()
    if not user:
        print("Aucun utilisateur trouvé. Créez un utilisateur d'abord.")
        return

    # Créez des mods initiaux
    mods_data = [
        {
            "user_id": user.id,
            "name": "Gaming Mod",
            "type": "gaming",
            "description": "Optimise les paramètres pour le gaming",
            "is_active": False,
            "priority": 5,
            "config": {}
        },
        {
            "user_id": user.id,
            "name": "Night Mod",
            "type": "night",
            "description": "Mode nuit avec luminosité réduite",
            "is_active": False,
            "priority": 5,
            "config": {}
        }
    ]

    for mod_data in mods_data:
        existing_mod = db.query(Mod).filter_by(name=mod_data['name']).first()
        if not existing_mod:
            new_mod = Mod(**mod_data)
            db.add(new_mod)
    
    db.commit()
    print("Mods initiaux créés avec succès.")

def main():
    db = SessionLocal()
    try:
        create_initial_mods(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()