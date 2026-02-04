# Ansible Configuration

Ce dossier contient les playbooks et la configuration Ansible utilisés pour provisionner les machines virtuelles et installer le cluster Kubernetes.

## Fichiers Principaux

- **`setup.yml`** : Le playbook principal. C'est lui qui orchestre tout l'installation.
  - Installe les prérequis système (curl, gpg, etc.).
  - Installe Docker (Container Runtime).
  - Installe Kubernetes (kubeadm, kubelet, kubectl).
  - Initialise le Master Node.
  - Configure le réseau Pod (Flannel/Calico).
  - Joint les Worker Nodes au cluster.
  - Construit les images Docker des applications.
  - Déploie les manifestes Kubernetes.

- **`inventory.ini`** : Définit les groupes d'hôtes (`master`, `workers`) et leurs adresses IP. (Note: Vagrant génère souvent son propre inventaire dynamique).

- **`ansible.cfg`** : Configuration globale d'Ansible (désactivation de la vérification des clés SSH, etc.).

## Fonctionnement

Ce playbook est appelé automatiquement par Vagrant lors de la commande `vagrant up`.
Cependant, vous pouvez le relancer manuellement si vous modifiez la configuration :

```bash
# Depuis la racine du projet (sur l'hôte)
vagrant provision
```
