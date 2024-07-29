
from Extractor_UtilsFig import *

fig, axs = plt.subplots(1,2)
fig.set_size_inches(4.5,2)

folder_path = "./6 - PLS CADENCE/simus/"

cadence_csv_simu_path_exi = folder_path + "NeXon_HiddenV2_Carac_exi.csv"
#cadence_csv_simu_path_exi = folder_path + "NeXon_Hidden_Carac_exiZeroV.csv"
cadence_csv_simu_path_inhi = folder_path + "NeXon_HiddenV2_Carac_inhi.csv"
#cadence_csv_simu_path_inhi = folder_path + "NeXon_Hidden_Carac_inhiZeroV.csv"

json_path_exi = folder_path + "NeXon_Hidden_exi_Model.json"
json_path_inhi = folder_path + "NeXon_Hidden_inhi_Model.json"

extract_and_generate_model(cadence_csv_simu_path_exi, json_path_exi, {}, True, OrderedCourbeRef=-1,axf=axs[0],axg=axs[1])

# Read the exitation sigmoidal model
modelFile = open(json_path_exi)
exi_model = json.load(modelFile)
modelFile.close()

extract_and_generate_model(cadence_csv_simu_path_inhi, json_path_inhi, exi_model, True, OrderedCourbeRef=-1, col_typ='r',axf=axs[0],axg=axs[1])

plt.show()