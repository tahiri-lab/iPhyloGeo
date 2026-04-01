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

#### 7. 🐳 Démarrer la base de données et Redis avec Docker

Installez [Docker Desktop](https://docs.docker.com/get-docker/), puis lancez les conteneurs en arrière-plan :

```bash
docker compose up -d
```

```bash
docker run -d --name redis -p 6379:6379 redis:alpine
```

### ⚙️ Configuration du programme

Modifiez le fichier `.env` à la racine du projet avec vos paramètres :

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

Sur Windows, dans la racine du projet :

```bash
venv\Scripts\activate
```

```bash
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

---

## 🧪 Exécuter les tests

Assurez-vous que l'environnement virtuel est activé, puis installez les navigateurs Playwright (requis pour les tests e2e) :

```bash
venv\Scripts\playwright install chromium
```

Ensuite, lancez tous les tests depuis la racine du projet :

```bash
venv\Scripts\python -m pytest tests/
```

Pour lancer uniquement les tests unitaires :

```bash
venv\Scripts\python -m pytest tests/unit/
```

Pour lancer un fichier de tests spécifique :

```bash
venv\Scripts\python -m pytest tests/unit/test_enums.py
```

Pour lancer un seul test :

```bash
venv\Scripts\python -m pytest tests/unit/test_enums.py::test_get_code_returns_expected_code
```
