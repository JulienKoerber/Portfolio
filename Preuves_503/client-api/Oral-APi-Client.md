# Oral API Client — Plan de présentation (15 min)

## Objectif
- Présenter clairement l'API Client (authentification & utilisateurs)
- Expliquer les choix techniques et l'intégration avec les autres services
- Montrer la sécurité, le déploiement, la fiabilité et une mini démo
- Conclure par les compétences acquises (AC DevCloud)

## Agenda (15 min)
- 0:00–0:30 Pitch rapide
- 0:30–2:00 Contexte projet & rôle de l'API Client
- 2:00–5:30 Architecture, modèle de données, sécurité
- 5:30–8:00 Endpoints clés + mini démo
- 8:00–11:00 Déploiement & infrastructure (Docker, K8s, Vagrant/Ansible)
- 11:00–13:00 Fiabilité, observabilité, décisions
- 13:00–15:00 Compétences acquises + Q&A rapide

## Pitch (30 secondes)
- "L'API Client est le service d'authentification central de notre e‑commerce. Elle gère l'inscription, la connexion, les profils et les rôles, avec JWT et bcrypt. Elle est stateless, sécurisée, et déployée sur Kubernetes en environnement virtualisé automatisé via Vagrant + Ansible."

## Contexte du projet
- Architecture microservices: Catalogue, Panier, Commandes, Client + Frontend
- Chaque service a sa propre base (isolation des données)
- Le Frontend parle à toutes les APIs en REST; les autres APIs valident le JWT émis par l'API Client

## Rôle de l'API Client
- Authentification (génère/valide JWT), gestion des utilisateurs, rôles
- Service stateless: pas de sessions serveur, facile à scaler
- Point unique de vérité pour l'identité des utilisateurs

## Stack technique
- Backend: FastAPI 0.104.1 (+ Swagger / ReDoc)
- BDD: PostgreSQL + SQLAlchemy 2.x, psycopg2-binary
- Sécurité: JWT (python-jose, HS256, exp 30 min), bcrypt
- Validation: Pydantic 2.x
- Serveur: Uvicorn 0.24.0

## Architecture & code
- Fichiers: `main.py`, `auth.py`, `models.py`, `schemas.py`, `database.py`, `routes/users.py`
- Flux: Client → Router → Middleware Auth → Business Logic → Database
- Dépendance clé: `get_current_user()` protège les routes

## Modèle de données (table `users`)
- `id` (PK), `email` (UNIQUE, NOT NULL), `password` (hashé bcrypt), `username` (UNIQUE, optionnel), `role` (DEFAULT "user")
- Schémas Pydantic: `UserCreate`, `UserLogin`, `UserUpdate`, `UserResponse` (sans mot de passe)

## Sécurité (JWT + bcrypt)
- JWT: HS256, expiration 30 min, secret via `JWT_SECRET_KEY`
- Payload: `sub` (username), `role`, `user_id`, `exp`
- Bcrypt: salt automatique, mot de passe jamais stocké ni renvoyé
- Headers: `Authorization: Bearer <token>`

## Endpoints essentiels
| Méthode | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | /users/register | Non | Inscription d'un user |
| POST | /users/login | Non | Connexion → JWT + profil |
| GET | /users/me | Oui | Profil du user connecté |
| GET | /users/ | (Selon besoin) | Liste des users |
| GET | /users/{id} | (Selon besoin) | Détails d'un user |
| PUT | /users/{id} | (Selon besoin) | Modifier un user |
| DELETE | /users/{id} | (Selon besoin) | Supprimer un user |
| GET | /health | Non | Statut de l'API |

## Mini démo (2–3 minutes)
- Objectif: montrer login → token → accès protégé

```bash
# 1) Inscription (exemple)
curl -X POST http://<node-ip>:30082/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepassword123","username":"john_doe"}'

# 2) Connexion → récupère le token
curl -X POST http://<node-ip>:30082/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepassword123"}'
# → Copier la valeur de access_token

# 3) Profil protégé
TOKEN="ey..."  # remplacer par le token renvoyé
curl http://<node-ip>:30082/users/me -H "Authorization: Bearer $TOKEN"

# 4) Health check
curl http://<node-ip>:30082/health
```

