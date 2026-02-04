# Point d'entrée de l'API
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import users
import os

# Créer les tables automatiquement au démarrage
Base.metadata.create_all(bind=engine)

# Initialiser l'application
app = FastAPI(title="API Clients")

# Configuration CORS
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://frontend-service.ecommerce.svc.cluster.local:80")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("/{full_path:path}")
def preflight(full_path: str):
    return Response(status_code=200, headers={
        "Access-Control-Allow-Origin": FRONTEND_ORIGIN,
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Authorization,Content-Type",
        "Access-Control-Allow-Credentials": "true",
    })

@app.middleware("http")
async def ensure_cors_header(request: Request, call_next):
    response = await call_next(request)
    if "Access-Control-Allow-Origin" not in response.headers:
        response.headers["Access-Control-Allow-Origin"] = FRONTEND_ORIGIN
    return response

# Ajouter les routes utilisateurs
app.include_router(users.router)

@app.get("/")
def home():
    return {"message": "API Clients operationnelle"}

@app.get("/health")
def health():
    return {"status": "ok"}
