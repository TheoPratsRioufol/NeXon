
from Extractor_Utils import *

folder_path = "./6 - PLS CADENCE/simus/"

cadence_csv_simu_path_exi = folder_path + "NeXon_First_Carac_exi.csv"
cadence_csv_simu_path_inhi = folder_path + "NeXon_First_Carac_inhi.csv"

json_path_exi = folder_path + "NeXon_First_exi_Model.json"
json_path_inhi = folder_path + "NeXon_First_inhi_Model.json"

extract_and_generate_model(cadence_csv_simu_path_exi, json_path_exi, {}, True, "net7",OrderedCourbeRef=0)

# Read the exitation sigmoidal model
modelFile = open(json_path_exi)
exi_model = json.load(modelFile)
modelFile.close()

extract_and_generate_model(cadence_csv_simu_path_inhi, json_path_inhi, exi_model, True, "net7", OrderedCourbeRef=0)