# Modèle de la table users
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"  # Nom de la table

    id = Column(Integer, primary_key=True) # Clé primaire
    email = Column(String, unique=True, nullable=False) # Email
    password = Column(String, nullable=False) # Mot de passe
    username = Column(String, unique=True, nullable=True) # Nom d'utilisateur (optionnel)
    role = Column(String, default="user", nullable=True) # Rôle du client (par défaut "user")