import subprocess
import pandas as pd
import os
import pathlib
from requests import get


'''
file_name = "donnees.csv"

specimen = 'sequence_ID'   #"Please enter the name of the colum containing the specimens names: "

names = ['sequence_ID','QV2M',
        'RH2M',
        'WS10M']
'''
#--------------------------------------
def prepareDirectory():
    #create user's files 
    #user_input = 'user/'  + getIpAdress() +'/input' 
    #user_output = 'user/'  + getIpAdress() +'/output' 
    #os.makedirs(user_input)
    #os.makedirs(user_output)

    # delete the results of last analysis, if we have
    intree = 'user/example/output/' + 'intree'
    with open(intree, "w"):
        pass
    # remove old newick files
    os.chdir('user/example/output/')
    delete_path = os.listdir()

    for item in delete_path:
        if item.endswith("_newick"):
            os.remove(item)
    os.chdir('../../..')

    if os.path.exists("output/upload_gene.fasta") :
        os.remove("output/upload_gene.fasta")

def getIpAdress():
    ip = get("https://api.ipify.org").text
    return ip
#-----------------------------------------

def getDissimilaritiesMatrix(nom_fichier_csv, column_with_specimen_name, column_to_search, outfile_name):
    df = pd.read_csv('user/example/input/' + nom_fichier_csv)
    # creation d'une liste contenant les noms des specimens et les temperatures min
    meteo_data = df[column_to_search].tolist()
    nom_var = df[column_with_specimen_name].tolist()
    nbr_seq = len(nom_var)
    # ces deux valeurs seront utiles pour la normalisation
    max_value = 0
    min_value = 0

    # premiere boucle qui permet de calculer une matrice pour chaque sequence
    temp_tab = []
    for e in range(nbr_seq):
        # une liste qui va contenir toutes les distances avant normalisation
        temp_list = []
        for i in range(nbr_seq):
            maximum = max(float(meteo_data[e]), float(meteo_data[i]))
            minimum = min(float(meteo_data[e]), float(meteo_data[i]))
            distance = maximum - minimum
            temp_list.append(float("{:.6f}".format(distance)))

        # permet de trouver la valeur maximale et minimale pour la donnee meteo et ensuite d'ajouter la liste temporaire a un tableau
        if max_value < max(temp_list):
            max_value = max(temp_list)
        if min_value > min(temp_list):
            min_value = min(temp_list)
        temp_tab.append(temp_list)

    # ecriture des matrices normalisees dans les fichiers respectifs
    with open(outfile_name, "w") as f:
        f.write("   " + str(len(nom_var)) + "\n")
        for j in range(nbr_seq):
            f.write(nom_var[j])
            # petite boucle pour imprimer le bon nbr d'espaces
            for espace in range(11-len(nom_var[j])):
                f.write(" ")
            for k in range(nbr_seq):
                # la normalisation se fait selon la formule suivante: (X - Xmin)/(Xmax - Xmin)
                f.write("{:.6f}".format(
                    (temp_tab[j][k] - min_value)/(max_value - min_value)) + " ")
            f.write("\n")
    #subprocess.call(["rm", "outfile"])  # clean up

#-----------------------------------------

def create_tree(file_name, names):
    prepareDirectory()
    infile = 'user/example/output/' + 'infile'
    intree = 'user/example/output/' + 'intree'
    print(infile)
    for i in range(1, len(names)):
        getDissimilaritiesMatrix(file_name, names[0], names[i], infile) # liste a la position 0 contient les noms des specimens
        os.chdir('user/example/output/')       #Requires access to the specific 'output' folder
        os.system("../../../exec/neighbor < ../../../parameter/input.txt")
        subprocess.call(["mv", "outtree", intree])
        subprocess.call(["rm", infile, "outfile"])
        os.system("../../../exec/consense < ../../../parameter/input.txt" )
        newick_file = names[i].replace(" ", "_") + "_newick"
        subprocess.call(["rm", "outfile"])
        subprocess.call(["mv", "outtree", newick_file])
        os.chdir('../../..')      #Change back to the previous run folder before the next loop
    subprocess.call(["rm", intree])

#----------------------------------------


#create_tree(file_name, names)

#prepareDirectory()