> Remarque: en local (Uvicorn), remplacer par `http://localhost:8000`.

## Déploiement & infrastructure
- Docker: image via `Dockerfile` (Python 3.11, `requirements.txt`)
- Kubernetes:
  - Deployment API Client: requests/limits CPU/RAM, `readinessProbe` & `livenessProbe` sur `/health`
  - Service NodePort (30082) pour tests; DB en `ClusterIP`
  - PostgreSQL avec PV/PVC 2 Go
  - Secrets K8s: `DB_PASSWORD`, `JWT_SECRET_KEY`
- Vagrant + Ansible:
  - 3 VMs Debian 12: master + 2 workers
  - `vagrant up` → provisioning automatique (Docker, kubeadm, CNI, déploiements)

## Fiabilité & observabilité
- Endpoint `/health` + probes K8s (readiness/liveness)
- Retry DB au démarrage (attend que PostgreSQL soit prêt)
- Limites de ressources pour éviter qu'un pod consomme tout
- Logs via `kubectl logs` et tests via Swagger

## Choix techniques & justifications
- JWT stateless: plus simple à scaler que des sessions
- Rôles dans le token: évite une requête DB pour chaque vérification
- Secrets K8s: pas de credentials en clair dans le code
- NodePort pour tests (en prod → Ingress + TLS)

## Limites & améliorations possibles
- Pas de refresh tokens (à ajouter pour UX longue durée)
- Rate limiting sur `/login` et `/register`
- Vérification email + politique de mot de passe fort
- RBAC plus granulaire si les rôles évoluent

## Questions fréquentes (Q&A rapide)
- Pourquoi JWT plutôt que sessions ? → Stateless, scalable, simple en microservices
- Comment protégez-vous les mots de passe ? → Bcrypt avec salt, jamais renvoyés
- Que se passe-t-il si la DB démarre en retard ? → Retry, probes, pas de trafic avant readiness
- Où sont stockés les secrets ? → Secrets Kubernetes
- Comment les autres APIs valident l'utilisateur ? → Elles vérifient la signature JWT, sans appeler l'API Client

## Compétences acquises (AC DevCloud)
- **AC34.01**: Conception + supervision d'un cluster (probes, health, logs)
- **AC34.02**: Orchestration K8s (Deployments, Services, PV/PVC, Secrets)
- **AC34.03**: Investigation incidents (retry, probes, limits)
- **AC35.02**: Microservice sécurisé (JWT, bcrypt, CORS, validation)
- **AC35.03**: Infra as Code (Vagrant, Ansible, YAML K8s, Docker)

## Compétences personnelles — "J'ai appris"
- J'ai appris à concevoir et déployer une API stateless avec FastAPI, à la documenter et la tester proprement.
- J'ai appris à sécuriser une appli côté serveur: JWT (HS256, expiration), bcrypt, CORS et validation Pydantic.
- J'ai appris à utiliser Kubernetes au quotidien: Deployments, Services (NodePort/ClusterIP), PV/PVC, probes.
- J'ai appris à automatiser une infra complète avec Vagrant et Ansible, et à gérer les secrets via Kubernetes.
- J'ai appris à diagnostiquer des incidents (logs, readiness/liveness, retry DB) et à améliorer la fiabilité.
- J'ai appris à structurer les données avec SQLAlchemy et à poser des contraintes utiles (UNIQUE, NOT NULL).
- J'ai appris à raisonner scalabilité: stateless, rôles dans le token pour éviter des requêtes inutiles.
- J'ai appris à présenter et justifier des choix techniques simplement (pour un public non expert).

## Conclusion
- Projet très formateur: sécurité appliquée, K8s réel, automatisation
- L'API Client est centrale: fiabilité et sécurité prioritaires
- J'ai gagné en confiance sur les microservices et l'Infra as Code
