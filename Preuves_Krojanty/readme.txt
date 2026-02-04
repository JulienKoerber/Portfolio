Voici les instructions à suivre pour utiliser notre projet!

## La structure de notre projet
- `src/` : Contient les fichiers sources principaux du projet (.c).
- `include/` : Contient les fichiers d'en-tête (.h).
- `tests/` : Contient les tests unitaires de nos fichiers.
- `doc/` : Contient le fichier Doxyfile et le doxygen8log.txt 
- `Makefile` : C'est l'outil qui permet de compiler et lancer le projet facilement.

## Compilation et exécution de notre jeu
1. Ouvrir un terminal à la racine du dossier `Immersion_groupe_9`.
        cd Immersion_groupe_9 
        (Pour se rendre dans le répertoire où se trouve le MakeFile)

2. Une fois dans le répertoire Immersion_groupe_9, il faut compiler le projet avec la commande :
        
        make
        (Cela va générer notre éxecutable principal qui s'appelle "game")

3. Lancer le jeu en réseau ou non avec ou sans l'ia grâce à la commande :

        ./game -l  (pour lancer le jeu en local)
        ./game -l -ia (pour jouer en local contre notre ia)
        ./game -s pppp  (pour lancer le jeu en mode serveur sur le port de votre choix)
        ./game -s pppp -ia  (pour lancer le jeu en mode serveur pour que l'IA joue à la place du serveur)
        ./game -c aaa.aaa.aaa.aaa:pppp  (pour lancer le jeu en mode client sur l'adresse et le port du serveur)
        ./game -c aaa.aaa.aaa.aaa:pppp -ia  (pour lancer le jeu en mode client pour que l'IA joue à la place du client)

4. La Documentation avec Doxygen :

        make docs
        (Afin de générer les fichiers HTML et LATEX dans le dossier doc)
        
        make open
        (Afin d'ouvrir la page index.html)

5. Lancer les tests unitaires :

        make test
        (Afin d'exécuter tous les tests unitaires du projet)

        make coverage-report
        (Afin de voir un rapport détaillé de chaque code)

6. Nettoyer les fichiers compilés :

        make clean
        (Afin de supprimer tout les éxecutables pour pouvoir recompiler)

7. Résumé des commandes make

        make help
        (Cette commande affiche l'ensemble des make qu'il est possible de faire)