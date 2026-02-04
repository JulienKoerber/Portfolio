# Routes pour gérer les utilisateurs
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserLogin, UserUpdate, UserResponse
from auth import get_password_hash, verify_password, get_current_user, create_access_token

router = APIRouter(prefix="/users", tags=["Users"])

# POST /users/register - Créer un utilisateur (inscription)
@router.post("/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Vérifier si email existe déjà
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    # Hash le password avant de sauvegarder
    hashed_password = get_password_hash(user.password)
    
    # Créer et sauvegarder
    new_user = User(email=user.email, password=hashed_password, username=user.username, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# POST /users/login - Connexion
@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    # Trouver l'utilisateur
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    # Vérifier le password hashé
    if not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    # Créer le token JWT avec username, role et user_id
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }

# GET /users/me - Récupérer l'utilisateur actuel
@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Récupère les informations de l'utilisateur actuellement connecté"""
    user = db.query(User).filter(User.username == current_user["username"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

# GET /users/ - Liste tous les utilisateurs
@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# GET /users/{user_id} - Récupérer un utilisateur par ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

# PUT /users/{user_id} - Modifier un utilisateur
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    # Trouver l'utilisateur
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Mettre à jour les champs fournis
    if user_update.email is not None:
        # Vérifier si le nouvel email existe déjà
        existing = db.query(User).filter(User.email == user_update.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
        user.email = user_update.email
    
    if user_update.password is not None:
        # Hash le nouveau password
        user.password = get_password_hash(user_update.password)
    
    if user_update.username is not None:
        user.username = user_update.username
    
    if user_update.role is not None:
        user.role = user_update.role
    
    db.commit()
    db.refresh(user)
    return user

# DELETE /users/{user_id} - Supprimer un utilisateur
@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    db.delete(user)
    db.commit()
    return None
