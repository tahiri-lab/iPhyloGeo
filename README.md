# iPhyloGeo

- Link for the french version : [french version](README.fr.md)

## Description:
### Data Visualization Interfaces in Python With Dash

The purpose of this application is to visualize the pipeline of Phylotree and to simplify its use.

https://github.com/tahiri-lab/phylogeography-algo


The project can be used in two ways:
1. Using the filesystem to store the files and results
2. Using a database to store the files and results

The first option is the default option. If you want to use the database, you need to change the .env file. See the section "Setting up the program" for more details.

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
5. Make sure your are in the aPhyloGeo directory, and install the aPhyloGeo package using `pip install -e .`.

For a windows based system, you can use the following commands:
1. git clone https://github.com/tahiri-lab/aPhylogeo
2. If you do not have `virtualenv` installed, run `python3 -m pip install --user virtualenv`
3. Create a new virtual environment (venv) in your terminal using `python3 -m venv aPhyloGeo_env`.
4. Still in the terminal, activate the new venv using `aPhyloGeo_env/Scripts/activate .`.
5. Make sure your are in the aPhyloGeo directory, and install the aPhyloGeo package using `pip install -e .`.


Then you can install the other requirements. Make sure you are using the same venv as above. Make sure youa re in the iPhyloGeo directory.
Then run the following commands :
```
pip install -r requirements.txt
npm install
```

Finally, if want to run the programm with a database, you need to install docker. You can find the installation guide here : https://docs.docker.com/get-docker/

- Folder apps: template for each web page
- Folder assets: images utilised in template and css file


### Setting up the programm
- To set up the programm, you need to chahge the .env file with your own data.
Here is an example of the .env file if you want to run the programm locally :
```
APP_ENV='dev'
HOST='local'
MONGO_URI=
DB_NAME=
URL='http://localhost'
PORT='8050'
```
- If you want to run the programm with a database, you need to change the .env. For example :
```
APP_ENV='dev'
HOST='server'
MONGO_URI='mongodb://localhost:27017'
DB_NAME='iPhyloGeo'
URL='http://localhost'
PORT='8050'
```
-If you wish for the email address function to operate correctly, you need to generate a "password.env" file within the directory path "iPhyloGeo\apps\pages\results\password.env" with the following format: GMAIL_PASSWORD=(insert application password of aphylogeotest@gmail.com here or the e-mail you want to use).


### Running
- To run the programm locally, you can use the following command :
```
npm start
```
- To run the programm with a database, you need to run the following commands :
```
docker compose up
npm start
```

### Using the cronJob

If the database is deployed on a linux server, we've included a script to delete the files that are older than 14 days. To do so, you need to create a cronjob.
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
