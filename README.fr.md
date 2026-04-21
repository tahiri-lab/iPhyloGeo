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

#### 7. 🧬 Installer les outils d'alignement externes (MUSCLE, ClustalW2, MAFFT, FastTree) (Optionnel, mias nécessaire pour que tout les paramètres fonctionnent)

Ces binaires sont requis si vous choisissez la méthode d'alignement `MUSCLE`, `CLUSTALW` ou `MAFFT`, ou le type d'arbre `Fast Tree`. Ils **ne sont pas** inclus dans le paquet Python `aphylogeo`.

Téléchargez les binaires Windows :

- MUSCLE 5 : https://drive5.com/muscle/downloads_v5.htm → `muscle5.1.win64.exe`
- ClustalW2 : http://www.clustal.org/clustal2/ → `clustalw2.exe`
- MAFFT : https://mafft.cbrc.jp/alignment/software/windows.html → le dossier `mafft-win/`
- FastTree : http://www.microbesonline.org/fasttree/#Install → `FastTree.exe`

Sous Windows, `aphylogeo` résout ces chemins à partir du dossier d'installation du paquet. Placez donc les fichiers dans le `site-packages` de votre environnement virtuel :

```
venv\Lib\site-packages\aphylogeo\bin\
├── muscle5.1.win64.exe
├── clustalw2.exe
├── mafft-win\
│   └── mafft.bat
├── FastTree.exe
└── tmp\          ← doit exister (fichiers FASTA temporaires)
```

> ⚠️ Si le dossier `tmp\` est absent dans `site-packages\aphylogeo\bin\`, créez-le manuellement. FastTree et les helpers d'alignement y écrivent des fichiers FASTA temporaires et échoueraient sinon avec `FileNotFoundError`.

#### 8. 🐳 Démarrer la base de données avec Docker

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

#### 5. 🧬 Installer les outils d'alignement externes (MUSCLE, ClustalW2, MAFFT, FastTree) (Optionnel, mais nécessaire pour que tous les paramètres fonctionnent)

Ces outils sont requis si vous choisissez la méthode d'alignement `MUSCLE`, `CLUSTALW` ou `MAFFT`, ou le type d'arbre `Fast Tree`. Ils **ne sont pas** inclus dans le paquet Python `aphylogeo`.

**Option A — Installation système via `apt` (la plus simple, recommandée sous Linux)**

```bash
sudo apt install muscle clustalw mafft fasttree -y
```

Les binaires se retrouvent dans `/usr/bin/` (par ex. `/usr/bin/FastTree`, `/usr/bin/mafft`, …). Sur la plupart des configurations Linux, c'est suffisant pour exécuter le pipeline.

> ℹ️ `aphylogeo` utilise en interne des chemins en dur du type `aphylogeo/bin/<binaire>` (relatifs au cwd sous Linux/macOS — voir la section [TODO](#todo)). Si vous rencontrez un `FileNotFoundError` ou `ApplicationError` indiquant un binaire manquant, passez à l'Option B ou créez des liens symboliques vers les binaires système :
>
> ```bash
> mkdir -p aphylogeo/bin
> ln -sf "$(command -v FastTree)"  aphylogeo/bin/FastTree
> ln -sf "$(command -v muscle)"    aphylogeo/bin/muscle5.1.linux_intel64
> ln -sf "$(command -v clustalw)"  aphylogeo/bin/clustalw2
> mkdir -p aphylogeo/bin/mafft-linux64
> ln -sf "$(command -v mafft)"     aphylogeo/bin/mafft-linux64/mafft.bat
> ```

**Option B — Binaires manuels dans `aphylogeo/bin/`**

Téléchargez les binaires Linux :

- MUSCLE 5 : https://drive5.com/muscle/downloads_v5.htm → `muscle5.1.linux_intel64`
- ClustalW2 : http://www.clustal.org/clustal2/ → `clustalw2`
- MAFFT : https://mafft.cbrc.jp/alignment/software/ → le dossier `mafft-linux64/`
- FastTree : http://www.microbesonline.org/fasttree/#Install → `FastTree`

Placez-les à la racine du projet iPhylogeo (`aphylogeo` résout ces chemins relativement au répertoire de travail courant) :

```
iPhylogeo/aphylogeo/bin/
├── muscle5.1.linux_intel64
├── clustalw2
├── mafft-linux64/
│   └── mafft.bat
├── FastTree
└── tmp/
```

Rendez les binaires exécutables :

```bash
chmod +x aphylogeo/bin/muscle5.1.linux_intel64 \
         aphylogeo/bin/clustalw2 \
         aphylogeo/bin/FastTree
```

> ℹ️ iPhylogeo crée déjà `aphylogeo/bin/tmp/` au démarrage du pipeline pour contourner un bug de chemin dans `aphylogeo`. Voir la section [TODO](#todo).

#### 6. 🐳 Démarrer la base de données avec Docker

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

---

## TODO

Les points suivants sont des **problèmes en amont dans `aphylogeo`** qui impactent `iPhylogeo`. Ils doivent être signalés/corrigés dans `aphylogeo` lui-même — **ne pas** patcher le paquet installé localement, car ces modifications seraient perdues à la prochaine réinstallation.

- **Faute de frappe sur la similarité Sørensen-Dice.** Dans `aphylogeo/alignement.py` (ligne 937), `td.sorencen(...)` devrait être `td.sorensen(...)`. En l'état, sélectionner la méthode `SorensenDice` lève `AttributeError: module 'textdistance' has no attribute 'sorencen'` et le job d'alignement génétique échoue. Contournement en attendant : éviter la méthode `SorensenDice` dans les paramètres d'iPhylogeo.
- **`step_size` est ignoré.** Dans `slidingWindow()` (`aphylogeo/alignement.py` ligne 755), le pas de glissement est fixé à `Params.window_size` au lieu de `Params.step_size`. Modifier `step_size` depuis les paramètres d'iPhylogeo n'a donc actuellement aucun effet ; la largeur de la fenêtre est également utilisée comme pas. À corriger en amont.
- **Bug de chemin `aphylogeo/bin/tmp` (Linux/macOS).** `createTmpFasta()`, `fasttree()` et les helpers MUSCLE/ClustalW utilisent le chemin relatif au cwd `aphylogeo/bin/tmp/` sous Linux/macOS, tandis que Windows utilise un chemin absolu dérivé de `__file__`. Le correctif amont consiste à résoudre les chemins temporaires depuis le dossier du paquet (par exemple `Path(__file__).resolve().parent / "bin" / "tmp"`) sur toutes les plateformes et à s'assurer que ce dossier existe avant toute écriture/lecture/nettoyage. Contournements actuels côté iPhylogeo (sans modifier `aphylogeo`) :
  - Linux/macOS : iPhylogeo crée `./aphylogeo/bin/tmp/` au démarrage du pipeline dans `create_genetic_trees()` (`os.makedirs("aphylogeo/bin/tmp", exist_ok=True)`).
  - Windows : le dossier `tmp\` dans `…\site-packages\aphylogeo\bin\` doit être créé manuellement une fois (voir l'étape d'installation Windows).
