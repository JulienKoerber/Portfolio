# API Clients

Service de gestion des utilisateurs et de l'authentification.

## Technologies
- Python 3.11
- FastAPI
- PostgreSQL
- JWT (JSON Web Tokens)
- BCrypt

## Fonctionnalites
- Inscription des utilisateurs
- Connexion (generation de token JWT)
- Gestion du profil utilisateur
- Verification des tokens

## Configuration
Variables d'environnement requises :
- DB_HOST : Hote de la base de donnees (defaut: client-db)
- DB_USER : Utilisateur de la base de donnees
- DB_PASSWORD : Mot de passe de la base de donnees
- DB_NAME : Nom de la base de donnees (defaut: client)
- JWT_SECRET_KEY : Cle secrete pour la signature des tokens

## Installation Locale
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Endpoints API & Exemples Curl

### 1. Inscription (Register)
Crée un nouveau compte utilisateur.

```bash
curl -X 'POST' \
  'http://192.168.56.10:30080/client/users/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123",
  "role": "client"
}'
```

### 2. Connexion (Login)
Authentifie un utilisateur et retourne un token JWT.

```bash
curl -X 'POST' \
  'http://192.168.56.10:30080/client/users/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "john@example.com",
  "password": "securepassword123"
}'
```
*Réponse attendue :*
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": { ... }
}
```

### 3. Profil Utilisateur (Me)
Récupère les informations de l'utilisateur connecté (nécessite le token).

```bash
# Remplacez <TOKEN> par le token reçu au login
curl -X 'GET' \
  'http://192.168.56.10:30080/client/users/me' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <TOKEN>'
```

### 4. Récupérer un utilisateur par ID
(Admin ou utilisateur concerné)

```bash
curl -X 'GET' \
  'http://192.168.56.10:30080/client/users/1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <TOKEN>'
```
