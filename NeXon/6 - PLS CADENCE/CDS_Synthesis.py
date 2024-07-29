import matplotlib.pyplot as plt
import numpy as np
import json
import csv
from Utils import *
# Resolving import
import sys
cur_path = sys.path[0]
parent_folder = cur_path[:cur_path.rfind('/')]
sys.path.insert(0, parent_folder + "/libs")
from stplibV6 import *


# PROGRAM TO SYTHESIS AND RUN NETWORK IN CADENCE


def build_simulator():
    simulator = stplib_class("/home-nonpermanents/prats_the/Cadence/B55", "TB_NetworkAuto") #"TB_NeXonNetwork_tf_test1"
    simulator.spectre_env_variable = {'PDK_STM_BICMOS055ROOT':'/usr/local/ST/b55_3v1/PDK_STM_BICMOS055/3.1.c-07',
                                    'LM_LICENSE_FILE':"30000@cadence.cnfm.fr"}
    simulator.path_spectre = "/usr/local/cadence/spectre_21/tools/bin/spectre"
    simulator.simu_duration = "1m"
    return simulator


def load_network_sizing(path=parent_folder + '/6 - PLS CADENCE/simus/Network.json'):
    f = open(path)
    param_raw = json.load(f)
    f.close()
    param = {}
    for syn in param_raw:
        synname = "".join(syn.split('_'))
        param_name = list(param_raw[syn]['CDS']['param'].keys())[0]
        param_dic = {param_name: param_raw[syn]['CDS']['param'][param_name]/1000}
        param[synname] = {'param':param_dic, 'block_name':param_raw[syn]['CDS']['block_name']}
    return param

def compute_conso_cds(traces):
    i_vdd = np.array(traces['I0:6']['value'])
    i_vss = np.array(traces['I0:7']['value'])
    i_inx = np.array(traces['I0:3']['value'])
    i_iny = np.array(traces['I0:4']['value'])
    vx = np.array(traces['net3']['value'])
    vy = np.array(traces['net2']['value'])
    conso = np.abs(i_vdd)*0.1 + np.abs(i_vss)*0.1
    conso_in = np.abs(i_inx*vx) + np.abs(i_iny*vy)*0.1
    return (np.max(conso), np.max(conso_in))

def compute_traces(VXi, VXf, VY, simulator, param, log = False):
    globalParam = {'VXi':VXi, 'VY':VY,'VXf':VXf, 'W':0.44, 'Lr': 0.4}
    simulator.load_netlist()
    simulator.update_instance_parameters(param)
    simulator.update_parameters(globalParam)
    simulator.build_input_from_netlist()
    simulator.launch_simulation(log)  # Run the simulation
    traces = simulator.read_signals_computed()
    return traces

def compute_square(simulator, Ngrid=4, plot=False):
    conso_max = 0
    conso_in_max = 0
    param = load_network_sizing()
    Ys = np.linspace(-0.1,0.1,Ngrid)
    ImgNetwork = np.zeros((Ngrid,Ngrid))
    # Start computation
    for idx, val in enumerate(Ys, 0):
        if (plot):
            print("Trace n°",idx+1,"on",Ngrid)
        traces = compute_traces(-0.1,0.1,val, simulator, param)

        conso, conso_in = compute_conso_cds(traces)
        if (conso > conso_max):
            conso_max = conso
        if (conso_in > conso_in_max):
            conso_in_max = conso_in

        pas = int((len(traces['I1:1']['value'])-1)/(Ngrid-1))
        # Echantillonage
        for x in range(Ngrid):
            ImgNetwork[x, idx] = traces['I1:1']['value'][get_idx_in_time(traces['time']['value'], 0.001*x/(Ngrid-1))]/1e-12
            if plot:
                plt.plot(traces['time']['value'][get_idx_in_time(traces['time']['value'], 0.001*x/(Ngrid-1))], ImgNetwork[x, idx], 'ro')
        if plot:
            plt.plot(traces['time']['value'], np.array(traces['I1:1']['value'])/1e-12)
    return ImgNetwork, conso_max, conso_in_max


#simulator = build_simulator()
#ImgNetwork = compute_square(simulator, 4, True)