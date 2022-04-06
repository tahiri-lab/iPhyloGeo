import subprocess
import os
import re
import pandas as pd
from csv import writer
import shutil
from requests import get

# ATTENTION AUX NOMS DES FICHIERS AVEC LES 
'''
bootstrap_threshold = 0
rf_threshold = 100
window_size = 200
step_size = 50 
data_names = ["QV2M_newick",
              "RH2M_newick", "WS10M_newick"]
reference_gene_file = '../input/reference_gene.fasta'

'''
#-----------------------------------------  
def prepareDirectory():
    path_output_windows = 'user/example/output/seq/windows'                            
    isExist = os.path.exists(path_output_windows)

    if isExist:
        for f in os.listdir(path_output_windows):
            os.remove(os.path.join(path_output_windows, f))
    else:
        os.makedirs(path_output_windows)

    # delete the results of last analysis, if we have    
    delete_path = os.listdir('user/example/output/seq')

    for item in delete_path:
        if item.endswith("_gene"):
            shutil.rmtree('user/example/output/seq'+'/'+item)
        

    delete_path2 = 'user/example/output/'

    for item in delete_path2:
        if item == "output.csv" or item.startswith("RAxML_") or item.startswith("outtree"):
            os.remove(item)
    
    with open('user/example/output/output.csv', 'w') as f:
        f.write("Gene,Arbre phylogeographique,Position ASM,Bootstrap moyen,RF normalise\n")

#prepareDirectory()

#--------------------------------------------------------------
#'1. Use the whole DNA sequences'

# main function

def createPhylogeneticTree(reference_gene_file, window_size, step_size, bootstrap_threshold, rf_threshold, data_names):
    prepareDirectory()
    os.chdir('user/example/output/')       #Requires access to the specific 'output' folder
    number_seq = alignSequences(reference_gene_file)
    slidingWindow(window_size, step_size)
    files = os.listdir("seq/windows")       
    for file in files:
        os.system("cp seq/windows/" + file + " infile")
        createBoostrap()
        createDistanceMatrix()
        createUnrootedTree()
        createConsensusTree() # a modifier dans la fonction
        filterResults(reference_gene_file, bootstrap_threshold, rf_threshold, data_names, number_seq, file)
    os.chdir('../../..')      #Change back to the previous run folder

#---------
'''
def getIpAdress():
    ip = get("https://api.ipify.org").text
    return ip
'''
#-----------------------------------
def alignSequences(reference_gene_file):
    subprocess.call(["../../../exec/muscle", "-in", reference_gene_file, "-physout", "infile", "-maxiters", "1", "-diags"])
    f = open("infile", "r").read()
    number_seq = int(f.split()[0])
    return number_seq

# number_seq = alignSequences(reference_gene_file)

# print(number_seq)

#-------------------------------------------------

def slidingWindow(window_size=0, step=0):
    # Permet d'avoir le nombre de lignes totales dans le fichier
    try:
        f = open("infile", "r")
        line_count = -1
        for line in f:
            if line != "\n":
                line_count += 1
        f.close()
        f = open("infile", "r").read()
        # premier nombre de la premiere ligne du fichier represente le nbr de sequences
        num_seq = int((f.split("\n")[0]).split(" ")[0])
        # second nombre de la premiere ligne du fichier represente la longueur des sequences
        longueur = int((f.split("\n")[0]).split(" ")[1])
        # permet d'obtenir le nbr de lignes qui compose chaque sequence
        no_line = int(line_count/num_seq)

        # Recupere la sequence pour chaque variante
        with open("outfile", "w") as out:
            depart = 1
            fin = depart + no_line
            # on connait la longueur de chaque sequence, 
            # donc on va recuperer chaque sequence et le retranscrire sur un autre fichier separes par un \n entre chaque
            for i in range(0, int(num_seq)):
                f = open("infile", "r")
                lines_to_read = range(depart, fin)
                for position, line in enumerate(f):
                    if position in lines_to_read:
                        out.write(line)
                out.write("\n")
                depart = fin
                fin = depart + no_line
        out.close()  

        # on cree un fichier out qui contient chaque sequence sans espaces 
        # et on enregistre dans une list le nom en ordre des sequences
        with open("outfile", "r") as out, open("out", "w") as f:
            sequences = out.read().split("\n\n")
            list_names = []
            for seq in sequences:
                s = seq.replace("\n", " ").split(" ")
                if s[0] != "":
                    list_names.append(s[0])
                s_line = s[1:len(seq)]
                for line in s_line:
                    if line != "":
                        f.write(line)
                f.write("\n")
        out.close()  
        f.close()

        # slide the window along the sequence
        debut = 0
        fin = debut + window_size
        while fin <= longueur:
            index = 0 
            with open("out", "r") as f, open("seq/windows/" + str(debut) + "_" + str(fin), "w") as out:
                out.write(str(num_seq) + " " + str(window_size) + "\n")
                for line in f:
                    if line != "\n":
                        espece = list_names[index]
                        nbr_espaces = 11 - len(espece)   
                        out.write(espece)
                        for i in range(nbr_espaces):
                            out.write(" ")
                        out.write(line[debut:fin] + "\n")
                        index = index + 1
            out.close()
            f.close()
            debut = debut + step
            fin = fin + step             
    except:
        print("An error occurred.")

    # clean up
    os.system("rm out outfile infile")

