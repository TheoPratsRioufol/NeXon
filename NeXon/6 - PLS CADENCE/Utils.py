import numpy as np
import csv

def get_idx_in_time(times, time):
    for idx, val in enumerate(times, 0):
        if (val > time):
            return idx
    return len(times)-1

def read_simu_file(path, deli=',', quotechr='|'):
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=deli, quotechar=quotechr)
        firstline = True
        SignalsDic = {}
        NamesRow = []
        for row in reader:
            if firstline:
                NamesRow = row
                for elm in NamesRow:
                    SignalsDic[elm] = []
            else:
                for idx in range(len(NamesRow)):
                    try:
                        SignalsDic[NamesRow[idx]].append(float(row[idx]))
                    except:
                        SignalsDic[NamesRow[idx]].append(None)
            firstline = False
    return SignalsDic

def get_perfect_img(Ngrid):
        rho = np.sqrt(2/np.pi)
        def in_ref(x):
                return 2*x/(Ngrid-1) - 1
        TargetImg = np.zeros((Ngrid,Ngrid))
        for x in range(Ngrid):
                for y in range(Ngrid):
                        if (np.sqrt(in_ref(x)**2 + in_ref(y)**2) < rho**2):
                                TargetImg[x,y] = 1
        return TargetImg

TargetImg = get_perfect_img(20)

def get_accuracy(ImgNetwork, TargetImg):
        vrai_positif = np.logical_and(TargetImg, ImgNetwork)
        vrai_négatif = np.logical_and(np.logical_not(TargetImg), np.logical_not(ImgNetwork))
        return (np.sum(vrai_positif)+np.sum(vrai_négatif))/(vrai_positif.shape[0]**2)

def get_accuracy_at_level(ImgNetwork, TargetImg, level_):
    ImgNetwork_cut = np.where(ImgNetwork < level_, np.zeros_like(ImgNetwork), np.ones_like(ImgNetwork))
    return get_accuracy(ImgNetwork_cut, TargetImg)

def get_max_accuracy(ImgNetwork, TargetImg):
        # Return the accuracy for the optimal treashold
        max_acc = 0
        seuil_max_acc = 0
        max_ = np.max(ImgNetwork)
        min_ = np.min(ImgNetwork)
        for i in np.linspace(0,1,20):
                # On coupe 
                level_ = min_ + i*(max_ - min_)
                acc = get_accuracy_at_level(ImgNetwork, TargetImg, level_)
                if (acc > max_acc):
                        max_acc = acc
                        seuil_max_acc = i
        return max_acc, seuil_max_acc


def get_img(img_trace, N=20):
    img = np.zeros((N,N))
    loop = 0
    for idxy, vy in enumerate(img_trace):
        for idxx, i in enumerate(np.linspace(0,0.001,N)):
            idx = get_idx_in_time(img_trace[vy]['X'], i)
            img[idxx, idxy] = img_trace[vy]['Y'][idx]
        loop += 1
    return img