
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import csv
import json

# ===== PARAMETER(S) ======

g_fct_w_deg = 4
b_fct_w_deg = 6
fitting_fa_first_deg = 4

# =========================

def read_simu_file(path):
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
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
                    SignalsDic[NamesRow[idx]].append(float(row[idx]))
            firstline = False
    return SignalsDic

def get_value_per_value_maxmin(max_, vals_, mode = True):
    out = np.zeros_like(max_)
    for x in range(len(vals_)):
        if (mode):
            out[x] = max(vals_[x],max_[x])
        else:
            out[x] = min(vals_[x],max_[x])
    return out

def compute_relative_std(x_, y_):
    '''compute std y_ relative to x_'''
    sum_ = 0
    for idx in range(len(x_)):
        sum_ += (x_[idx] - y_[idx])/y_[idx]
    return sum_/len(x_)

def get_w_value(name):
    split = name.split('/')
    for elm in split:
        if (elm[0:2] == "I_"):
            return float(elm[2:])
    raise Exception("Unexcepted axis name")

def sigmoid(x, L ,x0, k, b):
    y = L / (1 + np.exp(-k*(x-x0))) + b
    return (y)

def extract_and_generate_model(cadence_csv_simu_path, json_path, extModel, display=False, voltageNet=None, OrderedCourbeRef=0, col_typ='k', axf=None, axg=None):
    data = {} # for export
    # Read csv traces
    SignalsDic = read_simu_file(cadence_csv_simu_path)
    
    # Get Y OUTA axis traces
    YTracesDic = {}
    YTraceIN = []
    for trace_name in SignalsDic:
        if (" Y" in trace_name) and ("OUT" in trace_name):
            YTracesDic[get_w_value(trace_name)] = -np.array(SignalsDic[trace_name])
        if (voltageNet == None):
            if ((len(YTraceIN) == 0) and ("/IN Y" in trace_name)):
                YTraceIN = np.array(SignalsDic[trace_name])
        else:
            if ((len(YTraceIN) == 0) and (voltageNet in trace_name) and (" Y" in trace_name)):
                YTraceIN = np.array(SignalsDic[trace_name])

    print(len(YTracesDic.keys()),"differents parameters trace(s) founds")

    # Linear Regression
    # Choose a reference

    if extModel == {}:
        # internal
        reference_af_w = sorted(list(YTracesDic.keys()))[OrderedCourbeRef]
        reference_af = YTracesDic[reference_af_w]
    else:
        # extenal
        if ('sigmo' in extModel):
            # sigmo model
            reference_af = sigmoid(YTraceIN/extModel['k_h'][0], *np.array(extModel['sigmo']))*extModel['k_h'][0]
        else:
            # polynomial model
            reference_af = np.poly1d(np.array(extModel['mod']))(YTraceIN/extModel['k_h'][0])

    # To memorise linear fitting parameters :
    w_ = []
    a_ = []
    b_ = []

    typic_af = np.zeros_like(reference_af)

    # For deviation plot :
    max_dev = reference_af
    min_dev = reference_af

    for w_value in sorted(YTracesDic.keys()):
        coeffs = np.polyfit(reference_af, YTracesDic[w_value], 1)


        # save coefs :
        w_.append(w_value)
        a_.append(coeffs[0])
        b_.append(coeffs[1])

        
        #plt.plot(YTraceIN, reference_af*a_[-1] + b_[-1], '*')
        #plt.plot(YTraceIN, YTracesDic[w_value])

        linear_fitted_trace = (YTracesDic[w_value]-coeffs[1])/coeffs[0]
        max_dev = get_value_per_value_maxmin(max_dev, linear_fitted_trace)
        min_dev = get_value_per_value_maxmin(min_dev, linear_fitted_trace, False)

        typic_af = typic_af + linear_fitted_trace
        if display:
            pass
            #plt.plot(YTraceIN, linear_fitted_trace, 'k',  alpha=.3)

    typic_af /= len(YTracesDic.keys())
    sigma_max = max(compute_relative_std(typic_af,max_dev), compute_relative_std(typic_af,min_dev))
    print("Maximum relative std :",sigma_max)

    # Fitting sigmoidal de la FA (si hidden, sinon modèle polynomial) :

    k_h = (max(YTraceIN) - min(YTraceIN))/2
    x_axis_tf = YTraceIN/k_h

    if (voltageNet == None):
        KxPlot = 1e12
        InitialGuess = [2, 0, 1, 0]
        popt, pcov = curve_fit(sigmoid, x_axis_tf, typic_af/k_h, p0=InitialGuess, method='dogbox')
        data['sigmo'] = popt
    else:
        data['mod'] = np.polyfit(x_axis_tf, typic_af, fitting_fa_first_deg)
        KxPlot = 1000

    data['k_h'] = [k_h]
    if display:
        if (axf != None):
            axf.set_title("Normalized activation function, rstd= "+str(round(100*sigma_max,2))+" %")
            axf.plot(YTraceIN*KxPlot, typic_af*1e12, color=col_typ, label = "Typic")
            #plt.plot(YTraceIN, reference_af, 'c', label = "Reference")
        #plt.plot([min(YTraceIN),max(YTraceIN)], [0,0], 'k--')
        #plt.plot([0,0], [min(typic_af),max(typic_af)], 'k--')
        if (axf != None):
            axf.fill_between(YTraceIN*KxPlot, max_dev*1e12, min_dev*1e12, color=col_typ,  alpha=.3)
            if (voltageNet == None):
                axf.plot(YTraceIN*KxPlot, sigmoid(YTraceIN/k_h, *popt)*k_h*1e12, 'k--', label="Sigmoidal Fitting")
            else:
                axf.plot(YTraceIN*KxPlot, np.poly1d(data['mod'])(YTraceIN/k_h)*1e12, 'k--', label="Poly Fitting")

        axg.set_title("Gain(W)")
        #plt.plot(w_, a_, 'ro')
    # On fait un modèle polynomial de W en fonction du gain
    data['w_fct_g'] = np.polyfit(a_, w_, g_fct_w_deg)
    data['g_fct_w'] = np.polyfit(w_,a_, g_fct_w_deg)
    w_hd = np.linspace(min(w_),max(w_))
    a_hd = np.linspace(min(a_),max(a_))
    data['g_bounds'] = [min(a_),max(a_)]
    w_ = np.array(w_)
    if display:
        #plt.plot(np.poly1d(data['w_fct_g'])(a_hd), a_hd, 'k--')
        if (extModel == {}):
            axg.plot(w_/1000, a_, col_typ)
        else:
            axg.plot(w_/1000, -np.array(a_), col_typ)
        axg.set_xlabel("Transistor width [nm]")

        #plt.subplot(2,2,3)
        #plt.title("Bias(W)")
        #plt.plot(w_, b_, 'ro')
    # On fait un modèle polynomial de W en fonction du gain
    data['b_fct_w'] = np.polyfit(w_, b_, b_fct_w_deg)
    """if display:
        plt.plot(w_hd, np.poly1d(data['b_fct_w'])(w_hd), 'k--')
        plt.xlabel("Transistor width [nm]")
        plt.ylabel("Bias current [A]")"""

    # Export relevant data :
    # W as a function of G
    # Leak as a function of G
    # Sigmoidal fitting

    # Changing format to be serializable
    for data_name in data:
        data[data_name] = [float(d) for d in data[data_name]]

    with open(json_path, "w") as write_file:
        json.dump(data, write_file)

    #if display:
        #plt.show()