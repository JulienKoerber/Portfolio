# Schémas de validation
from pydantic import BaseModel

# Données pour créer un user
class UserCreate(BaseModel):
    email: str
    password: str
    username: str | None = None
    role: str = "user"

# Données pour la connexion
class UserLogin(BaseModel):
    email: str
    password: str

# Données pour mettre à jour un user
class UserUpdate(BaseModel):
    email: str | None = None
    password: str | None = None
    username: str | None = None
    role: str | None = None

# Données retournées (sans password)
class UserResponse(BaseModel):
    id: int
    email: str
    username: str | None = None
    role: str | None = None
    
    class Config:
        from_attributes = True  # Permet de lire les objets SQLAlchemy
