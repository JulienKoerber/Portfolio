# Infrastructure & Déploiement

Ce dossier contient toute la configuration nécessaire pour déployer l'infrastructure Kubernetes locale via Vagrant et Ansible.

## Architecture

L'infrastructure est composée de 3 machines virtuelles (VMs) Debian 12 gérées par Vagrant :

| Hostname       | IP            | Rôle               | Ressources (CPU/RAM) |
|----------------|---------------|--------------------|----------------------|
| `k8s-master`   | 192.168.56.10 | Control Plane      | 6 vCPU / 4096 MB     |
| `k8s-worker-1` | 192.168.56.11 | Worker Node        | 4 vCPU / 2048 MB     |
| `k8s-worker-2` | 192.168.56.12 | Worker Node        | 4 vCPU / 2048 MB     |

## Prérequis

- [VirtualBox](https://www.virtualbox.org/)
- [Vagrant](https://www.vagrantup.com/)
- Un terminal (Bash, Zsh, PowerShell)

## Démarrage Rapide

1. **Lancer les VMs** :
   À la racine du projet (où se trouve le `Vagrantfile` ou dans ce dossier), lancez :
   ```bash
   vagrant up
   ```
   Cette commande va :
   - Télécharger l'image Debian 12 (si nécessaire).
   - Créer les 3 VMs.
   - Configurer le réseau.
   - Exécuter le playbook Ansible `infrastructure/ansible/setup.yml` automatiquement.

2. **Le Provisioning Ansible** :
   Le script Ansible effectue automatiquement les tâches suivantes :
   - Installation de Docker et Kubernetes (kubelet, kubeadm, kubectl).
   - Initialisation du Cluster sur le Master.
   - Jonction des Workers au cluster.
   - Installation de `kubectl` et `helm`.
   - Construction des images Docker des microservices (sur le Master).
   - Déploiement des manifestes Kubernetes (situés dans `infrastructure/kubernetes/`).

3. **Accéder au Cluster** :
   Connectez-vous au master via SSH :
   ```bash
   vagrant ssh master
   ```
   Vérifiez l'état des nœuds :
   ```bash
   kubectl get nodes
   ```
   Vérifiez l'état des pods :
   ```bash
   kubectl get pods -n ecommerce
   ```

## Structure des Dossiers

- **`Vagrantfile`** : Configuration des VMs.
- **`ansible/`** : Scripts d'automatisation.
  - `setup.yml` : Playbook principal qui installe tout.
  - `inventory.ini` : Inventaire des machines (généré dynamiquement par Vagrant souvent, mais peut être défini ici).
- **`kubernetes/`** : Manifestes YAML pour le déploiement des applications.
  - `namespace.yaml` : Crée le namespace `ecommerce`.
  - `pv-pvc.yaml` : Volumes persistants pour les bases de données.
  - `secret.yaml` & `configmap.yaml` : Configuration et secrets.
  - `*.yaml` : Déploiements et Services pour chaque API et DB.
  - `frontend-nginx-config.yaml` : Configuration spécifique pour le frontend.

## Commandes Utiles

### Redéployer l'infrastructure (Ansible)
Si vous modifiez le playbook Ansible, vous pouvez le relancer sans recréer les VMs :
```bash
vagrant provision
```

### Reconstruire les images Docker
Si vous modifiez le code d'une API, connectez-vous au master et utilisez le script de rebuild :
```bash
vagrant ssh master
cd /vagrant/scripts
./rebuild_apis.sh
```
Ou manuellement pour une API spécifique :
```bash
cd /vagrant/api/mon-api
docker build -t mon-api:latest .
kubectl rollout restart deployment/mon-api -n ecommerce
```

### Accès aux Services
Les services sont exposés via NodePort sur le cluster.
- **Frontend** : http://192.168.56.10:30080
- **APIs** : Accessibles via le frontend ou directement via les NodePorts configurés (voir `kubectl get svc -n ecommerce`).

## Dépannage

### Problème de "ImagePullBackOff" (Rate Limit Docker Hub)
Si vous voyez des erreurs `ImagePullBackOff` pour des images publiques (comme `redis` ou `postgres`), c'est souvent dû aux limites de téléchargement de Docker Hub pour les utilisateurs non authentifiés.
**Solution** : Attendre un peu ou configurer un miroir de registre, ou s'authentifier via `docker login` sur les nœuds (non automatisé ici).

### Les Pods restent en "Pending"
Vérifiez si les nœuds sont prêts (`kubectl get nodes`) ou s'il y a assez de ressources.
```bash
kubectl describe pod <nom-du-pod> -n ecommerce
```
