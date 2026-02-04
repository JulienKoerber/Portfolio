# Configuration Docker

Ce dossier contient les fichiers de configuration Docker partagés ou de base pour l'infrastructure du projet.

## Fichiers

### base.Dockerfile

Ce fichier définit une image Docker de base (`base:latest`) utilisée par tous les microservices Python du projet (Catalogue, Client, Commandes, Panier).

**Objectif :**
- Centraliser les dépendances communes (FastAPI, SQLAlchemy, Uvicorn, etc.).
- Réduire le temps de construction des images individuelles (les couches communes sont déjà en cache).
- Assurer la cohérence des versions des bibliothèques entre les différents services.

**Contenu :**
- Image source : `python:3.9-slim`
- Installation des paquets Python communs via `pip`.

## Utilisation

Cette image est construite automatiquement lors du déploiement via le playbook Ansible (`setup.yml`). Elle est taguée localement comme `base:latest`.

Les Dockerfiles des APIs commencent ensuite par :
```dockerfile
FROM base:latest
```
Cela leur permet d'hériter de tout l'environnement pré-configuré.
