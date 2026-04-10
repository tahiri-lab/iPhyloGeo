# 🌳 iPhyloGeo

- 🇫🇷 Link for the French version: [version française](README.fr.md)

## 📝 Description

### 🔎 Data Visualization Interface in Python with Dash

The purpose of this application is to visualize the Phylotree pipeline and simplify its use.

https://github.com/tahiri-lab/phylogeography-algo

> ⚠️ The application requires a database to run.

## 🚀 Getting started

### 📋 Prerequisites

- 🐙 [Git](https://git-scm.com/)
- 🐍 Python 3.10 (see steps below)
- 📦 [Node.js / npm](https://nodejs.org/) (npm version 11.11.0 recommended)
- 🐳 [Docker Desktop](https://docs.docker.com/get-docker/)
- 🔧 Microsoft C++ Build Tools

### 💻 Installation (Windows)

#### 1. 🐙 Clone the repository

Install [Git](https://git-scm.com/), then run:

```bash
git clone https://github.com/tahiri-lab/iPhylogeo
cd iPhylogeo
```

#### 2. 🐍 Install Python 3.10

Download and install the Python Manager:

```
https://www.python.org/ftp/python/pymanager/python-manager-26.0.msix
```

> **Note:** If you get an error like `'install' command is unavailable`, you have the legacy Python Launcher installed. Go to **Settings > Installed Apps**, search for **"Python Launcher"**, and uninstall it before running the command below.

Then install Python 3.10.11 through the manager:

```bash
py install 3.10.11
```

#### 3. 🏠 Create and activate the virtual environment

```bash
py -3.10 -m venv venv
venv\Scripts\activate
python --version
```

#### 4. 🔧 Install Microsoft C++ Build Tools

Some Python dependencies require C++ build tools.
Download them here: https://visualstudio.microsoft.com/visual-cpp-build-tools/

During installation, make sure to select **"Desktop development with C++"**.

#### 5. 📚 Install Python dependencies

Make sure the virtual environment is activated, then run:

```bash
pip install -r requirements.txt
```

#### 6. 📦 Install npm dependencies

If npm is not installed, download Node.js here: https://nodejs.org/ (npm version 11.11.0 recommended).

```bash
npm install
```

#### 7. 🐳 Start the database with Docker

Install [Docker Desktop](https://docs.docker.com/get-docker/), open it, then start the containers in the background:

```bash
docker compose up -d
```

### 🐧 Installation (Linux / Ubuntu)

The following procedure is intended for desktop Linux users.

#### 1. 🐙 Clone the repository

```bash
git clone https://github.com/tahiri-lab/iPhylogeo
cd iPhylogeo
```

#### 2. 📦 Install system prerequisites

On Debian/Ubuntu-based distributions, install the base tools (Python, C++ compilers, Node.js, and Docker):

```bash
sudo apt update
sudo apt install python3-venv python3-dev build-essential nodejs npm docker.io docker-compose-v2 -y
```

#### 3. 🏠 Create and activate the virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 4. 📚 Install dependencies (Python and npm)

Make sure the virtual environment is activated in the iPhylogeo folder, then run:

```bash
pip install -r requirements.txt
npm install
```

#### 5. 🐳 Start the database with Docker

Start the containers in the background (add sudo if your user is not in the docker group):

```bash
sudo docker compose up -d
```

> ✅ Installation complete (Windows or Linux).
> Move to the next section to configure the project.

---

### ⚙️ Setting up the program

Edit or create the `.env` file at the project root with your settings:

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

> **Note:** The MongoDB port is `27018` (not the default `27017`) because `docker-compose.yml` maps `27018:27017`.

If you want the email notification feature to work, add these to your `.env`:

```
EMAIL_USER='iphylogeo@gmail.com'
EMAIL_PASSWORD='rogo lqhi fldu mwml'
```

### ▶️ Running

Make sure you are at the project root (iPhylogeo) and your virtual environment is activated.

On Windows:

```bash
venv\Scripts\activate
npm start
```

On Linux:

```bash
source venv/bin/activate
npm start
```

---

## 🕐 Using the cronJob

If the database is deployed on a Linux server, a script is included to delete files older than 14 days. Example `cronjob` file:

```bash
00 00 * * * /path/to/python /path/to/iPhyloGeo/scripts/delete_files.py >> /path/to/iPhyloGeo/scripts/cron.log 2>&1
```

To register the cron job:

```bash
crontab /path/to/iPhyloGeo/scripts/cronjob
```

🛠️ Useful tool for cron syntax: https://crontab.guru/

To list active cron jobs:

```bash
crontab -l
```

---

## 🎨 Generating a CSS file from SCSS

The project uses SCSS files compiled to CSS with the Node Sass CLI (no Grunt).

SCSS files should be placed in:

```
apps/assets/styles/your_file.scss
```

Then add the source/output pair in [scripts/sass_css.js](scripts/sass_css.js), inside the `PAIRS` array:

```js
["apps/assets/styles/your_file.scss", "apps/assets/your_file.css"];
```

Build CSS once:

```bash
npm run build:css
```

Watch SCSS changes and recompile automatically:

```bash
npm run watch:css
```

If you run `npm start`, CSS watching is already included via `dev:assets`.

> ⚠️ The CSS output file must be generated in the `apps/assets` folder, otherwise Dash will not load it.
