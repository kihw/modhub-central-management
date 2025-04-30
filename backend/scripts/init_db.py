import sys
import os

# Ajouter le chemin du projet au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import manual_db_init

def main():
    print("Initializing database...")
    manual_db_init()
    print("Database initialization complete.")

if __name__ == "__main__":
    main()