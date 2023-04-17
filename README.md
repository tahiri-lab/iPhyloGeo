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
5. Make sure your are in the aPhyloGeo directory, and install the aPhyloGeo package using `pip install -e .`.


Then you can install the other requirements. Make sure you are using the same venv as above. Make sure youa re in the iPhyloGeo directory.
Then run the following commands :
```
pip install -r requirements.txt
npm install
```

Finally, you need to install. You can find the installation guide here : https://docs.docker.com/get-docker/

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
docker compose up
npm start
```
### Using the cronJob
To create a cron job, you can use the `cronjob` as a template.
For exemple create a file named `cronjob` and add the following line:
```bash
00 00 * * * /home/local/USHERBROOKE/belm1207/miniconda3/envs/geo/bin/python /home/local/USHERBROOKE/belm1207/iPhyloGeo/scripts/delete_files.py >> /home/local/USHERBROOKE/belm1207/iPhyloGeo/scripts/cron.log 2>&1
```
To create the cronjob with the file, you can use the following command:
```bash
crontab /home/local/USHERBROOKE/belm1207/iPhyloGeo/scripts/cronjob
```

This will run the script every day at 00:00 am.

1. The first element of the cronjob is the time. [Usefull tools](https://crontab.guru/)
2. The second element is the path of the python executable. In this case, we use geo environment from conda
3. The third element is the full path of the script file
4. The fourth element is the full path of the log file. This is optional, but it is a good practice to log the output of the script

To create the cronjob with the file, you can use the following command:
```bash
crontab /home/local/USHERBROOKE/belm1207/iPhyloGeo/scripts/cronjob
```

If you want to see the list of cronjobs, you can use the following command:
```bash
crontab -l
```

## How to generate CSS file?
### Understanding the structure of the project

* The project use SCSS files witch need to be created in the styles folder.
```
apps/assets/styles/your_file.scss
```
* Dash dosen't use SCSS files directly, so you need to generate a CSS file from the SCSS file. To do so, you need to include it in the Gruntfile.js file.
```
./Gruntfile.js 
```
* In the Gruntfile.js file, you need to add the following code in the dist section. `the desire output` : `the SCSS file location`

*The CSS files need to be generated in the **assets** folder, otherwise it won't work*
```
 [...]
 
 dist: {
                files: {
                    'apps/assets/your_file.css': 'apps/assets/styles/your_file.scss'
                }
 [...]
```
* In the Gruntfile.js file, you also need to add the following code in the watch/sass/files section. `the desire output`

*The watch section is necessary to regenerate the CSS file when is detected change in the SCSS files, it will also regenerate all CSS files on `npm start`*

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