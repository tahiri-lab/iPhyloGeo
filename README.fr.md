# 🌳 iPhyloGeo

- 🇬🇧 Lien vers la version anglaise : [version anglaise](README.md)

## 📝 Description

### 🔎 Interface de visualisation de données en Python à l'aide de Dash

Le but de cette application est la simplification et la visualisation du projet Phylotree.

https://github.com/tahiri-lab/phylogeography-algo

> ⚠️ L'application nécessite une base de données pour fonctionner.

## 🚀 Pour commencer

### 📋 Prérequis

- 🐙 [Git](https://git-scm.com/)
- 🐍 Python 3.12 (voir étapes ci-dessous)
- 📦 [Node.js / npm](https://nodejs.org/) (version npm 11.11.0 recommandée)
- 🐳 [Docker Desktop](https://docs.docker.com/get-docker/)
- 🔧 Microsoft C++ Build Tools

### 💻 Installation (Windows)

#### 1. 🐙 Cloner le dépôt

Installez [Git](https://git-scm.com/), puis exécutez :

```bash
git clone https://github.com/tahiri-lab/iPhylogeo
cd iPhylogeo
```

#### 2. 🐍 Installer Python 3.12

Téléchargez et installez le gestionnaire Python (Python Manager) :

```
https://www.python.org/ftp/python/pymanager/python-manager-26.0.msix
```

Ensuite, installez Python 3.12.10 via le gestionnaire :

```bash
py install 3.12.10
```

#### 3. 🏠 Créer et activer l'environnement virtuel

```bash
py -3.12 -m venv venv
venv\Scripts\activate
python --version
```

#### 4. 🔧 Installer Microsoft C++ Build Tools

Certaines dépendances Python requièrent les outils de compilation C++.
Téléchargez-les ici : https://visualstudio.microsoft.com/visual-cpp-build-tools/

Lors de l'installation, assurez-vous de cocher **"Développement Desktop en C++"**.

#### 5. 📚 Installer les dépendances Python

Assurez-vous que l'environnement virtuel est activé, puis :

```bash
pip install -r requirements.txt
```

#### 6. 📦 Installer les dépendances npm

Si npm n'est pas installé, téléchargez Node.js ici : https://nodejs.org/ (version npm 11.11.0 recommandée).

```bash
npm install
```

#### 7. 🐳 Démarrer la base de données avec Docker

Installez [Docker Desktop](https://docs.docker.com/get-docker/), puis lancez les conteneurs en arrière-plan :

```bash
docker compose up -d
```

### 🐧 Installation (Linux / Ubuntu)

La procédure suivante est destinée aux utilisateurs d'un environnement Linux de bureau (Desktop).

#### 1. 🐙 Cloner le dépôt

```bash
git clone https://github.com/tahiri-lab/iPhylogeo
cd iPhylogeo
```

#### 2. 📦 Installer les prérequis système

Sur les distributions basées sur Debian/Ubuntu, installez les outils de base (Python, compilateurs C++, Node.js et Docker) :

```bash
sudo apt update
sudo apt install python3-venv python3-dev build-essential nodejs npm docker.io docker-compose-v2 -y
```

#### 3. 🏠 Créer et activer l'environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 4. 📚 Installer les dépendances (Python et npm)

Assurez-vous que l'environnement virtuel est activé dans le dossier iPhylogeo, puis exécutez :

```bash
pip install -r requirements.txt
npm install
```

#### 5. 🐳 Démarrer la base de données avec Docker

Lancez les conteneurs en arrière-plan (ajoutez sudo si votre utilisateur n'est pas dans le groupe docker) :

```bash
sudo docker compose up -d
```

> ✅ Installation terminée (Windows ou Linux).
> Passez maintenant à la section suivante pour configurer le projet.

---

### ⚙️ Configuration du programme

Modifiez ou créez le fichier `.env` à la racine du projet avec vos paramètres :

```
APP_ENV='dev'
HOST='localhost'
MONGO_URI='mongodb://localhost:27017'
DB_NAME='iPhyloGeo'
URL='http://localhost'
PORT='8050'
```

Si vous souhaitez que la fonctionnalité d'envoi d'e-mail fonctionne, créez un fichier `password.env` dans `iPhyloGeo\apps\pages\results\` :

```
GMAIL_PASSWORD=(mot de passe d'application de aphylogeotest@gmail.com ou de l'adresse e-mail souhaitée)
```

### ▶️ Exécution

Assurez-vous d'être à la racine du projet (iPhylogeo) et que votre environnement virtuel est activé.

Sur Windows :

```bash
venv\Scripts\activate
npm start
```

Sur Linux :

```bash
source venv/bin/activate
npm start
```

---

## 🕐 Utilisation de la tâche planifiée (cronJob)

Si la base de données est déployée sur un serveur Linux, un script est inclus pour supprimer les fichiers de plus de 14 jours. Exemple de fichier `cronjob` :

```bash
00 00 * * * /chemin/vers/python /chemin/vers/iPhyloGeo/scripts/delete_files.py >> /chemin/vers/iPhyloGeo/scripts/cron.log 2>&1
```

Pour enregistrer la tâche :

```bash
crontab /chemin/vers/iPhyloGeo/scripts/cronjob
```

🛠️ Outil utile pour la syntaxe cron : https://crontab.guru/

Pour lister les tâches planifiées actives :

```bash
crontab -l
```

---

## 🎨 Générer un fichier CSS à partir de SCSS

Le projet utilise des fichiers SCSS compilés en CSS. Les fichiers SCSS doivent être placés dans :

```
apps/assets/styles/votre_fichier.scss
```

Ajoutez une entrée dans la section `dist` du fichier [Gruntfile.js](Gruntfile.js) :

```js
dist: {
    files: {
        'apps/assets/votre_fichier.css': 'apps/assets/styles/votre_fichier.scss'
    }
}
```

Et dans la section `watch/sass/files` :

```js
watch: {
    sass: {
        files: [
            'apps/assets/votre_fichier.css'
        ],
    }
}
```

> ⚠️ Le fichier CSS doit être généré dans le dossier `assets`, sinon Dash ne le chargera pas.