def createBoostrap():
    os.system("../../../exec/seqboot < ../../../parameter/bootstrap_input.txt")
    subprocess.call(["mv", "outfile", "infile"])

def createDistanceMatrix():
    os.system("../../../exec/dnadist < ../../../parameter/dnadist_input.txt")
    subprocess.call(["mv", "outfile", "infile"])

def createUnrootedTree():
    os.system("../../../exec/neighbor < ../../../parameter/neighbor_input.txt")
    subprocess.call(["rm", "infile", "outfile"])
    subprocess.call(["mv", "outtree", "intree"])


def createConsensusTree():
    os.system("../../../exec/consense < ../../../parameter/input.txt")
    # subprocess.call(["mv", "outtree", file])
    subprocess.call(["rm", "intree", "outfile"])

def filterResults(gene, bootstrap_threshold, rf_threshold, data_names, number_seq, aligned_file):
    bootstrap_average = calculateAverageBootstrap()
    if bootstrap_average < float(bootstrap_threshold):
        subprocess.call(["rm", "outtree"])
    else:
        for tree in data_names:
            print(tree)
            calculateRfDistance(tree)
            rfn = standardizedRfDistance(number_seq)
            if rfn == None:                 #  '<=' not supported between instances of 'NoneType' and 'int'
                rfn = 100                     # fix it 
            if rfn <= rf_threshold:
                runRaxML(aligned_file, gene, tree)
                cleanUp(aligned_file, tree)
                bootstrap_rax = calculateAverageBootstrapRax()
                if bootstrap_rax < float(bootstrap_threshold):
                    continue
                else:
                    calculateRfDistance(tree)
                    rfn_rax = standardizedRfDistance(number_seq)
                    if rfn_rax == None:     #  '<=' not supported between instances of 'NoneType' and 'int'
                        rfn_rax = 100         # fix it 
                    if rfn_rax <= rf_threshold:
                        gene_name = gene.split("/")[2].split(".")[0]
                        addToCsv(gene_name, tree, aligned_file, bootstrap_rax, rfn_rax)
                        keepFiles(gene, aligned_file, tree)
                        # a verifier ici
        subprocess.call(["rm", "outtree"])

def calculateAverageBootstrap():
    total = 0
    f = open("outtree", "r").read()
    numbers = re.findall(r'[)][:]\d+[.]\d+', f)
    for number in numbers:
        total = total + float(number[2:])
    average = total / len(numbers)
    return average

def calculateRfDistance(tree):
    os.system("cat " + tree + " >> infile")
    os.system("cat outtree >> infile")
    os.system("../../../exec/rf infile outfile tmp matrix")

def standardizedRfDistance(number_seq):
    # clean up the repository
    subprocess.call(["rm", "infile", "matrix", "tmp"])
    # find the rf
    f = open("outfile", "r").read()
    words = re.split(r'[ \n]', f)
    for i in range(len(words)):
        if words[i] == "=":
            rf = int(words[i+1])
            normalized_rf = (rf/(2*number_seq-6))*100
            subprocess.call(["rm", "outfile"])
            return normalized_rf

def runRaxML(aligned_file, gene, tree):
    current_dir = os.getcwd()
    file_name = os.path.basename(aligned_file + "_" + tree)
    input_path = os.path.join(current_dir, "seq", "windows", aligned_file)
    # output_path = os.path.join(current_dir, "output", gene + "_gene")
    # IL FAUT CHANGER LE MODELE SELON LE GENE CHOISI
    os.system("../../../exec/raxmlHPC -s " + input_path + " -n " + file_name + " -N 100 -m GTRGAMMA -x 123 -f a -p 123")
    # output_path = os.path.join(output_path, file_name)
    # subprocess.call(["cp", input_path, output_path])

def cleanUp(file, tree):
    file = "RAxML_bipartitionsBranchLabels."+file+"_"+tree
    # directory = os.path.join("output", gene + "_gene", file)
    subprocess.call(["mv", file, "outtree"])
    files_to_delete = ['*bipartitions.*', '*bootstrap*', '*info*', '*bestTree*']
    for file in files_to_delete:
        os.system("rm -rf " +file)

def calculateAverageBootstrapRax():
    total = 0
    f = open("outtree", "r").read()
    numbers = re.findall(r'[\[]\d+[\]]', f)
    for number in numbers:
        total = total + float(number[1:(len(number)-1)])
    average = total / len(numbers)
    return average

def addToCsv(gene, tree, file, bootstrap_average, rfn):
    list = [gene, tree, file, bootstrap_average, rfn]
    with open('output.csv', 'a') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(list)
        f_object.close()

def keepFiles(gene, aligned_file, tree):
    current_dir = os.getcwd()
    file_name = os.path.basename(aligned_file + "_" + tree + "_tree")
    input_path = os.path.join(current_dir, "output", "windows", aligned_file)
    output_path = os.path.join(current_dir, "output", gene + "_gene")
    tree_path = os.path.join(output_path, file_name)
    subprocess.call(["cp", input_path, output_path]) # on garde l'ASM initial
    subprocess.call(["cp", "outtree", tree_path]) # on transfere l'arbre a garder dans le bon fichier
    subprocess.call(["mv", "seq/windows/"+aligned_file+".reduced", output_path])


#createPhylogeneticTree(reference_gene_file, window_size, step_size, bootstrap_threshold, rf_threshold, data_names)

#displayGenesOption(window_size, step_size, bootstrap_threshold, rf_threshold, data_names,genes_chosen)
