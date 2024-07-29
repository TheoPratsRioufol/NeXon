import os
import subprocess
import numpy as np


# STP Lib
#
#   --- V0 - 8/12/22:
#   Possibility to launch spectre, get results (read the "psf" file or .tran), put initials conditions, replace only name in netlist by their value
#   Not support differents instances
#
#   --- V2/V3 - 15/12/22
#   Working on instance handeling
#   Possibility to hide spectre result in shell
#   Add frequency mesurement function
#
#   --- V6 - 1/03/24:
#   Making everithing more robust and simple
#   Instance parameter updating



class stplib_class:
    def __init__(self, path_cadence, simu_name):
        self.path_cadence = path_cadence
        self.simu_name = simu_name
        # To initialise the communication
        # Usefull environement variables :
        self.spectre_env_variable = {}

        # this need to be the path of the following file :
        # include "$PDK_STM_BICMOS055ROOT/DATA/MODEL/CDS/SPECTRE/CORNERS/common_varind.scs" section=TYP
        self.build = False

        # GENERATING THE PATHS :
        self.simu_output_path = path_cadence + "/simulations/" + \
            simu_name + "/spectre/schematic/psf/tran.tran.tran"
        self.path_input_simulator = path_cadence + "/simulations/" + \
            simu_name + "/spectre/schematic/netlist/input.scs"
        self.path_netlist = path_cadence + "/simulations/" + \
            simu_name + "/spectre/schematic/netlist/netlist"

        # GENERATING SPECTRE SIMULATION PARAMETERS :
        self.simu_duration = "50u"
        self.simu_type = "conservative"
        self.path_corners = self.path_cadence + "/corners.scs"
        self.path_spectre = ""

        # DEFINE SPECTRE NETLIST END MARKER :
        self.initials_conditions = ""
        # Can be use manualy
        self.INPUT_FILE_END_TEXT = ""

        # DEFINITION FOR USEFULL FUNCTIONS
        self.signals = []
        self.netlist_read = ""

    def launch_simulation(self, Display = True):
        '''launch spectre. if Display is set to false, the output will be hidden. Make sure you fill the environement variables'''

        if (not self.build):
            raise Exception("You should build the netlist before lauching spectre")
        if (self.path_spectre == ""):
            raise Exception("You should specify the path of the bin spectre (self.path_spectre)")

        for env_variable in self.spectre_env_variable:
            os.environ[env_variable] = self.spectre_env_variable[env_variable]

        l2 = self.path_cadence + "/simulations/" + self.simu_name + "/spectre/schematic/netlist/input.scs"
        l3 = "+escchars"
        l4 = "+log"
        l5 = self.path_cadence + "/simulations/" + self.simu_name + "/spectre/schematic/psf/spectre.out"
        l6 = "-format"
        l7 = "psfascii"
        l8 = "-raw"
        l9 = self.path_cadence + "/simulations/" + self.simu_name + "/spectre/schematic/psf"
        l10 =  "+lqtimeout"
        l11 =  "900"
        l12 =  "-maxw"
        l13 =  "5"
        l14 = "-maxn"
        l15 =  "5"
        if (Display == False):
            subprocess.run([self.path_spectre, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11, l12, l13, l14, l15], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run([self.path_spectre, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11, l12, l13, l14, l15])

    def add_initial_condition(self, netname, value):
        self.initials_conditions += "nodeset " + netname + "=" + value + "\nic " + netname + "=" + value + "\n"

    def read_signals_computed(self):
        '''return a dictionary with all the trace with the form : {trace_name: {value:[]}}'''
        
        simu_output_file = os.open(self.simu_output_path, os.O_RDONLY)
        simu_output_size = os.stat(simu_output_file).st_size
        simu_output_read = os.read(simu_output_file, simu_output_size).decode(
            'ascii')  # To turn byte array into string
        
        lines = simu_output_read.split('\n')
        traces = {}

        def exploit_line(line):
            linesplit = line.split(' ')
            if (len(linesplit) != 2):
                raise Exception("Error to extract the signal of the line "+line)
            return (linesplit[0].replace('"',''), float(linesplit[1]))

        # Go to the "VALUE" section
        start_index = 0
        while (lines[start_index] != "VALUE"):
            start_index += 1

        for index in range(start_index+1, len(lines)):

            if (lines[index] == "END"):
                break

            (name, val) = exploit_line(lines[index])

            if (name in traces):
                traces[name]['value'].append(val)
            else:
                traces[name] = {'value':[val]}

        return traces

    def get_signals_computed(self):
        '''deprecated'''
        # Return the list of the signals availables and their unit
        # Reset the list :
        self.signals = []

        # Read the output file :
        simu_output_file = os.open(self.simu_output_path, os.O_RDONLY)
        simu_output_size = os.stat(simu_output_file).st_size
        simu_output_read = os.read(simu_output_file, simu_output_size).decode(
            'ascii')  # To turn byte array into string
        lines = simu_output_read.split('\n')

        # go to the "TRACE" section :
        start_index = 0
        while (lines[start_index] != "TRACE"):
            start_index += 1
        
        start_index += 1
        # Read the names :
        while (lines[start_index] != "VALUE"):
            name_line = lines[start_index].split('"')
            self.signals.append((name_line[1], name_line[3])) # value and unit
            start_index += 1

    def load_netlist(self):
        '''Open the original netlist and load it'''

        self.build = False
        netlistFile = os.open(self.path_netlist, os.O_RDONLY)
        netlistFile_size = os.stat(netlistFile).st_size
        self.netlist_read = os.read(netlistFile, netlistFile_size).decode('ascii')
        os.close(netlistFile)

    def build_input_from_netlist(self):
        '''generate and save the input.scs file for spectre'''

        self.build = True
        # Prepare the output file
        os.remove(self.path_input_simulator)  # Remove the existing one
        os.mknod(self.path_input_simulator)
        inputFile = os.open(self.path_input_simulator, os.O_WRONLY)
        # Spectre parameters :
        # Initials conditions are here in the input file
        self.INPUT_FILE_END_TEXT = self.initials_conditions
        # End marker :
        self.INPUT_FILE_END_TEXT += """\r\n\r\nsimulatorOptions options psfversion="1.1.0" reltol=1e-3 vabstol=1e-6 \
            iabstol=1e-12 temp=27 tnom=27 scalem=1.0 scale=1.0 gmin=1e-12 rforce=1 \
            maxnotes=5 maxwarns=5 digits=5 cols=80 pivrel=1e-3 \
            sensfile="../psf/sens.output" dochecklimit=no checklimitdest=both 
        tran tran stop=""" + self.simu_duration + """ errpreset=""" + self.simu_type + """ write="spectre.ic" \
            writefinal="spectre.fc" annotate=status maxiters=5 
        finalTimeOP info what=oppoint where=rawfile
        modelParameter info what=models where=rawfile
        element info what=inst where=rawfile
        outputParameter info what=output where=rawfile
        designParamVals info what=parameters where=rawfile
        primitives info what=primitives where=rawfile
        subckts info what=subckts where=rawfile
        saveOptions options save=allpub subcktprobelvl=2"""

        # Create the input netlist
        netlist_read = "simulator lang=spectre\nglobal 0\ninclude \"" + self.path_corners + "\"\n" + \
            self.netlist_read + self.INPUT_FILE_END_TEXT

        # Save the file
        os.write(inputFile, netlist_read.encode('ascii'))
        os.close(inputFile)

    def update_parameters(self, param_dic):
        '''replace all parameters in a netlist by the value in param_dic
        param_dic = {'param1':value1, 'param2': value2...}'''

        if (self.netlist_read == ""):
            raise Exception("Netlist empty, you should load it before !")
        
        self.netlist_read = replace_parameter_in_netlist(self.netlist_read, param_dic)

    def new_sub_ckt_and_replace_name(self, sub_ckt_name, sub_ckt_netlist):
        '''create a new sub circuit'''

        # we add at the top
        # prepare for replacing the name
        sub_ckt_lines = sub_ckt_netlist.split('\n')
        first_line = sub_ckt_lines[0].split(' ')
        end_line = sub_ckt_lines[-1].split(' ')

        # replace name
        first_line[1] = sub_ckt_name
        end_line[1] = sub_ckt_name

        first_line = ' '.join(first_line)
        end_line = ' '.join(end_line)
        sub_ckt_lines[0] = first_line
        sub_ckt_lines[-1] = end_line

        sub_ckt_netlist_ok = '\n'.join(sub_ckt_lines)

        self.netlist_read = "\n\n// [WARNING !] Automatic generation of sub_ckt\n" + sub_ckt_netlist_ok + '\n' + self.netlist_read

    def replace_block_for_instance(self, instance_name, new_block_name):
        '''will replace the block (subcircuit) corresponding to the instance having the name instance_name'''

        linebuffer = ""
        i_begin = 0

        for i in range(len(self.netlist_read)):
            if (self.netlist_read[i] == '\n') or (i == len(self.netlist_read)-1):
                if (is_instance_def(linebuffer, instance_name)):
                    oldlinebuffer = linebuffer
                    linesplit = linebuffer.split(' ')
                    linesplit[-1] = new_block_name
                    linebuffer = ' '.join(linesplit)
                    # replacing :
                    self.netlist_read = self.netlist_read[0:i_begin] + linebuffer + self.netlist_read[(i_begin+len(oldlinebuffer)):]
                    return
                linebuffer = ""
                i_begin = i+1
            else:
                linebuffer += self.netlist_read[i]
        print("[WARNING] - Instance \""+instance_name+"\" not found in the netlist")


    def update_instance_parameters(self, instance_dic_values):
        '''form of instance_dic_values : {instance_name(str) : {'block_name':strname, 'param':{'Param1':value1, 'Param2':value2}} }
        will replace all instance have it's name in instance_name dictionary by a new block (named strname) and having it parameter equal to value1, value2...
        The subcircuit for strname should already be in the netlist (you can put this circuit on a side, connected to nothing)'''

        subckts_netlist = {}
        unique_id = 0

        for instance_name in instance_dic_values:
            unique_id += 1

            block_name = instance_dic_values[instance_name]['block_name']

            if (block_name not in subckts_netlist):
                subckts_netlist[block_name] = get_subckt_netlist(self.netlist_read,block_name)

            new_block_name = block_name + "_" + str(unique_id)

            self.new_sub_ckt_and_replace_name(new_block_name, replace_parameter_in_netlist(subckts_netlist[block_name],instance_dic_values[instance_name]['param']))
            self.replace_block_for_instance(instance_name, new_block_name)


# OTHER USEFULL FUNCTIONS

def get_first_letter_idx(line):
    for idx in range(len(line)):
        c = line[idx]
        if ((c <= 'z') and (c >= 'a')) or ((c <= 'Z') and (c >= 'A')) or (c == '_'):
            return idx
    return 0
            
def is_instance_def(line, instance_name):
    '''return true if the line is the definition of the instance instance_name'''
    start_idx = get_first_letter_idx(line)
    return line[start_idx:len(instance_name)+start_idx] == instance_name
            
def get_subckt_netlist(netlist, name):
    '''return netlist of a the first occurence of a sub circuit'''

    linebuffer = ""
    subckt_netlist = ""
    found = False

    for i in range(len(netlist)):
        if (netlist[i] == '\n') or (i == len(netlist)-1):
            if (found):
                subckt_netlist = subckt_netlist + '\n' + linebuffer
            if (linebuffer[0:len("subckt")] == "subckt") and (linebuffer.split(' ')[1] == name):
                found = True
                subckt_netlist = linebuffer
            if (linebuffer[0:len("ends")] == "ends") and (linebuffer.split(' ')[1] == name) and found:
                return subckt_netlist
            linebuffer = ""
        else:
            linebuffer += netlist[i]

    raise Exception("No subcircuit named "+name+" found in the netlist ! Make sure the subcircuit is present in the circuit (even connected to nothing)")
            
def replace_parameter_in_netlist(netlist, param_dic):
    '''replace all parameters in a netlist by the value in param_dic
    param_dic = {'param1':value1, 'param2': value2...}'''

    netlistout = netlist
    for param in param_dic:
        if (type(param_dic[param]) == str):
            param_value = param_dic[param]
        else:
            param_value = str(param_dic[param])
        netlistout = netlistout.replace(param, param_value)
    return netlistout




        
