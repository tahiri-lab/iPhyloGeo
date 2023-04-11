# Phylogeo_frelon

- Link for the french version : [french version](README.fr.md)

## Description:
### Data Visualization Interfaces in Python With Dash

The purpose of this application is to visualize the pipeline of Phylotree and to simplify its use.

https://github.com/tahiri-lab/phylogeography-algo

## Getting started

### Installing:

* First the programm need to be downloaded with Github(git clone command). 
* Second you need to choose with witch operating system you want to run the programm.
Mac OS(main), Linux, or Windows.
* Last step to download the programm. We need to clone the project with the git clone command.
* For Macbook(MacOSX) users (main branch in our case) use this command :
```
git clone -b "main" https://github.com/tahiri-lab/iPhylogeo
git clone -b "main" https://github.com/tahiri-lab/aPhylogeo
```
* For windows user use this command :
```
git clone -b "Windows" https://github.com/tahiri-lab/iPhylogeo
git clone -b "Windows" https://github.com/tahiri-lab/aPhylogeo
```
* For Linux user use this command :
```
git clone -b "Linux" https://github.com/tahiri-lab/iPhylogeo
git clone -b "Linux" https://github.com/tahiri-lab/aPhylogeo
```

To download the project simply type one of the command above in a terminal.
* You can also download the zip file with the Github link above.

## How to use?
### Prerequisites,library etc.
Before using this program make sure that you have installed all the necessary libraries for it to work properly. 
First, you need to install the aPhyloGeo package. To do this, you can use the following commands:

1. If you do not have `virtualenv` installed, run `python3 -m pip install --user virtualenv`
2. Create a new virtual environment (venv) in your terminal using `python3 -m venv aPhyloGeo_env`.
3. Still in the terminal, enter the new venv using `source aPhyloGeo_env/bin/activate`.
4. Install the package using `pip -e install .`.

Then you can install the other requirements (make sure you are using the same venv as above) : 
```
pip install -r requirements.txt
npm install
```

- Using index.py to star the program
- tree.py pipeline.py and pipeline_specific_genes.py are the algorithme
- Folder apps: template for each web page
- Folder assets: images utilised in template and css file
- Folder datasets: Meteorological data used in the analysis
- Folder exec: Biological software used in the analysis
- Folder input: Parameters used when using biology software
- Folder output: This folder is used to store the analysis results


### Setting up the programm
- To set up the programm, you need to chahge the .env file with your own data. 
Here is an example of the .env file :
```
APP_MODE='local'
MONGO_URI='mongodb://localhost:27017/iPhyloGeo'
DB_NAME='iPhyloGeo'
URL='http://localhost'
PORT='8050'
```

### Running
- To run the programm :
```
npm start
```
