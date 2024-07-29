
from Extractor_UtilsFig import *
import scipy
import scipy.stats
import matplotlib.ticker as ticker
from matplotlib.ticker import StrMethodFormatter
lineWidthFig = 0.5

plt.rcParams.update({'font.size': 9})
plt.rcParams['axes.linewidth'] = lineWidthFig

fig, axs = plt.subplots(1,3)
fig.set_size_inches(8,2.5)

folder_path = "./6 - PLS CADENCE/simus/"

cadence_csv_simu_path_exi = folder_path + "NeXon_HiddenV2_Carac_exi.csv"
#cadence_csv_simu_path_exi = folder_path + "NeXon_Hidden_Carac_exiZeroV.csv"
cadence_csv_simu_path_inhi = folder_path + "NeXon_HiddenV2_Carac_inhi.csv"
#cadence_csv_simu_path_inhi = folder_path + "NeXon_Hidden_Carac_inhiZeroV.csv"

json_path_exi = folder_path + "NeXon_Hidden_exi_Model.json"
json_path_inhi = folder_path + "NeXon_Hidden_inhi_Model.json"

extract_and_generate_model(cadence_csv_simu_path_exi, json_path_exi, {}, True, OrderedCourbeRef=-1, col_typ='r',axf=axs[0],axg=axs[2])

# Read the exitation sigmoidal model
modelFile = open(json_path_exi)
exi_model = json.load(modelFile)
modelFile.close()

extract_and_generate_model(cadence_csv_simu_path_inhi, json_path_inhi, exi_model, True, OrderedCourbeRef=-1, col_typ='b',axf=axs[0],axg=axs[2])

folder_path = "./6 - PLS CADENCE/simus/"

cadence_csv_simu_path_exi = folder_path + "NeXon_First_Carac_exi.csv"
cadence_csv_simu_path_inhi = folder_path + "NeXon_First_Carac_inhi.csv"

json_path_exi = folder_path + "NeXon_First_exi_Model.json"
json_path_inhi = folder_path + "NeXon_First_inhi_Model.json"

extract_and_generate_model(cadence_csv_simu_path_exi, json_path_exi, {}, True, "net7",OrderedCourbeRef=0, col_typ='r',axf=axs[1],axg=axs[2])

# Read the exitation sigmoidal model
modelFile = open(json_path_exi)
exi_model = json.load(modelFile)
modelFile.close()

extract_and_generate_model(cadence_csv_simu_path_inhi, json_path_inhi, exi_model, True, "net7", OrderedCourbeRef=0,axf=axs[1], col_typ='b',axg=axs[2])



def set_tick_format(ax, format='{x:,.2f}', bool=True):
    ax.set_tick_params(width=lineWidthFig)
    if bool:
        ax.set_major_formatter(StrMethodFormatter(format))
        ax.set_major_locator(ticker.LinearLocator(3))

set_tick_format(axs[0].xaxis,'{x:,.0f}')
set_tick_format(axs[0].yaxis,'{x:,.0f}')
set_tick_format(axs[1].xaxis,'{x:,.0f}')
set_tick_format(axs[1].yaxis,'{x:,.0f}')
set_tick_format(axs[2].xaxis,'{x:,.2f}')
set_tick_format(axs[2].yaxis,'{x:,.2f}')

axs[0].minorticks_on()
axs[1].minorticks_on()
axs[0].grid()
axs[1].grid()

plt.show()