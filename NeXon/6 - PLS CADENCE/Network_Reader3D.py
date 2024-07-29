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
    #plt.title("Image par le réseau Cadence")
    #plt.xlabel("Temporel")
    #plt.ylabel("Corners")
    #plt.imshow(img)
    return img


#plt.subplot(1,1,1)
ImgNetwork = plot_grid(folder_path + "FullPLS_standard.csv")
acc,rseuil = get_max_accuracy(ImgNetwork, TargetImg)
print("Max Acc = ",acc,rseuil)

seuil = rseuil*(np.max(ImgNetwork) - np.min(ImgNetwork)) + np.min(ImgNetwork)

#plt.title("CDS")


from mpl_toolkits.mplot3d import Axes3D

image_data = np.array(ImgNetwork)*1e12

x = np.linspace(0, image_data.shape[1], image_data.shape[1])
y = np.linspace(0, image_data.shape[0], image_data.shape[0])
x, y = np.meshgrid(x, y)
z = np.ones_like(x)*seuil*1e12  

level = np.abs(z-image_data) < 4
#print(level)

fig = plt.figure()
fig.set_size_inches(3.5,3.5)
ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(x, y, image_data, cmap='plasma')
ax.plot_surface(x, y, z, alpha=0.2, rstride=100, cstride=100, color='black')


#ax.plot(x[level],y[level],z[level],zorder=10, marker='o', color='k', alpha=0.3, linestyle='')
zi = z[level]
zii =  [zi[i] for i in range(1,len(zi),2)] + [zi[i] for i in range(0,len(zi),2)]
ax.plot(x[level],y[level],zii,zorder=10, color='k', alpha=0.3, linestyle='-')

#ax.plot_surface(x,y,level*seuil*1e12,zorder=10, alpha=0.8, color='red')

#ax.plot_wireframe(x[indices], y[indices], zinter[indices], color='red')

ax.view_init(45,45)
 

ax.set_xlabel('Vx [V]')
ax.set_ylabel('Vy [V]')
ax.set_zlabel('Out [pA]')
ax.set_title('Network Output')
plt.show()