# Phylogeo_frelon

- Link for the french version : [french version](README.fr.md)

## Description:
### Data Visualization Interfaces in Python With Dash

The purpose of this application is to visualize the pipeline of Phylotree and to simplify its use.

https://github.com/tahiri-lab/phylogeography-algo

## Getting started

### Installing:

* First the programm need to be downloaded with Github(git clone command). 
```
git clone https://github.com/tahiri-lab/iPhylogeo
```

To download the project simply type one of the command above in a terminal.
* You can also download the zip file with the Github link above.

## How to use?
### Prerequisites,library etc.
Before using this program make sure that you have installed all the necessary libraries for it to work properly. 
First, you need to install the aPhyloGeo package. Depending on your OS, the specific commands will be slightly 
diffrent. Fof a linux based system, you can use the following commands:

1. git clone https://github.com/tahiri-lab/aPhylogeo
2. If you do not have `virtualenv` installed, run `python3 -m pip install --user virtualenv`
3. Create a new virtual environment (venv) in your terminal using `python3 -m venv aPhyloGeo_env`.
4. Still in the terminal, enter the new venv using `source aPhyloGeo_env/bin/activate`.
5. Make sure your are in the aPhyloGeo directory, and install the aPhyloGeo package using `pip -e install .`.

Fof a windows based system, you can use the following commands:
1. git clone https://github.com/tahiri-lab/aPhylogeo
2. If you do not have `virtualenv` installed, run `py -m pip install --user virtualenv`
3. Create a new virtual environment (venv) in your terminal using `py -m venv aPhyloGeo_env`.
4. Still in the terminal, activate the new venv using `aPhyloGeo_env/bin/activate .`.
5. Make sure your are in the aPhyloGeo directory, and install the aPhyloGeo package using `pip -e install .`.


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
