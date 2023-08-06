import os
import sys
import ast
from tabulate import tabulate

import numpy as np
from glob import glob
import matplotlib.pyplot as plt

print("-----------Creating summary page--------------")
input_dir = sys.argv[1]

output_dir = (
    os.getenv("HOME")
    + "/public_html/RapidPE/"
    + input_dir[input_dir.rfind("output/") + 7 :]
)
os.makedirs(output_dir, exist_ok=True)

if len(sys.argv) > 2:
    summary_plot_dir = sys.argv[2] + "/summary_plots/"
else:
    summary_plot_dir = input_dir + "/summary_plots/"
os.system(f"cp {summary_plot_dir}*png {output_dir}/")
print(f"Summary page will be saved in {output_dir}")
index_html_file = output_dir + "/summarypage.html"
sys.stdout = open(index_html_file, "w")


print("<html><body>")
print(f"<h2>rundir = {summary_plot_dir}</h2>")
filelist = glob(output_dir + "/grid*png")
print("<h1> Grid Plots </h1>")
for fname_full in sorted(filelist):
    fname_split = fname_full.split("/")
    fname = fname_split[-1]
    print(f'<img src="{fname}">')

filelist = glob(output_dir + "/posterior*png")
print("<h1> Posterior Plots </h1>")
for fname_full in sorted(filelist):
    fname_split = fname_full.split("/")
    fname = fname_split[-1]
    print(f'<img src="{fname}">')
print("<h1> Skymaps </h1>")
filelist = glob(output_dir + "/skymap*png")
for fname_full in sorted(filelist):
    fname_split = fname_full.split("/")
    fname = fname_split[-1]
    print(f"<br>{fname}")
    print(f'<img src="{fname}">')


# Get timing plots:

ILE_outfile = glob(input_dir + "/logs/integrate-MASS_SET_*.err")
# Neff= []
PRESET_TIME = []
PRECOMPUTE_TIME = []
EXTRINSIC_SAMPLING_TIME = []
SAMPLE_SAVING_TIME = []
ILE_SCRIPT_RUNTIME = []
for outfile in ILE_outfile:
    with open(outfile) as f:
        lines = f.readlines()[-5:]
        if len(lines) == 5:
            try:
                PRESET_TIME_line = (
                    lines[0] if lines[0].startswith("PRESET_TIME") else None
                )
                preset_time = float(PRESET_TIME_line[len("PRESET_TIME =  "):])
                PRESET_TIME.append(preset_time)
            except:
                continue
            PRECOMPUTE_TIME_line = (
                lines[1] if lines[1].startswith("PRECOMPUTE_TIME") else None
            )
            precompute_time = float(
                PRECOMPUTE_TIME_line[len("PRECOMPUTE_TIME =  "):]
            )
            PRECOMPUTE_TIME.append(precompute_time)

            EXTRINSIC_SAMPLING_TIME_line = (
                lines[2]
                if lines[2].startswith("EXTRINSIC_SAMPLING_TIME")
                else None
            )
            extrinsic_sampling_time = float(
                EXTRINSIC_SAMPLING_TIME_line[
                    len("EXTRINSIC_SAMPLING_TIME =  "):
                ]
            )
            EXTRINSIC_SAMPLING_TIME.append(extrinsic_sampling_time)

            SAMPLE_SAVING_TIME_line = (
                lines[3] if lines[3].startswith("SAMPLE_SAVING_TIME") else None
            )
            sample_saving_time = float(
                SAMPLE_SAVING_TIME_line[len("SAMPLE_SAVING_TIME =  "):]
            )
            SAMPLE_SAVING_TIME.append(sample_saving_time)

            ILE_SCRIPT_RUNTIME_line = (
                lines[4] if lines[4].startswith("ILE_SCRIPT_RUNTIME") else None
            )
            ile_script_runtime = float(
                ILE_SCRIPT_RUNTIME_line[len("ILE_SCRIPT_RUNTIME =  "):]
            )
            ILE_SCRIPT_RUNTIME.append(ile_script_runtime)


length = len(ILE_outfile)

plt.figure()
plt.hist(PRESET_TIME, bins=int(length / 5))
plt.xlabel("PRESET_TIME(s)")
plt.savefig(summary_plot_dir + "PRESET_TIME_hist.png")

plt.figure()
plt.hist(PRECOMPUTE_TIME, bins=int(length / 5))
plt.xlabel("PRECOMPUTE_TIME(s)")
plt.savefig(summary_plot_dir + "PRECOMPUTE_TIME_hist.png")

plt.figure()
plt.hist(EXTRINSIC_SAMPLING_TIME, bins=int(length / 5))
plt.xlabel("EXTRINSIC_SAMPLING_TIME(s)")
plt.savefig(summary_plot_dir + "EXTRINSIC_SAMPLING_TIME_hist.png")

plt.figure()
plt.hist(SAMPLE_SAVING_TIME, bins=int(length / 5))
plt.xlabel("SAMPLE_SAVING_TIME(s)")
plt.savefig(summary_plot_dir + "SAMPLE_SAVING_TIME_hist.png")

plt.figure()
plt.hist(ILE_SCRIPT_RUNTIME, bins=int(length / 5))
plt.xlabel("ILE_SCRIPT_RUNTIME(s)")
plt.savefig(summary_plot_dir + "ILE_SCRIPT_RUNTIME_hist.png")

os.system(f"cp {summary_plot_dir}/*hist*png {output_dir}/")

print("<h1> Timing </h1> ")
filelist = np.sort(glob(output_dir + "/*hist*png"))
for fname_full in sorted(filelist):
    fname_split = fname_full.split("/")
    fname = fname_split[-1]
    print(f'<img src="{fname}">')


# Total job time:
event_info_file = input_dir + "/event_info_dict.txt"
with open(event_info_file) as f:
    contents = f.read()
    dictionary = ast.literal_eval(contents)
    condor_submit_time = float(dictionary["condor_submit_time"])


job_timing_file = input_dir + "/job_timing.txt"
with open(job_timing_file) as f:
    lines = f.readlines()
    for line in lines:
        line_split = line.split(" ")
        level_complete_time = float(line_split[1])
        print(
            f'<br> <font size="+2"> iteration level {line_split[0]} took '
            f"{level_complete_time-condor_submit_time} s </font>"
        )

print("<h1> Config.ini </h1>")

with open(input_dir + "/Config.ini") as config_f:
    for line in config_f:
        if line[0] != "#" and len(line.strip()) > 0:
            if line[0] == "[":
                print(f"<br> <b> {line} </b>")
            else:
                print(f"<br> {line}")

print("<h1> Convergence </h1>")
header = [
    "filename",
    " iteration",
    " Neff ",
    " sqrt(2*lnLmax)",
    " sqrt(2*lnLmarg)",
    " ln(Z/Lmax)",
    "int_var",
]
log_file_list = np.sort(glob(input_dir + "/logs/integrate*out"))
convergence_data = np.ones(len(log_file_list)).tolist()
for i, log_file in enumerate(log_file_list):
    with open(log_file, "r") as f:
        lines = f.readlines()
        last_line = lines[-1]
        if 'Weight' in last_line:
            last_line = lines[-3]
        elif 'neff' in last_line:
            last_line = lines[-3] 
        log_filename = log_file.split("/")[-1]
        data_list = last_line.split(" ")[1:]
        data_list[0] = log_filename
        convergence_data[i] = data_list
print(tabulate(convergence_data, headers=header, tablefmt="html"))


print("</body></html>")

sys.stdout.close()
