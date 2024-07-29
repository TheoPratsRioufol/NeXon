import numpy as np
import matplotlib.pyplot as plt
import csv
from Utils import *


folder_path = "./6 - PLS CADENCE/simus/"
simu_path = folder_path + "NeXon_Network_out.csv"

def get_slices(SignalsDic):
    corners_dic = {}
    for trace in SignalsDic:
        if (trace[-2:] == " Y"):
            # On récupère le corners
            name = trace[:]
            corners_val = float(name.split(')')[0].split('=')[-1])
            corners_dic[corners_val] = {'Y':SignalsDic[trace], 'X':SignalsDic[trace[0:-2]+" X"]}
    return corners_dic

def get_none_idx(array):
    for i, val in enumerate(array, start=0):
        if (val == None):
            return i
    return len(array)

def get_bounds(corners_dic):
    data = corners_dic[list(corners_dic.keys())[0]]
    noneIdx = get_none_idx(data['X'])
    datax = data['X'][:noneIdx]
    return (min(datax), max(datax))

def get_pixel_slice(data, N, minx, maxx):
    dx = (maxx - minx)/N
    xtarget = minx
    datax = data['X']
    prevdiff = maxx - minx
    maxerr = 0
    slice_ = []
    for idx in range(len(data['X'])):
        if (datax[idx] == None):
            break
        if (abs(datax[idx] - xtarget) > prevdiff):
            xtarget += dx
            slice_.append(data['Y'][idx-1])
            maxerr = max(maxerr, prevdiff)
        prevdiff = abs(datax[idx] - xtarget)
    return maxerr, np.array(slice_)


def plot_grid(simu_path):
    SignalsDic = read_simu_file(simu_path)
    corners_dic = get_slices(SignalsDic)
    minx, maxx = get_bounds(corners_dic)
    sorted_slice = sorted(list(corners_dic.keys()))
    Nslice = len(sorted_slice)
    img = []
    maxerr = 0
    for sl in sorted_slice:
        err, slic = get_pixel_slice(corners_dic[sl], Nslice, minx, maxx)
        maxerr = max(err, maxerr)
        img.append(slic)
    print("Erreur maximale axe temporel =",maxerr,"relative =",round(maxerr/((maxx - minx)/Nslice),3))

    img = np.array(img)
    print("^=",round((np.max(img)-np.min(img))/1e-12,2),"pA")
    plt.title("Image par le réseau Cadence")
    plt.xlabel("Temporel")
    plt.ylabel("Corners")
    plt.imshow(img)
    return img


plt.subplot(1,1,1)
ImgNetwork = plot_grid(folder_path + "FullPLS_standard.csv")
print("Max Acc = ",get_max_accuracy(ImgNetwork, TargetImg))

plt.title("CDS")

plt.show()