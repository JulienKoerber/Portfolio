# Configuration de la base de données
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import os
import time

# Configuration de la connexion
DB_HOST = os.getenv("DB_HOST", "client-db")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "client")
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Connexion à Postgres
engine = create_engine(DATABASE_URL)

# Fabrique de sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour les modèles
Base = declarative_base()

# Wait for database to be ready
for i in range(30):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database is ready!")
        break
    except OperationalError as e:
        print(f"Waiting for DB... {i+1}/30")
        time.sleep(2)

# Fonction pour obtenir une session de BDD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
