#! /usr/bin/env python
#
# 20190626

#  GOAL

# Author: Sinead Walsh: walsh6@uwm.edu
#
# Called from submit_rapidpe_m1m2_injections.py
#
# Needs all event information. 
#
#    Creates the .sub file needed to run at exact signal position
#    Submits it 
#    As with GCT, monitors output so that once the results are available it can run the convert and plot script to plot extrinsic
#

import sys,os,json,ast
import subprocess,time
import numpy as np
#from lalinference.rapid_pe import dagutils

from rapidpe_rift_pipe.modules import *

from glue import pipeline # https://github.com/lscsoft/lalsuite-archive/blob/5a47239a877032e93b1ca34445640360d6c3c990/glue/glue/pipeline.py

from rapidpe_rift_pipe.config import Config
cfgname = sys.argv[1]
config = Config.load(cfgname)

username = os.environ["USER"]

exe_generate_initial_grid = ""
# TODO: add extra argument to `Config.load` to override source of `event_info`
if config.event_params_in_cfg:
    event_info = config.common_event_info
elif len(sys.argv) == 3:
    event_info = convert_dict_string_to_dict(sys.argv[2])

else:
    sys.exit("ERROR: need to pass cfg_name and string of dict of event args if event not in config. args given:"+sys.argv)
    
output_event_directory= event_info["output_event_ID"] #the output directory for the single event trigger being followed up here
event_info["dag_script_start_time"] = time.time()

output_dir = script_directory+"/"+config.output_parent_directory+"/"+output_event_directory+"/"

def main():


    #
    # Create new working directory for the event
    #
    print ("The directory for this event is",output_dir)
    print ("The working dir will change to the above after initial grid generation, if generating the initial grid")

    if not os.path.isdir(output_dir):
        os.system("mkdir -p "+output_dir)
    elif not config.overwrite_existing_event_dag:
        sys.exit("ERROR: event directory already exists")
    if not os.path.isdir(output_dir+"/logs"):
        os.mkdir(output_dir+"/logs")
        os.mkdir(output_dir+"/results")

    os.system("cp "+cfgname+" "+output_dir+"/Config.ini")
    os.system('echo "\n#Original config name: '+cfgname+'" >> '+output_dir+'/Config.ini')




    ###
    ### With the inital grid generated, you have all the information you need to run iteration 0. You set up the dag for that here, using rapidpe_create_event_dag in lalsuite. FIXME: this only works for m1 m2. It needs to be adapted for any dimension by taking 
    ### The output .dag file has a few lines for every m1 m2 etc point with the values of the point. The output .sh file has the values filled into the common command line arguements for integrate extrinsic likelihood. The only variable that remains to be filled in the integarte commands is the name of the output file, which includes the cluster and process id. Why are these neeed? I don't know, but it's probably for debugging
    ###
    ### output-name is the name of the dag files for iteration 0. output-file is the name of the file output per intrinsic grid point. The latter will have the massID, cluster and process appended to it.
    ###
    ### FIXME: What doesn the output xml.gz file contain. output name and output file are independent
 
    #event specific commands which need to be lassed to the integration exe are added to the dict here
    if any(k in config.integrate_likelihood_cmds_dict for k in {"event-time", "psd-file", "channel-name"}):
        sys.exit("ERROR: event specific info specified in LikelihoodIntegration of config and in command line or Event section of config. event_time, psd_file,cache_file and channel_name must be specified in the [Event] section or in the input event dictionary ")
    else:
        config.integrate_likelihood_cmds_dict["event-time"] = event_info["event_time"]
        config.integrate_likelihood_cmds_dict["psd-file"] = event_info["psd_file"]
        config.integrate_likelihood_cmds_dict["channel-name"] = event_info["channel_name"]
        config.integrate_likelihood_cmds_dict["cache-file"] = event_info["cache_file"]
        config.integrate_likelihood_cmds_dict["approximant"] = event_info["approximant"]
        if "skymap_file" in event_info:
            config.integrate_likelihood_cmds_dict["skymap-file"] = event_info["skymap_file"]

    #This is the filename for the output at each intrinsic grid point
    integration_output_file_name = "results/ILE_iteration_0_exact_mass.xml.gz"

    extra_cmd_line = convert_dict_to_cmd_line(config.integrate_likelihood_cmds_dict)

    #FIXME: this is all removed because lalsuite build isn't working, should be reenabled when it works again
