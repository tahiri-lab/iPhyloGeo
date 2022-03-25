
from ete3 import Tree, TreeStyle

def creer_un_arbre():
    print('creation un arbre')



#Utiliser dans une autre fonction

def lireNewick():
    with open('WS10M_newick.txt') as f:
        lines = f.readlines()
        myTree = Tree(lines)
        ts = TreeStyle()
        print(lines)
        ts.show_leaf_name = True
        ts.show_branch_length = True
        ts.show_branch_support = True
        #>> > t.show(tree_style=ts)

        f.close()

    #f = open(dictionary_name, "w+")
    #f.write(jsonString)
    #f.close()
    #lire un fichier
    #read(fname)
    #contenue de ce fichier
    #creer un arbre t = Tree(contenue)
    #donner le style a tree
    #rendre() dans une image
    if lireNewick == '/tree/create_tree':
        return lireNewick.py
    if lireNewick == '/tree/prepareDirectory':
        return lireNewick.py