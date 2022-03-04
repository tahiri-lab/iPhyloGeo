# Phylogeo_frelon

- Lien vers la version anglaise : [version anglaise](README.md)

## Description:
### Interface de visualisation de données en Python à l'aide de Dash

Le but de cette application est la simplification et la visualisation du projet Phylotree.

https://github.com/tahiri-lab/phylogeography-algo

## Pour commencer

### Installation:

* Premièrement, le programme devra être téléchargé à l'aide de GitHub(la commande git clone).  
* Deuxièmement, vous devez choisir sur quel système d'exploitation vous voulez faire exécuter le programme.
Mac OS(main), Linux, or Windows.
* Dernière étape, il faut télécharger le programme. Pour se faire, il faut cloner le projet à l'aide
de l'une des commandes suivantes.
* Pour les utilisateurs Macbooks(MacOSX) (la branche principal dans notre cas) utilisez cette commande :
```
git clone -b "main" git@github.com:tahiri-lab/iPhylogeo.git
```
* Pour les utilisateurs Windows, utilisez cette commande:
```
git clone -b "Windows" git@github.com:tahiri-lab/iPhylogeo.git
```
* Pour les utilisateurs Linux, utilisez cette commande:
```
git clone -b "Linux" git@github.com:tahiri-lab/iPhylogeo.git
```

Pour télécharger le projet, il suffit d'entrée la commande dans un terminal dans le fichier voulu.
* Vous pouvez aussi télécharger le fichier zip sur GitHub avec le lien plus haut. 

## Comment utilisez le programme? 
### Préalables,librairies etc.
Avant d'utilisez se programme il faut s'assurer d'avoir installé les librairies nécéssaire pour le faire fonctionner.
Pour se faire, il suffit d'utiliser la commande suivante: 
```
pip install -r requirements.txt
```

- Utilisez index.py pour démarer le programme
- tree.py pipeline.py et pipeline_specific_genes.py sont les algorithmes
- Fichier apps: modèle pour chaque page web
- Fichier assets: images utilisez dans les modèles et les fichiers css
- Fichier datasets: Données météorologiques utilisez dans l'analyse
- Fichier exec: Programmes biologiques utilisez dans l'analyse
- Fichier input: Paramètres utilisez avec les programmes biologiques
- Fichier output: Se fichier est utilisez pour stocker les résultats de l'analyse

### Exécution:
- Pour exécuter le programme il suffit d'utiliser son interpréteur Python et d'exécuter le fichier index.py dans le
fichier iPhylogeo.