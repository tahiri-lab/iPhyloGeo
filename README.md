# 🌳 iPhyloGeo

## Web application for analyzing phylogenetic trees with climatic parameters

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

#### 7. 🐳 Start the database and the Redis with Docker

Install [Docker Desktop](https://docs.docker.com/get-docker/), then start the containers in the background:

```bash
docker compose up -d
```

```
docker run -d --name redis -p 6379:6379 redis:alpine
```

### ⚙️ Setting up the program

Edit the `.env` file at the root of the project:

```
APP_ENV='dev'
HOST='server'
MONGO_URI='mongodb://localhost:27017'
DB_NAME='iPhyloGeo'
URL='http://localhost'
PORT='8050'
```

If you want the email feature to work, create a `password.env` file in `iPhyloGeo\apps\pages\results\`:

```
GMAIL_PASSWORD=(insert application password of aphylogeotest@gmail.com or the email you want to use)
```

### ▶️ Running

On Windows, in the root of the project:

```bash
venv\Scripts\activate
```

```bash
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
