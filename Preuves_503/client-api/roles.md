# Répartition des Rôles — Projet E-Commerce Microservices (Groupe de 5)

## 📌 Organisation Générale
Le projet repose sur une architecture microservices comprenant :
- API Catalogue  
- API Clients & Authentification  
- API Panier  
- API Commandes  
- Front-End (interface utilisateur)  
- Infrastructure Kubernetes + Ansible  

Chaque étudiant possède un rôle dédié, avec des tâches même‐ ment réparties et clairement définies.

---

# 👤 Étudiant 1 (VLADIMIR) — Front-End (Responsable Interface Utilisateur)

## Responsabilités principales
- Développer l’intégralité du front-end de l’application.
- Consommer les API : Catalogue, Clients, Panier, Commandes.
- Créer toutes les pages principales :
  - Accueil (liste produits)
  - Page produit (optionnel selon niveau)
  - Connexion / Inscription
  - Panier
  - Validation commande
  - Historique commandes
- Gérer l’affichage dynamique (fetch API).
- Intégrer les messages d’erreur des API.
- Assurer le responsive et l’ergonomie.

## Livrables
- Site fonctionnel consommant les 4 microservices.
- Documentation : architecture front, schémas de navigation.
- Participation à la soutenance : démonstration de l’UI.

---

# 👤 Étudiant 2 (BENJAMIN) — API Catalogue (Responsable Produits)

## Responsabilités principales
- Développer l’API Catalogue (FastAPI recommandé).
- Mettre en place la base de données dédiée aux produits.
- Implémenter les endpoints :
  - `GET /products`
  - `GET /products/{id}`
  - `POST /products`
  - `PUT /products/{id}`
  - `DELETE /products/{id}`
- Validation des données (schémas).
- Gestion d'éventuels stocks.
- Conteneurisation (Dockerfile).
- Déploiement Kubernetes (Deployment + Service).
- Création de la documentation API.

## Livrables
- API opérationnelle + base produits.
- Swagger / OpenAPI complet.
- YAML Kubernetes fonctionnels.
- Chapitre documentation : API Catalogue.

---

# 👤 Étudiant 3 (JULIEN) — API Clients & Authentification (Responsable Comptes)

## Responsabilités principales
- Développer l’API Clients.
- Gestion complète des utilisateurs :
  - Inscription  
  - Connexion (JWT recommandé)  
  - Lecture / modification du profil  
- Mise en place de la sécurité :
  - Hash des mots de passe (bcrypt ou équivalent)
  - Génération / validation JWT
- Base de données clients.
- Rédaction de la documentation.
- Déploiement sur Kubernetes (DB + API).

## Livrables
- API Clients sécurisée et fonctionnelle.
- JWT utilisable par les autres microservices.
- YAML K8s opérationnels.
- Chapitre documentation : Authentification & Sécurité.

---

# 👤 Étudiant 4 (CORENTIN) — API Panier (Responsable Sessions / Redis)

## Responsabilités principales
- Développer l’API Panier.
- Choisir et mettre en place la solution de stockage :
  - Redis (idéal)
  - ou sessions serveur
- Implémenter les endpoints :
  - `POST /cart/add`
  - `DELETE /cart/remove`
  - `GET /cart`
  - `DELETE /cart/clear`
- Interaction interne avec l’API Catalogue (prix, stocks).
- Gestion des sessions :
  - Lien entre JWT (id utilisateur) → panier utilisateur.
- Documentation de l’API.
- Déploiement Kubernetes (Redis + API Panier).

## Livrables
- API Panier fonctionnelle + stockage persistant.
- Tests d’intégration avec Catalogue.
- Documentation : fonctionnement des sessions / Redis.
- YAML Kubernetes.

---

# 👤 Étudiant 5 (BASTIAN) — API Commandes + Infrastructure Kubernetes & Ansible

## Responsabilités principales

### Partie API Commandes
- Développer l’API Commandes.
- Récupérer les données du panier (API Panier).
- Récupérer les informations du client (API Clients).
- Vérifier les informations produits (API Catalogue).
- Enregistrer une commande complète en base.
- Gérer l’historique des commandes d'un utilisateur.
- Rédiger la documentation API.
- Conteneurisation + déploiement Kubernetes.

### Partie Infrastructure Kubernetes
- Installer et configurer le cluster Kubernetes :
  - 1 master  
  - 2 workers  
- Installer :
  - Docker/containerd
  - kubeadm / kubelet / kubectl
  - Plugin réseau (Calico ou Flannel)
- Créer l’infrastructure logique :
  - Namespaces
  - Secret/ConfigMap
  - Ingress Controller (si nécessaire)
  - PersistentVolumes / PersistentVolumeClaims
- Déployer les YAML de tous les microservices.
- Assurer la communication interne entre les API.

### Partie Automatisation (Ansible)
- Créer des playbooks automatisant :
  - L’installation de Docker/containerd
  - L’installation de Kubernetes sur chaque VM
  - Le déploiement des microservices

## Livrables
- API Commandes complète.
- Tutoriel d’installation du cluster.
- Réseau Kubernetes opérationnel.
- Playbooks Ansible.
- Chapitre documentation : Infrastructure & Déploiement.
