# Librairie pour lire proprement les fichiers spectre

import os
import numpy as np
import csv

# Y'a le cas pb IT("/IB/IN") à gérer

Paterns = {"multi_traces":["*-X/Y","*-(-*-)-X/Y"],
           "adexl_1var":["*-(-*-=-*-)-X/Y"]}

delimiters = ['=', '(', ')']

def type_(str):
    if (str in ['(', ')', '=']):
        return str
    if (str in ['X', 'Y']):
        return 'X/Y'
    else:
        return '*'

class SReader:
    def __init__(self):
        self.run_path = os.path.dirname(os.path.abspath(__file__))
        self.begin_path = self.run_path
        self.courbes = {}

    def read(self,path):
        # Il faut intelligement savoir à quoi ressemble le fichier pour le traiter correctement :
        # Plusieurs courbe avec absycces partagée ?
        # Run adexl ?
        # etc...
        # Et savoir dans quelle forme le sauvegarder (discriminant = value ou name...)
        """
        Run ADEXL (1 variable) : "NAME (PARAMETER=VALUE) X -> dic {value:{X:[], Y:[]}}"
        Run PARTAGES : "NAME X", "NAME Y -> dic {name:{X:[], Y:[]}}"
        """
        PatIdentified = ''
        with open(self.begin_path + '/'+ path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            firstrow = next(csv_reader)
            for elm in delimiters:
                firstrow[0] = firstrow[0].replace(elm,' '+elm+' ')
            firstrow[0] = firstrow[0].replace('  ',' ')
            firstelm = firstrow[0].split(' ')
            for pat in Paterns:
                for idxseq in range(len(Paterns[pat])):
                    Sequence = Paterns[pat][idxseq].split('-')
                    matched = 0
                    for i in range(min(len(Sequence),len(firstelm))):
                        #print(firstelm[i],'<==>',Sequence[i])
                        if (type_(firstelm[i]) == Sequence[i]):
                            matched += 1
                    if (matched == len(Sequence)):
                        if (PatIdentified != ''):
                            raise Exception("More than one patern has been identified : ",PatIdentified," and ",matched)
                        PatIdentified = pat
        if (PatIdentified == ''):
            raise Exception("No patern found to exploit .csv")
        Method = getattr(self, PatIdentified)
        print("Extraction for",PatIdentified)
        Method(path)
        print("DONE !")

    def adexl_1var(self, path):
        self.courbes = {}
        # Marche pour les courbes à 1 corners
        # Renvoie un dictionaire avec pour clée la valeur du corner et en atribue les listes X et Y
        paramtxt = ''
        with open(self.begin_path + '/'+ path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            start = 1
            for row in csv_reader:
                if (start):
                    start = 0
                    # La première ligne est de la forme : r (W=1) X, r (W=1) Y, r (W=2) X, r (W=2) Y
                    for idx in range(len(row)):
                        colum = row[idx]
                        if (colum[-1] == 'Y'):
                            # On extrait la valeur du corners
                            val = float(colum.split('=')[1].split(')')[0])
                            self.courbes[val]['Yidx'] = idx
                            self.courbes[val]['Y'] = []
                        elif (colum[-1] == 'X'):
                            val = float(colum.split('=')[1].split(')')[0])
                            self.courbes[val] = {'Xidx':idx, 'X':[], 'Yidx':idx, 'Y':[]}
                    paramtxt = row[1].split('=')[0].split('(')[-1]
                else:
                    # On remplie pour tous les corners identifiés
                    for c in self.courbes:
                        try:
                            self.courbes[c]['X'].append(float(row[self.courbes[c]['Xidx']]))
                            self.courbes[c]['Y'].append(float(row[self.courbes[c]['Yidx']]))
                        except:
                            pass
        # Puis on numpérise
        for c in self.courbes:
            self.courbes[c]['X'] = np.array(self.courbes[c]['X'])
            self.courbes[c]['Y'] = np.array(self.courbes[c]['Y'])
        print("Parameter detected :",paramtxt)

    def multi_traces(self, path):
        # Pour charger des courbes multiples sur un adel
        # de la forme /I0/MINUS X,/I0/MINUS Y,/I11/MINUS X,/I11/MINUS Y etc
        self.courbes = {}
        # Marche pour les courbes à 1 corners
        # Renvoie un dictionaire avec pour clée la valeur du corner et en atribue les listes X et Y
        with open(self.begin_path + '/'+ path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            start = 1
            for row in csv_reader:
                if (start):
                    start = 0
                    # La première ligne est de la forme : r (W=1) X, r (W=1) Y, r (W=2) X, r (W=2) Y
                    for idx in range(len(row)):
                        colum = row[idx]
                        if (colum[-1] == 'Y'):
                            # On extrait la piste
                            self.courbes[colum[:-2]]['Yidx'] = idx
                        elif (colum[-1] == 'X'):
                            self.courbes[colum[:-2]] = {'Xidx':idx, 'X':[], 'Yidx':0, 'Y':[]}
                else:
                    # On remplie pour tous les corners identifiés
                    for c in self.courbes:
                        try:
                            self.courbes[c]['X'].append(float(row[self.courbes[c]['Xidx']]))
                            self.courbes[c]['Y'].append(float(row[self.courbes[c]['Yidx']]))
                        except:
                            pass
        # Puis on numpérise
        for c in self.courbes:
            self.courbes[c]['X'] = np.array(self.courbes[c]['X'])
            self.courbes[c]['Y'] = np.array(self.courbes[c]['Y'])