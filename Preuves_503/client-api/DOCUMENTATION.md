# 📚 Documentation API Client

## 📋 Table des matières
1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Infrastructure](#infrastructure)
4. [Modèle de données](#modèle-de-données)
5. [Authentification & Sécurité](#authentification--sécurité)
6. [Endpoints API](#endpoints-api)
7. [Configuration & Déploiement](#configuration--déploiement)
8. [Dépendances](#dépendances)
9. [Bilan de compétences](#bilan-de-compétences)

---

## 🎯 Vue d'ensemble

### Introduction

L'API Client est un microservice REST qui gère l'authentification et les utilisateurs de notre projet e-commerce. On l'a développée avec FastAPI. C'est le service central pour tout ce qui concerne la connexion et la gestion des comptes utilisateurs. En gros, cette API permet de gérer tous les utilisateurs de manière centralisée pour l'ensemble des microservices de la plateforme.

### Rôle dans l'architecture microservices

Dans notre architecture distribuée, l'API Client a plusieurs rôles importants. Elle stocke toutes les infos sur les utilisateurs (emails, mots de passe, etc.). Elle gère l'authentification en créant et validant des tokens JWT. Elle attribue aussi les rôles (user, admin) pour contrôler les accès. Et elle protège les données sensibles comme les mots de passe avec bcrypt.

On a conçu cette API avec quelques principes clés. Elle est stateless, ce qui veut dire qu'elle n'a pas besoin de garder des sessions en mémoire grâce aux JWT. Ça facilite la scalabilité car on peut lancer plusieurs instances sans problème. L'API est aussi totalement indépendante des autres services, elle communique uniquement via REST. On a aussi fait attention à la sécurité en appliquant les bonnes pratiques (hashage bcrypt, tokens avec expiration, etc.).

### Fonctionnalités principales

L'API Client gère tout le cycle de vie des utilisateurs. Les utilisateurs peuvent s'inscrire en créant un compte (avec validation des données). Ensuite ils peuvent se connecter et recevoir un token JWT. Une fois connectés, ils peuvent consulter et modifier leur profil. On peut aussi supprimer des comptes si besoin.

Pour l'authentification, on utilise des tokens JWT qui expirent au bout de 30 minutes. Les mots de passe sont hashés avec bcrypt (qui ajoute un salt aléatoire pour chaque mot de passe, donc c'est très sécurisé). On a implémenté OAuth2 Password Bearer pour rester compatible avec les standards modernes. Un middleware vérifie automatiquement les tokens sur toutes les routes protégées.

Le système de rôles est simple et flexible. On a deux rôles de base : "user" et "admin", mais on peut en ajouter d'autres facilement. Le rôle est stocké directement dans le token JWT, donc pas besoin de faire une requête en base pour vérifier les permissions.

L'API offre toutes les opérations CRUD classiques. Create pour l'inscription, Read pour consulter les profils et lister les users, Update pour modifier les infos (email, password, role), et Delete pour supprimer un compte.
### Technologies et stack technique

On a choisi nos technos en fonction des performances, de la sécurité et de la facilité de maintenance. Pour le backend, on utilise FastAPI 0.104.1. C'est un framework Python moderne et rapide. Il génère automatiquement une doc interactive (Swagger UI), ce qui est super pratique pour tester l'API. FastAPI valide aussi les données automatiquement et supporte l'async/await pour de meilleures performances.

Pour stocker les données, on a PostgreSQL comme base de données. On accède à la BDD avec SQLAlchemy 2.0.23, un ORM qui facilite la manipulation des données (on manipule des objets Python au lieu d'écrire du SQL). Le driver psycopg2-binary 2.9.9 fait la connexion avec PostgreSQL.

Pour la sécurité, on a deux libs importantes. Python-jose 3.3.0 gère les JWT avec l'algo HS256 pour signer et valider les tokens. Bcrypt 4.0.1 hash les mots de passe de manière sécurisée (résistant aux attaques par force brute).

Pydantic 2.5.0 valide toutes les données qui entrent dans l'API et sérialise les réponses. Il utilise les type hints Python, donc le code est plus clair.

Enfin, on lance l'API avec Uvicorn 0.24.0, un serveur ASGI très performant. En dév, il reload automatiquement l'app quand on modifie le code, ce qui accélère le développement.

### Cas d'usage typiques

Voici quelques exemples concrets d'utilisation de l'API. Quand un utilisateur s'inscrit, le frontend envoie un POST vers /users/register. L'API vérifie les données, hash le mot de passe, sauvegarde l'user en base, et renvoie ses infos (sans le mot de passe bien sûr).

Pour la connexion, l'user envoie ses identifiants en POST vers /users/login. L'API compare le mot de passe avec le hash en base. Si c'est bon, elle génère un token JWT avec les infos de l'user et renvoie le token + les infos du profil.

Quand un utilisateur veut accéder à son profil (GET /users/me), il doit mettre le token JWT dans le header Authorization. L'API vérifie le token, sa signature et son expiration. Si tout est OK, elle renvoie les données demandées.

Pour modifier son profil, l'user envoie un PUT vers /users/{id} avec le token. L'API vérifie le token, check les permissions, met à jour la BDD et renvoie le profil mis à jour.

### Avantages de l'approche choisie

Notre architecture a plusieurs avantages. Toute la logique d'authentification est isolée dans un service dédié, donc c'est plus facile à maintenir. Tous les autres microservices peuvent valider les tokens JWT émis par cette API, on évite de dupliquer du code. Les perfs sont bonnes grâce aux JWT : pas besoin de requête en base à chaque appel pour vérifier l'authentification. La sécu est centralisée en un point, donc c'est plus simple à auditer et mettre à jour. Et le code reste focalisé sur un seul domaine, donc c'est plus facile à comprendre et faire évoluer.

### Intégration avec l'écosystème

L'API Client s'intègre avec tous les autres services du projet. Le frontend (React/Vue) utilise cette API pour l'inscription, la connexion et la gestion de profil. L'API Catalogue vérifie les tokens JWT pour autoriser la gestion des produits (seuls les admins peuvent ajouter/modifier des produits). L'API Panier utilise les infos du token pour associer un panier au bon utilisateur. L'API Commandes authentifie les users avant de leur permettre de créer ou consulter leurs commandes. Au niveau infrastructure, l'API est déployée en pod dans notre cluster Kubernetes avec le service discovery et le load balancing.

---

## 🏗️ Architecture

### Structure du projet
```
client-api/
├── main.py                 # Point d'entrée de l'application
├── models.py               # Modèles SQLAlchemy (base de données)
├── schemas.py              # Schémas Pydantic (validation)
├── auth.py                 # Logique d'authentification JWT
├── database.py             # Configuration base de données
├── routes/
│   ├── __init__.py
│   └── users.py            # Routes utilisateurs
├── requirements.txt        # Dépendances Python
├── Dockerfile              # Image Docker
└── README.md               # Documentation
```

### Flux de données

```
Client → FastAPI Router → Auth Middleware → Business Logic → Database
                              ↓
                         JWT Validation
                              ↓
                      get_current_user()
```

---

## 🏢 Infrastructure

### Schéma de l'infrastructure globale

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         CLUSTER KUBERNETES (3 VMs)                           │
│                                                                              │
│  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐               │
│  │  k8s-master │       │ k8s-worker-1│       │ k8s-worker-2│               │
│  │ 192.168.56.10│       │192.168.56.11│       │192.168.56.12│               │
│  │  6 CPU, 4GB  │       │  4 CPU, 2GB │       │  4 CPU, 2GB │               │
│  └──────┬──────┘       └──────┬──────┘       └──────┬──────┘               │
│         │                     │                      │                      │
│         └─────────────────────┴──────────────────────┘                      │
│                               │                                             │
│         ┌─────────────────────┴─────────────────────┐                       │
│         │        Namespace: ecommerce               │                       │
│         │                                           │                       │
│    ┌────┴─────────────────────────────────┐         │                       │
│    │         Frontend (React)             │         │                       │
│    │           Port: 80                   │         │                       │
│    └────┬─────────┬──────────┬────────┬──┘         │                       │
│         │         │          │        │            │                       │
│         │ (JWT)   │ (JWT)    │ (JWT)  │ (JWT)      │                       │
│         ▼         ▼          ▼        ▼            │                       │
│    ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌──────────────┐                  │
│    │ API     │ │Catalogue │ │ Panier  │ │  Commandes   │                  │
│    │ CLIENT ★│ │   API    │ │  API    │ │     API      │                  │
│    │         │ │          │ │         │ │              │                  │
│    │  Auth & │ │ Produits │ │ Paniers │ │  Commandes   │                  │
│    │  Users  │ │          │ │         │ │              │                  │
│    │         │ │          │ │         │ │              │                  │
│    │  30082  │ │  30081   │ │  30083  │ │    30084     │                  │
│    └────┬────┘ └────┬─────┘ └────┬────┘ └──────┬───────┘                  │
│         │           │            │              │                          │
│         │           │            │              │                          │
│    ┌────▼────┐ ┌────▼─────┐ ┌───▼──────┐ ┌─────▼────────┐                 │
│    │Client DB│ │Catalogue │ │  Redis   │ │ Commandes DB │                 │
│    │         │ │    DB    │ │          │ │              │                 │
│    │PostgreSQL│ │PostgreSQL│ │ Cache    │ │  PostgreSQL  │                 │
│    │ PV: 2Go │ │ PV: 2Go  │ │ In-Memory│ │  PV: 2Go     │                 │
│    └─────────┘ └──────────┘ └──────────┘ └──────────────┘                 │
│                                                                             │
│  Flux d'authentification:                                                 │
│  1. Frontend → POST /login → API Client                                    │
│  2. API Client renvoie le token JWT au Frontend                            │
│  3. Frontend stocke le token (localStorage)                                │
│  4. Frontend envoie le token dans les headers vers toutes les autres APIs  │
│  5. Chaque API vérifie la signature JWT de manière indépendante            │
│                                                                             │
│  Secrets Kubernetes (namespace ecommerce):                                 │
│  - DB_PASSWORD (pour toutes les BDD PostgreSQL)                            │
│  - JWT_SECRET_KEY (partagée par toutes les APIs pour valider les tokens)   │
│                                                                             │
└──────────────────────────────────────────────────────────────────────────────┘

         Vagrant + Ansible : Automatisation complète du déploiement
```

### Zoom sur l'API Client

```
┌────────────────────────────────────────────────────────────────────────┐
│                          API CLIENT (Port 30082)                       │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                    main.py (FastAPI App)                         │ │
│  │                                                                  │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐ │ │
│  │  │   Routes   │  │    Auth    │  │  Schemas   │  │  Models   │ │ │
│  │  │            │  │            │  │            │  │           │ │ │
│  │  │ /register  │  │    JWT     │  │ Pydantic   │  │SQLAlchemy │ │ │
│  │  │ /login     │  │  bcrypt    │  │ Validation │  │   ORM     │ │ │
│  │  │ /users/me  │  │  OAuth2    │  │            │  │           │ │ │
│  │  │ /users/    │  │get_current │  │UserCreate  │  │   User    │ │ │
│  │  │ /users/{id}│  │   _user()  │  │UserLogin   │  │  Table    │ │ │
│  │  │            │  │            │  │UserResponse│  │           │ │ │
│  │  └──────┬─────┘  └─────┬──────┘  └────────────┘  └─────┬─────┘ │ │
│  │         │              │                                │       │ │
│  │         └──────────────┴────────────────────────────────┘       │ │
│  │                              │                                  │ │
│  └──────────────────────────────┼──────────────────────────────────┘ │
│                                 │                                    │
│                         ┌───────▼────────┐                           │
│                         │  database.py   │                           │
│                         │                │                           │
│                         │ SQLAlchemy     │                           │
│                         │ Connection     │                           │
│                         │ Management     │                           │
│                         └───────┬────────┘                           │
│                                 │                                    │
│                         ┌───────▼─────────────────────────┐          │
│                         │  PostgreSQL Database (client)   │          │
│                         │                                 │          │
│                         │  Table: users                   │          │
│                         │  ┌────────────────────────────┐ │          │
│                         │  │ id (PK)                    │ │          │
│                         │  │ email (UNIQUE, NOT NULL)   │ │          │
│                         │  │ password (hashed, bcrypt)  │ │          │
│                         │  │ username (UNIQUE)          │ │          │
│                         │  │ role (DEFAULT "user")      │ │          │
│                         │  └────────────────────────────┘ │          │
│                         │                                 │          │
│                         │  PersistentVolume: 2 Go         │          │
│                         │  Service: client-db (ClusterIP) │          │
│                         └─────────────────────────────────┘          │
│                                                                      │
│  Variables d'environnement (depuis Secrets K8s):                    │
│  ├─ DB_HOST=client-db                                               │
│  ├─ DB_USER=user                                                    │
│  ├─ DB_PASSWORD=********** (secret)                                 │
│  ├─ DB_NAME=client                                                  │
│  ├─ JWT_SECRET_KEY=********** (secret)                              │
│  └─ FRONTEND_ORIGIN=http://frontend-service...                      │
│                                                                      │
│  Ressources Pod:                                                    │
│  ├─ Requests: 100m CPU, 128Mi RAM                                   │
│  ├─ Limits: 500m CPU, 512Mi RAM                                     │
│  ├─ ReadinessProbe: /health (5s interval)                           │
│  └─ LivenessProbe: /health (redémarrage auto)                       │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

Flux d'authentification:
1. Client → POST /login → API Client
2. API Client → Vérification bcrypt → PostgreSQL
3. API Client → Génération JWT → Client
4. Client → GET /users/me (avec token) → API Client
5. API Client → Validation JWT → get_current_user()
6. API Client → Requête BDD → Réponse
```

### Architecture générale du projet

Notre projet e-commerce utilise une architecture microservices avec quatre services principaux : l'API Catalogue (gestion des produits), l'API Client (authentification et utilisateurs), l'API Panier (gestion des paniers), et l'API Commandes (traitement des commandes). Chaque microservice a sa propre base PostgreSQL, donc les données sont bien séparées. Le frontend communique avec tous ces services en REST.

### Infrastructure virtualisée avec Vagrant

La virtualisation est super importante dans notre projet. On a choisi Vagrant pour créer et gérer nos environnements virtualisés. C'est un outil qui automatise tout et qui rend notre infra reproductible.

#### Pourquoi la virtualisation ?

La virtualisation nous apporte plusieurs avantages. D'abord, ça isole complètement notre environnement de dév de notre machine perso, donc pas de conflits de dépendances. Ensuite, tous les membres de l'équipe ont exactement le même environnement, que ce soit sur Windows, macOS ou Linux. Ça garantit que si ça marche chez moi, ça marchera chez les autres. En plus, on peut simuler toute une infrastructure distribuée (plusieurs machines) sur un seul PC, ce qui facilite les tests avant de déployer en vrai.

#### Architecture des machines virtuelles

On a créé trois VMs sous Debian 12 pour simuler un vrai cluster Kubernetes.

La première VM s'appelle **k8s-master** (IP : 192.168.56.10). C'est le Control Plane du cluster Kubernetes. On lui a donné 6 vCPUs et 4 Go de RAM pour qu'elle puisse bien gérer le cluster. Le Control Plane prend toutes les décisions importantes : où placer les pods, détecter les problèmes, exposer l'API Kubernetes, etc. Cette machine contient aussi des composants essentiels comme etcd (la BDD qui stocke toutes les config du cluster), le scheduler (qui décide où lancer les pods), et le controller manager (qui gère l'état du système).

Les deux autres VMs sont les workers : **k8s-worker-1** (192.168.56.11) et **k8s-worker-2** (192.168.56.12). Elles ont chacune 4 vCPUs et 2 Go de RAM. Ces workers exécutent nos applis (les microservices et leurs BDD). Ils font tourner kubelet (l'agent K8s qui communique avec le master et gère les pods) et kube-proxy (qui gère le réseau entre les pods).

#### Configuration avec le Vagrantfile

Le fichier Vagrantfile (dans infrastructure/) est le cœur de notre config de virtualisation. C'est un fichier en Ruby qui définit toute notre infra.

Le Vagrantfile détecte automatiquement l'archi du proc (x86_64 ou ARM64) et choisit la bonne box Debian. Ça marche donc sur tous les types de machines, même les nouveaux Mac avec processeurs Apple Silicon.

Pour chaque VM, le fichier définit : le nom (hostname), l'IP sur le réseau privé, et les ressources (CPU/RAM). Le réseau privé 192.168.56.0/24 permet aux VMs de communiquer entre elles tout en restant isolées de l'extérieur. Un truc important : le dossier synchronisé (synced_folder) monte le répertoire du projet dans /vagrant sur les VMs. Du coup, on peut coder sur notre machine avec VSCode ou autre, et les changements sont instantanément visibles dans les VMs.

#### Automatisation du provisioning

Un truc puissant dans notre config Vagrant, c'est l'intégration avec Ansible pour tout automatiser. Le Vagrantfile lance automatiquement le playbook Ansible (infrastructure/ansible/setup.yml) quand on crée les VMs ou quand on fait `vagrant provision`.

En gros, un simple `vagrant up` suffit pour passer de rien à un cluster Kubernetes complet avec toutes nos applis déployées. Vagrant crée les trois VMs en parallèle, configure le réseau, puis lance Ansible qui installe et configure tout. Ça élimine les erreurs manuelles et garantit que tout le monde a exactement la même infra.

Le playbook Ansible fait : mise à jour du système, installation de Docker (pour faire tourner les conteneurs), installation de Kubernetes (kubelet, kubeadm, kubectl). Ensuite il initialise le cluster K8s sur le master avec `kubeadm init`. Cette commande génère un token que les workers utilisent pour rejoindre le cluster. Le playbook configure aussi le réseau CNI (pour que les pods communiquent entre eux) et déploie tous nos microservices.

#### Cycle de vie des VMs

Vagrant simplifie la gestion de notre infra avec quelques commandes :

- `vagrant up` : démarre toutes les VMs et fait le provisioning. Si les VMs existent déjà, il les démarre juste sans refaire l'install.
- `vagrant ssh master` ou `vagrant ssh worker1` : connexion SSH à une VM pour l'admin ou le debug.
- `vagrant halt` : arrête proprement toutes les VMs et libère les ressources de notre PC.
- `vagrant destroy` : supprime complètement les VMs, utile pour repartir de zéro.
- `vagrant provision` : relance juste le playbook Ansible sans recréer les VMs. Super pratique pour tester des modifs de config rapidement.

### Orchestration Kubernetes

Une fois l'infra virtualisée en place, Kubernetes orchestre toutes nos applis conteneurisées. Tout est déployé dans un namespace "ecommerce" pour bien isoler nos ressources. Chaque microservice a son Deployment K8s qui définit combien de replicas on veut, les ressources allouées (CPU/RAM), et les health checks. Les Services (NodePort ou ClusterIP) exposent les applis et font l'équilibrage de charge. Pour les données, chaque BDD PostgreSQL a son PersistentVolume de 2 Go. Les infos sensibles (mots de passe, clés JWT) sont stockées dans des Secrets Kubernetes.

### Infrastructure spécifique de l'API Client

L'API Client a son infra définie dans le fichier client.yaml. Le Deployment configure un conteneur avec des ressources limitées : 100m CPU et 128Mi RAM au minimum, 500m CPU et 512Mi RAM au max. Ça évite qu'un conteneur défaillant bouffe toutes les ressources.

Deux probes surveillent l'appli. La readinessProbe check l'endpoint /health toutes les 5 secondes pour savoir si l'API est prête à recevoir du trafic. La livenessProbe redémarre automatiquement le conteneur si l'app plante. Les variables d'environnement (DB_HOST, DB_USER, etc.) configurent la connexion à la BDD. Les infos sensibles (DB_PASSWORD, JWT_SECRET_KEY) viennent des Secrets K8s.

Le Service de type NodePort expose l'API sur le port 30082, donc on peut y accéder depuis l'extérieur du cluster pour tester. La BDD PostgreSQL tourne dans un pod séparé avec un Service ClusterIP (accessible que depuis le cluster, donc sécurisé). Elle a un PersistentVolume de 2 Go pour garder les données des users. L'image Docker est construite localement depuis le Dockerfile (Python 3.11) et déployée automatiquement par Ansible.

---

## 💾 Modèle de données

### Table `users`

| Colonne    | Type    | Contraintes          | Description                   |
|------------|---------|----------------------|--------------------------------|
| `id`       | Integer | PRIMARY KEY          | Identifiant unique             |
| `email`    | String  | UNIQUE, NOT NULL     | Adresse email (login)          |
| `password` | String  | NOT NULL             | Mot de passe hashé (bcrypt)    |
| `username` | String  | UNIQUE, NULLABLE     | Nom d'utilisateur (optionnel)  |
| `role`     | String  | DEFAULT "user"       | Rôle de l'utilisateur          |

### Schémas Pydantic

#### `UserCreate` - Inscription
```python
{
    "email": "user@example.com",
    "password": "securepassword123",
    "username": "john_doe",
    "role": "user"
}
```

#### `UserLogin` - Connexion
```python
{
    "email": "user@example.com",
    "password": "securepassword123"
}
```

#### `UserUpdate` - Mise à jour
```python
{
    "email": "newemail@example.com",
    "password": "newpassword123",
    "username": "new_username",
    "role": "admin"
}
```

#### `UserResponse` - Réponse (sans password)

Le schéma `UserResponse` définit les données qu'on renvoie au client quand il consulte des infos utilisateur. C'est une classe Pydantic qui filtre les données sensibles. **Le point crucial : le mot de passe n'est jamais inclus dans les réponses**. C'est une règle de sécurité de base, on ne renvoie jamais le hash du mot de passe au client, même s'il est hashé.

Ce schéma est utilisé pour toutes les réponses qui retournent des infos utilisateur : après inscription, après connexion, consultation de profil, liste des users, etc.

**Champs retournés :**
- `id` : Identifiant unique de l'utilisateur (généré automatiquement)
- `email` : Adresse email de l'utilisateur
- `username` : Nom d'utilisateur (peut être null si non défini)
- `role` : Rôle de l'utilisateur ("user", "admin", etc.)

**Exemple de données JSON :**
```python
{
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe",
    "role": "user"
}
```

---

## 🔐 Authentification & Sécurité

La sécurité est un point crucial pour notre API qui gère des utilisateurs et des mots de passe. On a mis en place plusieurs mécanismes pour protéger les données et garantir que seuls les utilisateurs autorisés peuvent accéder aux ressources qui les concernes. Je vais expliquer comment fonctionne l'authentification par JWT et comment on sécurise les mots de passe avec bcrypt.

### Système JWT (Json Web Token)

Un JWT, c'est un token encodé en trois parties séparées par des points : le header, le payload, et la signature. Notre API crée un token quand l'utilisateur se connecte, et ensuite le client le renvoie dans le header `Authorization` à chaque requête.

Les tokens ont une durée de validité de 30 minutes. Une fois que ce délais est passé, le token expire et l'utilisateur doit se reconnecter. C'est un bon compromis entre sécurité et le fait que le client n'ai pas besoin de se reconnecter toutes les 5 minutes.

Le payload du token contient plusieurs informations importantes : le username de l'utilisateur (dans le champ `sub`), son rôle (`user` ou `admin`), son ID en base de données, et le timestamp d'expiration. Quand l'API reçoit une requête avec un token, elle vérifie d'abord la signature pour s'assurer que personne n'a modifié le token, puis elle check l'expiration pour voir si le token est encore valide.

### Configuration JWT de notre API

Notre API utilise l'algorithme **HS256** pour signer les tokens. C'est un algo symétrique, ce qui veut dire qu'on utilise la même clé pour créer et vérifier les tokens. Cette clé secrète est stockée dans la variable d'environnement `JWT_SECRET_KEY`. **Important** : il faut absolument que cette clé reste secrète et soit différente en prod et en dev.

Les tokens ont une **durée de validité de 30 minutes**. Passé ce délai, le token expire et l'user doit se reconnecter. C'est un bon compromis entre sécu (si quelqu'un vole le token, il ne reste valide que 30 minutes) et UX (l'user n'a pas besoin de se reconnecter toutes les 5 minutes). Si on voulait améliorer ça, on pourrait ajouter des refresh tokens pour prolonger la session sans redemander le mot de passe.

### Contenu du token JWT

Voici ce qu'on met dans le payload du token :

```json
{
    "sub": "john_doe",          // Le username (subject du token)
    "role": "user",             // Le rôle (user ou admin)
    "user_id": 1,               // L'ID en base de données
    "exp": 1234567890           // Timestamp d'expiration (Unix time)
}
```

Le champ `sub` (subject) contient le username. C'est un champ standard des JWT. Le `role` permet de gérer les permissions : un admin peut faire plus de trucs qu'un user simple. Le `user_id` est pratique pour les autres microservices qui ont besoin de l'ID en BDD. Et `exp` (expiration) est calculé automatiquement : timestamp actuel + 30 minutes.

Quand un utilisateur se connecte, l'API génère ce token et le renvoie au frontend. Ensuite, le frontend stocke le token (généralement dans le localStorage) et l'envoie dans le header de toutes les requêtes suivantes.

### Sécurisation des mots de passe avec Bcrypt

Stocker des mots de passe en clair en base, c'est la pire erreur possible. Si quelqu'un accède à la BDD, il a tous les mots de passe. Du coup, on utilise **bcrypt** pour hasher (transformer) les mots de passe avant de les stocker.

Bcrypt, c'est un algo de hashage conçu spécialement pour les mots de passe. Contrairement à MD5 ou SHA1 qui sont trop rapides (et donc vulnérables aux attaques par force brute), bcrypt est volontairement lent. Il ajoute aussi un **salt** (une valeur aléatoire) à chaque mot de passe avant de le hasher. Du coup, même si deux users ont le même mot de passe, les hash en base seront différents. Ça protège contre les attaques par rainbow tables (des tables précalculées de hash).

#### Comment ça marche en pratique ?

Quand un user s'inscrit ou change son mot de passe, on appelle la fonction `get_password_hash(password)`. Cette fonction utilise bcrypt pour générer un salt aléatoire, hash le mot de passe avec ce salt, et renvoie le hash complet (qui contient le salt). C'est ce hash qu'on stocke en base de données, jamais le mot de passe en clair.

```python
# Exemple simplifié de la fonction
def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
```

Quand l'user se connecte, on compare le mot de passe qu'il envoie avec le hash stocké en base. On utilise la fonction `verify_password(plain_password, hashed_password)`. Bcrypt extrait le salt du hash stocké, hash le mot de passe fourni avec ce même salt, et compare les deux hash. Si c'est identique, le mot de passe est bon.

```python
# Exemple simplifié de la vérification
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
```

Le point super important : **on ne peut jamais "décrypter" un hash bcrypt**. C'est une fonction à sens unique. La seule façon de vérifier un mot de passe, c'est de le hasher avec le même salt et comparer.

### Protection des routes avec les dépendances FastAPI

FastAPI utilise un système de dépendances super pratique pour protéger les routes. On a créé une fonction `get_current_user()` qui fait tout le boulot de vérification du token. Cette fonction récupère le token depuis le header `Authorization`, vérifie la signature avec la clé secrète, check que le token n'a pas expiré, et extrait les infos de l'utilisateur.

Ensuite, pour protéger une route, on ajoute juste `Depends(get_current_user)` dans les paramètres :

```python
@router.get("/me")
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    # Cette route est protégée
    # Si le token est invalide, FastAPI renvoie automatiquement une erreur 401
    # Si le token est valide, current_user contient les infos de l'utilisateur
    return current_user
```

Le système de dépendances de FastAPI exécute `get_current_user()` avant d'entrer dans la fonction de la route. Si le token est invalide ou expiré, l'exécution s'arrête là et une erreur 401 est renvoyée. Si tout est OK, les infos de l'user sont passées à la fonction. C'est super clean et ça évite de dupliquer le code de vérification partout.

### Format du header d'authentification

Pour les routes protégées, le client doit envoyer le token JWT dans le header HTTP `Authorization` avec ce format :

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Le mot `Bearer` indique qu'on utilise un token d'authentification (c'est le standard OAuth2). Ensuite vient le token JWT complet. FastAPI extrait automatiquement ce token grâce au système `OAuth2PasswordBearer` qu'on a configuré dans `auth.py`.

Si le header est absent, mal formaté, ou si le token est invalide/expiré, l'API renvoie une erreur **401 Unauthorized**. Ça indique au client qu'il doit redemander à l'user de se connecter.

### Bonnes pratiques de sécurité implémentées

Voici un résumé des mesures de sécu qu'on a mises en place :

1. **Jamais de mot de passe en clair** : On utilise bcrypt avec salt automatique. Même si quelqu'un accède à la BDD, il ne peut pas récupérer les mots de passe.

2. **Tokens avec expiration** : Les JWT expirent au bout de 30 minutes. Ça limite les dégâts si un token est volé.

3. **Clé secrète en variable d'environnement** : La clé JWT n'est pas dans le code, elle est configurée via `JWT_SECRET_KEY`. Chaque environnement (dev, prod) a sa propre clé.

4. **Mots de passe exclus des réponses** : Le schéma `UserResponse` ne contient jamais le champ `password`. Même le hash n'est jamais renvoyé au client.

5. **CORS configuré** : Seuls les domaines autorisés peuvent appeler l'API depuis un navigateur.

6. **Validation des données** : Pydantic valide toutes les entrées. Ça évite les injections SQL et autres attaques.

### Ce qu'on pourrait améliorer

Pour un environnement de prod, voici ce qu'on devrait ajouter :

- **HTTPS obligatoire** : Les tokens doivent être transmis uniquement en HTTPS, sinon ils peuvent être interceptés.
- **Refresh tokens** : Permettre de prolonger la session sans redemander le mot de passe.
- **Rate limiting** : Limiter le nombre de tentatives de connexion pour bloquer les attaques par force brute.
- **Politique de mot de passe fort** : Imposer une longueur minimale, des caractères spéciaux, etc.
- **Logs de sécurité** : Logger toutes les tentatives de connexion (réussies et échouées) pour détecter les comportements suspects.
- **Révocation de tokens** : Actuellement, si un token est compromis, il reste valide jusqu'à expiration. On pourrait ajouter une blacklist.

---

## 🛣️ Endpoints API

L'API Client expose plusieurs endpoints pour gérer l'authentification et les utilisateurs. Voici un tableau récapitulatif de toutes les routes disponibles :

| Méthode | Endpoint | Authentification | Description | Rôle requis |
|---------|----------|------------------|-------------|-------------|
| `POST` | `/users/register` | ❌ Non | Inscription d'un nouvel utilisateur | - |
| `POST` | `/users/login` | ❌ Non | Connexion et obtention du token JWT | - |
| `GET` | `/users/me` | ✅ Oui | Récupérer son propre profil | User/Admin |
| `GET` | `/users/` | ❌ Non | Lister tous les utilisateurs | - |
| `GET` | `/users/{user_id}` | ❌ Non | Récupérer un utilisateur par son ID | - |
| `PUT` | `/users/{user_id}` | ❌ Non | Modifier un utilisateur | - |
| `DELETE` | `/users/{user_id}` | ❌ Non | Supprimer un utilisateur | - |
| `GET` | `/` | ❌ Non | Page d'accueil de l'API | - |
| `GET` | `/health` | ❌ Non | Vérification de l'état de l'API | - |

### Exemples de requêtes importantes

#### Inscription (`POST /users/register`)
```json
// Request
{
    "email": "user@example.com",
    "password": "securepassword123",
    "username": "john_doe",
    "role": "user"
}

// Response (201 Created)
{
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe",
    "role": "user"
}
```

#### Connexion (`POST /users/login`)
```json
// Request
{
    "email": "user@example.com",
    "password": "securepassword123"
}

// Response (200 OK)
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "user@example.com",
        "role": "user"
    }
}
```

#### Profil utilisateur (`GET /users/me`)
```http
// Headers
Authorization: Bearer <token>

// Response (200 OK)
{
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe",
    "role": "user"
}
```

#### Modification d'un utilisateur (`PUT /users/{user_id}`)
```json
// Request (tous les champs sont optionnels)
{
    "email": "newemail@example.com",
    "password": "newpassword123",
    "username": "new_username",
    "role": "admin"
}

// Response (200 OK)
{
    "id": 1,
    "email": "newemail@example.com",
    "username": "new_username",
    "role": "admin"
}
```

### Codes de réponse HTTP

| Code | Signification | Cas d'usage |
|------|---------------|-------------|
| `200` | OK | Requête réussie (GET, PUT) |
| `201` | Created | Utilisateur créé avec succès (POST /register) |
| `204` | No Content | Utilisateur supprimé avec succès (DELETE) |
| `400` | Bad Request | Données invalides (email déjà utilisé, etc.) |
| `401` | Unauthorized | Token invalide, expiré ou absent |
| `404` | Not Found | Utilisateur non trouvé |

---

## ⚙️ Configuration & Déploiement

### Variables d'environnement

| Variable              | Valeur par défaut                                    | Description                          |
|-----------------------|------------------------------------------------------|--------------------------------------|
| `DB_HOST`             | `client-db`                                          | Hôte de la base de données           |
| `DB_USER`             | `user`                                               | Utilisateur PostgreSQL               |
| `DB_PASSWORD`         | `password`                                           | Mot de passe PostgreSQL              |
| `DB_NAME`             | `client`                                             | Nom de la base de données            |
| `DB_PORT`             | `5432`                                               | Port PostgreSQL                      |
| `JWT_SECRET_KEY`      | `your-secret-key`                                    | Clé secrète pour signer les JWT      |
| `FRONTEND_ORIGIN`     | `http://frontend-service.ecommerce.svc.cluster.local:80` | Origine autorisée pour CORS     |

### Configuration CORS

L'API configure automatiquement CORS pour permettre les requêtes depuis le frontend :

- **Origins autorisées** : Configurable via `FRONTEND_ORIGIN`
- **Méthodes** : GET, POST, PUT, DELETE, OPTIONS
- **Headers** : Authorization, Content-Type
- **Credentials** : Autorisées

### Base de données

#### Connexion automatique
La fonction `get_db()` gère automatiquement :
- Création de sessions
- Fermeture des connexions
- Gestion des transactions

#### Initialisation
Les tables sont créées automatiquement au démarrage via :
```python
Base.metadata.create_all(bind=engine)
```

#### Retry mechanism
L'application attend jusqu'à 30 tentatives (60 secondes) que la base de données soit prête avant de démarrer.

---

## 🐳 Déploiement Docker

### Build de l'image
```bash
docker build -t client-api:latest .
```

### Lancement du conteneur
```bash
docker run -d \
  -p 8000:8000 \
  -e DB_HOST=client-db \
  -e DB_USER=user \
  -e DB_PASSWORD=password \
  -e DB_NAME=client \
  -e JWT_SECRET_KEY=super-secret-key \
  --name client-api \
  client-api:latest
```

### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📦 Dépendances

### Fichier requirements.txt

```
fastapi==0.104.1               # Framework web moderne
uvicorn[standard]==0.24.0      # Serveur ASGI
sqlalchemy==2.0.23             # ORM pour PostgreSQL
psycopg2-binary==2.9.9         # Driver PostgreSQL
pydantic==2.5.0                # Validation de données
bcrypt==4.0.1                  # Hashage de mots de passe
python-jose[cryptography]==3.3.0  # JWT encoding/decoding
```

### Installation
```bash
pip install -r requirements.txt
```

---

## 🧪 Tests & Développement

### Lancement en développement local

```bash
# Installation des dépendances
pip install -r requirements.txt

# Configuration de la base de données
export DB_HOST=localhost
export DB_USER=user
export DB_PASSWORD=password
export DB_NAME=client
export JWT_SECRET_KEY=dev-secret-key

# Lancement du serveur
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Documentation interactive

Une fois l'API lancée, accédez à :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

Ces interfaces permettent de tester tous les endpoints directement depuis le navigateur.

---

## 🔄 Intégration avec les autres microservices

### Communication avec le Frontend
Le frontend consomme cette API pour :
- Gérer l'inscription/connexion
- Stocker le token JWT dans le localStorage
- Envoyer le token dans les headers pour les requêtes authentifiées

### Communication avec les autres APIs
Le token JWT peut être utilisé pour authentifier les requêtes vers :
- **API Catalogue** : Récupération des produits
- **API Panier** : Gestion du panier (requiert user_id du token)
- **API Commandes** : Création de commandes (requiert user_id du token)

---

## 🛡️ Sécurité - Bonnes pratiques

### ✅ Implémenté
- ✅ Hashage bcrypt des mots de passe
- ✅ Tokens JWT avec expiration
- ✅ CORS configuré
- ✅ Validation des données avec Pydantic
- ✅ Mots de passe exclus des réponses

### ⚠️ Recommandations pour la production
- [ ] Utiliser HTTPS uniquement
- [ ] Stocker `JWT_SECRET_KEY` dans un secret manager
- [ ] Implémenter un système de refresh tokens
- [ ] Ajouter rate limiting sur /login et /register
- [ ] Implémenter une vérification email
- [ ] Ajouter une politique de mot de passe fort
- [ ] Mettre en place des logs d'audit
- [ ] Implémenter RBAC (Role-Based Access Control)

---

## 📞 Support & Contact

Pour toute question ou problème :
- Consulter la documentation interactive : `/docs`
- Vérifier les logs de l'application
- Tester avec les health checks : `/health`

---

## 📝 Notes de version

### Version actuelle
- FastAPI 0.104.1
- Python 3.11
- PostgreSQL compatible

### Améliorations futures possibles
- Pagination sur `GET /users/`
- Filtres de recherche sur les utilisateurs
- Reset de mot de passe par email
- Authentification OAuth2 (Google, GitHub)
- Rate limiting
- Métriques et monitoring

---

## 🎓 Bilan de compétences

Ce projet m'a permis de valider plusieurs apprentissages critiques du BUT Réseaux & Télécommunications dans le domaine DevCloud. Voici comment j'ai mis en pratique chaque compétence sur l'API Client et l'infrastructure globale.

---

### AC34.01 - Concevoir, administrer et superviser une infrastructure Cloud

J'ai participé à la conception et à la mise en place de l'infrastructure virtualisée pour héberger l'API Client. J'ai défini l'architecture de déploiement avec Kubernetes (3 VMs : 1 master, 2 workers), configuré les services nécessaires (pods, volumes persistants) et mis en place la supervision avec les health checks (ReadinessProbe et LivenessProbe sur `/health`).

---

### AC34.02 - Orchestrer les ressources Cloud

J'ai intégré l'API Client dans l'architecture générale en configurant les Deployments, Services, PersistentVolumes et Secrets Kubernetes. J'ai aussi participé à l'automatisation du déploiement avec Ansible qui installe et configure le cluster Kubernetes et tous les microservices automatiquement.

---

### AC34.03 - Investiguer sur les incidents et les résoudre afin d'améliorer la qualité et la fiabilité des infrastructures

J'ai diagnostiqué et résolu des problèmes de connexion à la base de données en mettant en place un mécanisme de retry (60 secondes d'attente). J'ai configuré les LivenessProbes pour redémarrer automatiquement les pods défaillants et les resource limits pour empêcher qu'un conteneur monopolise les ressources du cluster.

---

### AC35.02 - Concevoir, gérer et sécuriser un environnement de microservices

J'ai implémenté un système d'authentification JWT avec expiration (30 minutes) et hashage bcrypt des mots de passe. J'ai mis en place la validation des tokens pour contrôler l'accès, et stocké les données sensibles (clé JWT, mots de passe) dans des Secrets Kubernetes plutôt qu'en clair.

---

### AC35.03 - Gérer son infrastructure comme du code

J'ai créé le Dockerfile de l'API Client, les fichiers YAML Kubernetes (Deployment, Service, PV/PVC, Secrets) et participé à la configuration du Vagrantfile et du playbook Ansible. L'infrastructure est versionnée dans Git, traçable, portable et automatisable (un simple `vagrant up` déploie tout le cluster).

---

## 📝 Conclusion

Ce projet m'a vraiment permis de progresser sur plein d'aspects techniques. En développant l'API Client, j'ai découvert concrètement comment sécuriser une application avec JWT et bcrypt, ce qui va bien au-delà de la théorie qu'on voit en cours. J'ai aussi beaucoup appris sur Kubernetes et la gestion d'infrastructure : déployer des pods, configurer des volumes persistants, mettre en place des health checks, tout ça dans un vrai cluster avec plusieurs machines virtuelles.

Le côté Infrastructure as Code m'a particulièrement marqué. Passer de configurations manuelles à tout automatiser avec Vagrant et Ansible, c'est vraiment un gain de temps énorme et ça évite plein d'erreurs. En gros, j'ai compris l'intérêt réel des microservices et du DevCloud dans un projet concret.

Ce qui est cool aussi, c'est que l'API Client est centrale dans l'architecture : elle gère toute l'authentification pour les autres services. Du coup, j'ai dû faire attention à la sécurité et à la fiabilité, parce que si cette API tombe, plus rien ne marche. Ça m'a appris à anticiper les problèmes et à mettre en place des solutions robustes.

---

**Dernière mise à jour** : Décembre 2024  
**Auteur** : Équipe DevCloud E-Commerce
