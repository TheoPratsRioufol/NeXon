import matplotlib.pyplot as plt
import numpy as np
import json

network_path = "./6 - PLS CADENCE/simus/Network.json"

networkFile = open(network_path)
network = json.load(networkFile)
networkFile.close()

def get_tuple_from_name(name):
    split = name.split('_')
    return (ord(split[0][0])-ord('a'), int(split[0][1:]),ord(split[1][0])-ord('a'), int(split[1][1:]))

def get_network_layer_info(network):
    syn_names = network.keys()
    layers = [0]*100
    for name in syn_names:
        tuple_name = get_tuple_from_name(name)    
        if (tuple_name[1] > layers[tuple_name[0]] - 1):
            layers[tuple_name[0]] = tuple_name[1] + 1
        if (tuple_name[3] > layers[tuple_name[2]] - 1):
            layers[tuple_name[2]] = tuple_name[3] + 1
    small_layer = []
    for i in layers[1:]:
        if i == 0:
            break
        small_layer.append(i)
    small_layer[0] = 2
    return small_layer

layers = get_network_layer_info(network)

print("Network have",len(layers),"layer(s) and max nb neuron per layer is",max(layers))

def get_syn_position(syn, layers):
    tuple_name = get_tuple_from_name(syn)
    return (tuple_name[3] + sum(layers[:tuple_name[0]]), tuple_name[1]-layers[tuple_name[0]-1]/2)


def plot_network(network):
    layers = get_network_layer_info(network)
    font_dic = {'size':9}
    for syn in network:
        tuple_name = get_tuple_from_name(syn)
        param_dic = network[syn]['CDS']['param']
        param = param_dic[list(param_dic.keys())[0]]/1000
        sign = network[syn]['TFw'] >= 0
        if (tuple_name[0] != 0):
            syn_position = get_syn_position(syn, layers)
            col = ['r','b','g','c','k']
            plt.text(syn_position[0]-0.06*len(syn), syn_position[1]+0.2, syn, fontdict=font_dic)
            disc = param == 0
            if not disc:
                plt.text(syn_position[0]-0.06*len(syn), syn_position[1]-0.2, str(round(param,3)), fontdict=font_dic)
                if sign:
                    plt.plot(syn_position[0], syn_position[1], 'ro')
                else:
                    plt.plot(syn_position[0], syn_position[1], 'bo')
            else:
                plt.plot(syn_position[0], syn_position[1], 'ko')
        else:
            xbias = sum(layers[:tuple_name[2]-1])+tuple_name[3]
            ybias = -3
            plt.text(xbias-0.06*len(syn), ybias+0.2, syn, fontdict=font_dic)
            if sign:
                sign = "+"
            else:
                sign = "-"
            plt.text(xbias-0.06*len(syn), ybias-0.2, sign+str(round(param,3)), fontdict=font_dic)
            plt.plot(xbias,ybias,'co')
    for idx in range(1,len(layers)):
        plt.plot([sum(layers[:idx])-0.5]*2,[-3,3],'k--')


plot_network(network)
plt.show()
