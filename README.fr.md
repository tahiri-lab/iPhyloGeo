# Phylogeo_frelon

- Lien vers la version anglaise : [version anglaise](README.md)

## Description:
### Interface de visualisation de données en Python à l'aide de Dash

Le but de cette application est la simplification et la visualisation du projet Phylotree.

https://github.com/tahiri-lab/phylogeography-algo


Le projet peut être utilisé de deux façons:
1. En utilisant le système de fichiers pour stocker les fichiers et les résultats
2. En utilisant une base de données pour stocker les fichiers et les résultats

La première option est l'option par défaut. Si vous voulez utiliser la base de données, vous devez modifier le fichier .env. Voir la section "Configuration du programme" pour plus de détails.

## Pour commencer

### Installation:

* Tout d'abord, le programme devra être téléchargé à l'aide de GitHub(la commande git clone).
```	
git clone https://github.com/tahiri-lab/iPhylogeo 
```

Pour télécharger le projet, tapez simplement l'une des commandes ci-dessus dans un terminal.

* Vous pouvez également télécharger le fichier zip avec le lien Github ci-dessus.


## Comment utilisez le programme? 
### Préalables,librairies etc.
Avant d'utiliser ce programme, assurez-vous d'avoir installé toutes les bibliothèques nécessaires pour qu'il fonctionne correctement.
Tout d'abord, vous devez installer le package aPhyloGeo. Selon votre système d'exploitation, les commandes spécifiques seront légèrement différentes. Pour un système basé sur Linux, vous pouvez utiliser les commandes suivantes :

1. git clone https://github.com/tahiri-lab/aPhylogeo
2. Si vous n'avez pas `virtualenv` installé, exécutez `python3 -m pip install --user virtualenv`
3. Créez un nouvel environnement virtuel (venv) dans votre terminal en utilisant `python3 -m venv venv`.
4. Toujours dans le terminal, entrez dans le nouvel environnement virtuel en utilisant `source venv/bin/activate`.

Si vous utilisez un système basé sur Windows, vous pouvez utiliser les commandes suivantes :

1. git clone https://github.com/tahiri-lab/aPhylogeo
2. Si vous n'avez pas virtualenv installé, exécutez `python -m pip install --user virtualenv`
3. Créez un nouvel environnement virtuel (venv) dans votre terminal en utilisant `python -m venv venv`.
4. Toujours dans le terminal, activez le nouveau venv en utilisant `venv/bin/activate`.

N.B. Vous aurez besoin de Microsoft C++ Build Tools pour installer toutes les dépendances vous pouvez le trouver ici: https://visualstudio.microsoft.com/visual-cpp-build-tools/ . Assurez-vous d'inclure C++ build tools dans votre installation.

Ensuite, vous pouvez installer les autres exigences. Assurez-vous d'utiliser le même venv que ci-dessus. Assurez-vous d'être dans le répertoire iPhyloGeo.
```
pip install -r requirements.txt
npm install
```

Enfin, si vous voulez exécuter le programme avec une base de données, vous devez installer Docker. Vous pouvez trouver le guide d'installation ici : https://docs.docker.com/get-docker/

- Le dossier apps : un modèle pour chaque page web
- Le dossier assets : les images utilisées dans le modèle et le fichier CSS


### Configuration du programme:
- Pour configurer le programme, vous devez modifier le fichier .env avec vos propres données.
Voici un exemple de fichier .env si vous voulez exécuter le programme localement :
```
APP_ENV='dev'
HOST='local'
MONGO_URI=
DB_NAME=
URL='http://localhost'
PORT='8050'
```
- Si vous voulez exécuter le programme avec une base de données, vous devez modifier le fichier .env. Par exemple :
```
APP_ENV='dev'
HOST='server'
MONGO_URI='mongodb://localhost:27017'
DB_NAME='iPhyloGeo'
URL='http://localhost'
PORT='8050'
```

Si vous souhaitez que la fonction d'adresse e-mail fonctionne correctement, vous devez générer un fichier `"password.env"` dans le chemin du répertoire `"iPhyloGeo\apps\pages\results\password.env"` avec le format suivant : 
```
GMAIL_PASSWORD=(insérez ici le mot de passe d'application de aphylogeotest@gmail.com ou l'adresse e-mail que vous souhaitez utiliser).
```

### Exécution:
- Pour exécuter le programme localement, vous pouvez utiliser la commande suivante :
```
npm start
```
Pour exécuter le programme avec une base de données, vous devez exécuter les commandes suivantes :
```
docker compose up
npm start
```


### Utilisation de la tâche planifiée cronJob
Si la base de données est déployée sur un serveur Linux, nous avons inclus un script pour supprimer les fichiers qui ont plus de 14 jours. Pour ce faire, vous devez créer une tâche planifiée cronJob.
Pour créer une tâche planifiée cron, vous pouvez utiliser le fichier `cronjob` comme modèle.
Par exemple, créez un fichier nommé `cronjob` et ajoutez la ligne suivante :
```bash
00 00 * * * /home/local/USHERBROOKE/belm1207/miniconda3/envs/geo/bin/python /home/local/USHERBROOKE/belm1207/iPhyloGeo/scripts/delete_files.py >> /home/local/USHERBROOKE/belm1207/iPhyloGeo/scripts/cron.log 2>&1
```
Pour créer la tâche planifiée cron avec le fichier, vous pouvez utiliser la commande suivante :
```bash
crontab /home/local/USHERBROOKE/belm1207/iPhyloGeo/scripts/cronjob
```

Cela exécutera le script tous les jours à 00:00.

1. Le premier élément de la tâche planifiée cron est l'heure. [Outils utiles](https://crontab.guru/)
2. Le deuxième élément est le chemin de l'exécutable Python. Dans ce cas, nous utilisons l'environnement geo de conda.
3. Le troisième élément est le chemin complet du fichier de script.
4. Le quatrième élément est le chemin complet du fichier journal. Ceci est facultatif, mais c'est une bonne pratique de journaliser la sortie du script.

Si vous voulez voir la liste des tâches planifiées cron, vous pouvez utiliser la commande suivante :
```bash
crontab /home/local/USHERBROOKE/belm1207/iPhyloGeo/scripts/cronjob
```

## Comment générer un fichier CSS
### Compréhension de la structure du projet

* Le projet utilise des fichiers SCSS qui doivent être créés dans le dossier des styles.
```
apps/assets/styles/your_file.scss
```
* Dash ne supporte pas les fichiers SCSS directement, il faut donc générer un fichier CSS à partir du fichier SCSS. Pour ce faire, il faut l'inclure dans le fichier Gruntfile.js.
```
./Gruntfile.js 
```
* Dans le fichier Gruntfile.js, vous devez ajouter le code suivant dans la section dist. `le fichier de sortie désiré` : `le fichier SCSS`

*Le fichier CSS doit être généré dans le dossier **assets**, sinon il ne fonctionnera pas.*
```
 [...]
 
 dist: {
                files: {
                    'apps/assets/your_file.css': 'apps/assets/styles/your_file.scss'
                }
 [...]
```
* Dans le fichier Gruntfile.js, vous devez ajouter le code suivant dans la section watch/sass/files. `le fichier SCSS`

*La section watch est nécessaire pour régénérer le fichier CSS lorsque des changements sont détectés dans les fichiers SCSS, elle régénérera également tous les fichiers CSS sur `npm start`*
```
 [...]
        watch: {
            sass: {
                files: [
                    'apps/assets/your_file.css'
                ],
            }
        }
  [...]
```
