# Kubernetes Manifests

Ce dossier contient tous les fichiers YAML décrivant les ressources Kubernetes nécessaires au fonctionnement de l'application.

## Organisation

### Configuration Globale
- **`namespace.yaml`** : Crée le namespace `ecommerce` où tout est déployé.
- **`pv-pvc.yaml`** : Définit les PersistentVolumes (PV) et PersistentVolumeClaims (PVC) pour assurer la persistance des données des bases de données.
- **`secret.yaml`** : Contient les mots de passe encodés en Base64 (DB passwords, JWT secret).
- **`configmap.yaml`** : Variables de configuration non sensibles.
- **`db-init-configmap.yaml`** : Scripts SQL d'initialisation pour les bases de données.

### Services & Déploiements
Chaque composant a son propre fichier YAML (ou une paire Deployment/Service) :

- **`catalogue.yaml`** : API Catalogue + Service NodePort.
- **`catalogue-db.yaml`** : Base PostgreSQL pour le catalogue.
- **`client.yaml`** : API Client.
- **`client-db.yaml`** : Base PostgreSQL pour les clients.
- **`panier.yaml`** : API Panier.
- **`redis.yaml`** : Base Redis pour le panier.
- **`commandes.yaml`** : API Commandes.
- **`commandes-db.yaml`** : Base PostgreSQL pour les commandes.
- **`frontend.yaml`** : Serveur Nginx servant l'application React.

### Ingress / Routing
- **`frontend-nginx-config.yaml`** : Configuration spécifique de Nginx pour le frontend (reverse proxy vers les APIs).

## Déploiement Manuel

Si vous deviez déployer ces fichiers manuellement (sans le script Ansible), l'ordre est important :

1. Namespace
2. Secrets & ConfigMaps
3. Volumes (PV/PVC)
4. Bases de données (attendre qu'elles soient prêtes)
5. APIs
6. Frontend

```bash
kubectl apply -f namespace.yaml
kubectl apply -f secret.yaml -f configmap.yaml
kubectl apply -f pv-pvc.yaml
# ... etc
```