###%    #Use dagutils to create integrate.sub in parent file, then read that in and replace relevant params
###%    sub_parent_name = "integrate.sub"
###%    #make the parent output directory your working directory                                                                             
###%    os.chdir(config.output_parent_directory)
###%    inj_param = convert_list_string_to_dict(event_info["injection_param"])    
###%    intr_prms = ("mass1","mass2")
###%    if "spin1z" in inj_param:
###%        intr_prms = ("mass1","mass2","spin1z","spin2z")
###%    if not os.path.isfile(sub_parent_name):
###%        condor_commands = {}
###%        condor_commands["accounting_group"] = config.accounting_group
###%        #Make the sub file using dag utils.
###%        ile_job_type, ile_sub_name = dagutils.write_integrate_likelihood_extrinsic_sub(
###%#        tag=sub_parent_name+'/integrate',
###%        tag='integrate',
###%        condor_commands=condor_commands,
###%        intr_prms=intr_prms,
###%        log_dir="logs/",
###%        exe=config.exe_integration_extrinsic_likelihood,
###%        ncopies=1,
###%        output_file=integration_output_file_name,
###%        **integrate_likelihood_cmds_dict
###%        )
###%        ile_job_type.write_sub_file()
###%        
###%

#    sub_parent_name = ""
#    sub_base = open(sub_parent_name,"r")
    inj_param = convert_list_string_to_dict(event_info["injection_param"])    

#    print ("WARNING: using python exe instead of exe as tmpfixes until PYTHONPATH figured out, remove this once exe is working directly")

    newlines = "universe = vanilla\n"
#    newlines += "executable = /usr/bin/python\n"
#    newlines += 'arguments = " '+config.exe_integration_extrinsic_likelihood
    newlines += "executable = "+config.exe_integration_extrinsic_likelihood+"\n"
    newlines += 'arguments = " '
    newlines += " --output-file="+integration_output_file_name
    newlines += " --mass1 "+str(inj_param["mass1"])+" --mass2 "+str(inj_param["mass2"])+" --spin1z "+str(inj_param["spin1z"])+" --spin2z "+str(inj_param["spin2z"])
    newlines += " "+extra_cmd_line
    newlines += ' "\n'
    newlines += "request_memory = 4096\naccounting_group = "+config.accounting_group+"\ngetenv = True\n"
    newlines += "log = logs/integrate.log\nerror = logs/integrate.err\noutput = logs/integrate.out\n"
    newlines += "notification = never\nqueue 1\n"

##%    newlines = ""
##%    for li,line in enumerate(sub_base):
##%        if "arguments" in line:
##%            nl = line.replace("$(macromass1)",str(inj_param["mass1"]))
##%            nl = nl.replace("$(macromass2)",str(inj_param["mass2"]))
##%            nl = nl.replace("$(macrospin1z)",str(inj_param["spin1z"]))
##%            nl = nl.replace("$(macrospin2z)",str(inj_param["spin2z"]))
##%            nl = nl.replace("-$(macromassid)-$(cluster)-$(process)","")
##%            newlines += nl
##%        elif ".log" in line:
##%            nl = "log = logs/integrate.log\n"
##%            newlines += nl
##%        elif ".err" in line:
##%            nl = "error = logs/integrate.err\n"
##%            newlines += nl
##%        elif ".out" in line:
##%            nl = "output = logs/integrate.out\n"
##%            newlines += nl
##%        else:
##%            newlines+=line
##%

    sub_file_path = output_dir+"/integrate.sub"
    fo = open(sub_file_path,"w")
    fo.write(newlines)
    fo.close()

#    os.system("cat "+sub_file_path)
    #make the output directory your working directory                                                                             
    os.chdir(output_dir)


    event_info["condor_submit_time"] = time.time()
    #Write the event_info dictionary to the output dir
    ef = open(output_dir+"/event_info_dict.txt","w")
    ef.write(json.dumps(event_info))
    ef.close()

    print("Job ready for submission",sub_file_path)
    if config.submit_dag:
        os.system("condor_submit "+sub_file_path)
    return        



if __name__ == '__main__':
    main()
