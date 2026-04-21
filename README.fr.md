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
- 🐍 Python 3.10 (voir étapes ci-dessous)
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

#### 2. 🐍 Installer Python 3.10

Téléchargez et installez le gestionnaire Python (Python Manager) :

```
https://www.python.org/ftp/python/pymanager/python-manager-26.0.msix
```

> **Note :** Si vous obtenez une erreur du type `'install' command is unavailable`, vous avez l'ancien lanceur Python (Python Launcher) installé. Allez dans **Paramètres > Applications installées**, recherchez **"Python Launcher"** et désinstallez-le avant d'exécuter la commande ci-dessous.

Ensuite, installez Python 3.10.11 via le gestionnaire :

```bash
py install 3.10.11
```

#### 3. 🏠 Créer et activer l'environnement virtuel

```bash
py -3.10 -m venv venv
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

Installez [Docker Desktop](https://docs.docker.com/get-docker/), ouvrez-le, puis lancez les conteneurs en arrière-plan :

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
MONGO_URI='mongodb://localhost:27018'
DB_NAME='iphylogeo'
URL='http://localhost'
PORT='8050'
REDIS_URL='redis://localhost:6379/0'
TEMP_RESULT_TTL_SECONDS='7200'
```

> **Note :** Le port MongoDB est `27018` (et non le port par défaut `27017`) car `docker-compose.yml` effectue le mappage `27018:27017`.

Si vous souhaitez que la fonctionnalité d'envoi d'e-mail fonctionne, ajoutez ces variables à votre `.env` :

```
EMAIL_USER='iphylogeo@gmail.com'
EMAIL_PASSWORD='rogo lqhi fldu mwml'
```

### ▶️ Exécution

Assurez-vous d'être à la racine du projet (iPhylogeo) et que votre environnement virtuel est activé.

Ouvrez 2 terminaux :

1. Terminal A (services de base de données) :

```bash
docker compose up
```

2. Terminal B (application) :

`npm start` lance maintenant l'application Dash, l'interface Electron, les watchers d'assets et le worker RQ.

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

Le projet utilise des fichiers SCSS compilés en CSS avec Dart Sass (le paquet npm `sass`).

Les fichiers SCSS doivent être placés dans :

```
apps/assets/styles/votre_fichier.scss
```

Ajoutez ensuite la paire source/sortie dans [scripts/sass_css.js](scripts/sass_css.js), dans le tableau `PAIRS` :

```js
["apps/assets/styles/votre_fichier.scss", "apps/assets/votre_fichier.css"];
```

Compilez une fois les fichiers CSS :

```bash
npm run build:css
```

Surveillez les changements SCSS et recompilation automatique :

```bash
npm run watch:css
```

Si vous lancez `npm start`, la surveillance CSS est déjà incluse via `dev:assets`.

> ⚠️ Le fichier CSS de sortie doit être généré dans le dossier `apps/assets`, sinon Dash ne le chargera pas.

---

## 🧪 Exécuter les tests

Assurez-vous que l'environnement virtuel est activé, puis installez Playwright et ses navigateurs (requis pour les tests e2e) :

```bash
python -m playwright install chromium
```

Ensuite, lancez tous les tests depuis la racine du projet :

```bash
python -m pytest tests/
```

Pour lancer uniquement les tests unitaires :

```bash
python -m pytest tests/unit/
```

Pour lancer un fichier de tests spécifique :

```bash
python -m pytest tests/unit/test_enums.py
```

Pour lancer un seul test :

```bash
python -m pytest tests/unit/test_enums.py::test_get_code_returns_expected_code
```
