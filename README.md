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

#### 7. 🧬 Install external alignment tools (MUSCLE, ClustalW2, MAFFT, FastTree) (Optional but needed for all parameters to works)

These binaries are required if you select the `MUSCLE`, `CLUSTALW`, or `MAFFT` alignment method, or the `Fast Tree` tree type. They are **not** shipped with the `aphylogeo` Python package.

Download the Windows binaries:

- MUSCLE 5: https://drive5.com/muscle/downloads_v5.htm → `muscle5.1.win64.exe`
- ClustalW2: http://www.clustal.org/clustal2/ → `clustalw2.exe`
- MAFFT: https://mafft.cbrc.jp/alignment/software/windows.html → the `mafft-win/` folder
- FastTree: http://www.microbesonline.org/fasttree/#Install → `FastTree.exe`

On Windows, `aphylogeo` resolves these paths from the installed package location, so drop the files into your virtual environment's `site-packages`:

```
venv\Lib\site-packages\aphylogeo\bin\
├── muscle5.1.win64.exe
├── clustalw2.exe
├── mafft-win\
│   └── mafft.bat
├── FastTree.exe
└── tmp\          ← must exist (used for temporary FASTA files)
```

> ⚠️ If the `tmp\` folder is missing under `site-packages\aphylogeo\bin\`, create it manually. FastTree and the alignment helpers write temporary FASTA files there and will otherwise fail with a `FileNotFoundError`.

#### 8. 🐳 Start the database with Docker

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

#### 5. 🧬 Install external alignment tools (MUSCLE, ClustalW2, MAFFT, FastTree) (Optional but needed for all parameters to works)

These tools are required if you select the `MUSCLE`, `CLUSTALW`, or `MAFFT` alignment method, or the `Fast Tree` tree type. They are **not** shipped with the `aphylogeo` Python package.

**Option A — System-wide install via `apt` (simplest, recommended on Linux)**

```bash
sudo apt install muscle clustalw mafft fasttree -y
```

This puts the binaries in `/usr/bin/` (e.g. `/usr/bin/FastTree`, `/usr/bin/mafft`, …). For most Linux setups this is enough to run the pipeline.

> ℹ️ `aphylogeo` internally uses hardcoded paths like `aphylogeo/bin/<binary>` (cwd-relative on Linux/macOS — see the [TODO](#todo) section). If you hit a `FileNotFoundError` or `ApplicationError` complaining that the binary is missing, use Option B below, or add symlinks pointing to the system binaries:
>
> ```bash
> mkdir -p aphylogeo/bin
> ln -sf "$(command -v FastTree)"  aphylogeo/bin/FastTree
> ln -sf "$(command -v muscle)"    aphylogeo/bin/muscle5.1.linux_intel64
> ln -sf "$(command -v clustalw)"  aphylogeo/bin/clustalw2
> mkdir -p aphylogeo/bin/mafft-linux64
> ln -sf "$(command -v mafft)"     aphylogeo/bin/mafft-linux64/mafft.bat
> ```

**Option B — Manual binaries in `aphylogeo/bin/`**

Download the Linux binaries:

- MUSCLE 5: https://drive5.com/muscle/downloads_v5.htm → `muscle5.1.linux_intel64`
- ClustalW2: http://www.clustal.org/clustal2/ → `clustalw2`
- MAFFT: https://mafft.cbrc.jp/alignment/software/ → the `mafft-linux64/` folder
- FastTree: http://www.microbesonline.org/fasttree/#Install → `FastTree`

Place them at the iPhylogeo project root (`aphylogeo` resolves these paths relative to the current working directory):

```
iPhylogeo/aphylogeo/bin/
├── muscle5.1.linux_intel64
├── clustalw2
├── mafft-linux64/
│   └── mafft.bat
├── FastTree
└── tmp/
```

Make the binaries executable:

```bash
chmod +x aphylogeo/bin/muscle5.1.linux_intel64 \
         aphylogeo/bin/clustalw2 \
         aphylogeo/bin/FastTree
```

> ℹ️ iPhylogeo already creates `aphylogeo/bin/tmp/` at pipeline start to work around an `aphylogeo` path bug. See the [TODO](#todo) section.

#### 6. 🐳 Start the database with Docker

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

Open 2 terminals:

1. Terminal A (database services):

```bash
docker compose up
```

2. Terminal B (application):

`npm start` now launches the Dash app, Electron UI, asset watchers, and the RQ worker process.

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

The project uses SCSS files compiled to CSS with Dart Sass (the `sass` npm package).

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

---

## 🧪 Running the tests

Make sure the virtual environment is activated, then install Playwright and its browser binaries (required for e2e tests):

```bash
pip install playwright
python -m playwright install chromium
```

Then run all tests from the root of the project:

```bash
python -m pytest tests/
```

To run only unit tests:

```bash
python -m pytest tests/unit/
```

To run a specific test file:

```bash
python -m pytest tests/unit/test_enums.py
```

To run a single test:

```bash
python -m pytest tests/unit/test_enums.py::test_get_code_returns_expected_code
```

---

## TODO

The following are **upstream issues in `aphylogeo`** that affect `iPhylogeo`. They should be reported/fixed in `aphylogeo` itself — do **not** patch the installed package locally, as those changes would be lost on the next reinstall.

- **Sørensen-Dice similarity typo.** In `aphylogeo/alignement.py` (line 937), `td.sorencen(...)` should be `td.sorensen(...)`. As-is, selecting the `SorensenDice` similarity method raises `AttributeError: module 'textdistance' has no attribute 'sorencen'` and the genetic alignment job fails. Workaround for now: avoid the `SorensenDice` method in iPhylogeo settings until this is fixed upstream.
- **`step_size` is ignored.** In `slidingWindow()` (`aphylogeo/alignement.py` line 755), the sliding step is set to `Params.window_size` instead of `Params.step_size`. Changing `step_size` from iPhylogeo settings currently has no effect; the window width is also used as the stride. To be fixed upstream.
- **`aphylogeo/bin/tmp` path bug (Linux/macOS).** `createTmpFasta()`, `fasttree()`, and the MUSCLE/ClustalW helpers use the cwd‑relative path `aphylogeo/bin/tmp/` on Linux/macOS, while Windows uses a `__file__`‑relative absolute path. The proper upstream fix is to resolve temp paths from the package location (e.g. `Path(__file__).resolve().parent / "bin" / "tmp"`) on all platforms and to ensure that directory exists before any write/read/cleanup. Current workarounds on the iPhylogeo side (no change to `aphylogeo`):
  - Linux/macOS: iPhylogeo creates `./aphylogeo/bin/tmp/` at pipeline start in `create_genetic_trees()` (`os.makedirs("aphylogeo/bin/tmp", exist_ok=True)`).
  - Windows: the `tmp\` folder inside `…\site-packages\aphylogeo\bin\` must be created manually once (see the Windows install step).
