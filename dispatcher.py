# from IPython.core.display import display, HTML
# display(HTML("<style>.container { width:95% !important; }</style>"))

## Import general libraries
from pathlib import Path
import os
import sys
import copy

import numpy as np
import itertools

### Import personal libraries
# dir_github = '/media/rich/Home_Linux_partition/github_repos'
dir_github = '/n/data1/hms/neurobio/sabatini/rich/github_repos'

import sys
sys.path.append(dir_github)
# %load_ext autoreload
# %autoreload 2
from basic_neural_processing_modules import container_helpers, server
# from s2p_on_o2 import remote_run_s2p


args = sys.argv
path_selfScript = args[0]
dir_save = args[1]
path_script = args[2]
dir_data = args[3:]

print(path_selfScript, dir_save, path_script, dir_data)

## set paths
# dir_save = '/n/data1/hms/neurobio/sabatini/rich/analysis/suite2p_output/'
Path(dir_save).mkdir(parents=True, exist_ok=True)


# path_script = '/n/data1/hms/neurobio/sabatini/rich/github_repos/s2p_on_o2/remote_run_s2p.py'


### Define directories for data and output.
## length of both lists should be the same
# dirs_data_all = ['/n/data1/hms/neurobio/sabatini/rich/analysis/suite2p_output']
# dirs_save_all = [str(Path(dir_save) / 'test_s2p_on_o2')]



params_template = {
    'prefs': {
        'log_print':True,
        'log_save':True,
    },

    'db' : {
        'data_path': dir_data,
        'save_path0': dir_save,
    },

    'ops' : {
        'fast_disk': ['/n/data1/hms/neurobio/sabatini/rich/analysis/suite2p_output/fast_disk'],
        'delete_bin': True,
        'mesoscan': False,
        'nplanes': 1,
        'nchannels': 1,
        'functional_chan': 1,
        'tau': 1.35,
        'fs': 5.14,
        'multiplane_parallel': False,
        'preclassify': 0.0,
        'save_mat': False,
        'save_NWB': False,
        'combined': True,
        'aspect': 1.0,
        'do_bidiphase': False,
        'do_registration': 1,
        'two_step_registration': False,
        'batch_size': 100,
        'align_by_chan': 1,
        'nonrigid': True,
        'block_size': [128, 128],
        'diameter': 12,
        'spatial_scale': 2,
        'connected': True,
        'max_iterations': 20,
        'threshold_scaling': 1.0,
        'max_overlap': 0.75,
        'denoise': True,
        'soma_crop': True,
        'neuropil_extract': True,
        'inner_neuropil_radius': 2,
        'neucoeff': 0.7
    }
}


## make params dicts with grid swept values
params = copy.deepcopy(params_template)
params = [params]
# params = [container_helpers.deep_update_dict(params, ['db', 'data_path'], val) for val in dirs_data_all]
# params = [container_helpers.deep_update_dict(param, ['db', 'save_path0'], val) for param, val in zip(params, dirs_save_all)]
# params = container_helpers.flatten_list([[container_helpers.deep_update_dict(p, ['lr'], val) for val in [0.00001, 0.0001, 0.001]] for p in params])

# params_unchanging, params_changing = container_helpers.find_differences_across_dictionaries(params)


## notes that will be saved as a text file in the outer directory
notes = \
"""
First attempt
"""
with open(str(Path(dir_save) / 'notes.txt'), mode='a') as f:
    f.write(notes)



## copy script .py file to dir_save
import shutil
shutil.copy2(path_script, str(Path(dir_save) / Path(path_script).name));



## save parameters to file
parameters_batch = {
    'params': params,
    # 'params_unchanging': params_unchanging,
    # 'params_changing': params_changing
}
import json
with open(str(Path(dir_save) / 'parameters_batch.json'), 'w') as f:
    json.dump(parameters_batch, f)

# with open(str(Path(dir_save) / 'parameters_batch.json')) as f:
#     test = json.load(f)


## run batch_run function
paths_scripts = [path_script]
params_list = params
# sbatch_config_list = [sbatch_config]
max_n_jobs=1
name_save='jobNum_'


## define print log paths
paths_log = [str(Path(dir_save) / f'{name_save}{jobNum}' / 'print_log_%j.log') for jobNum in range(len(params))]

## define slurm SBATCH parameters
sbatch_config_list = \
[f"""#!/usr/bin/bash
#SBATCH --job-name=suite2p
#SBATCH --output={path}
#SBATCH --partition=priority
#SBATCH -c 20
#SBATCH -n 1
#SBATCH --mem=16GB
#SBATCH --time=0-00:01:00

unset XDG_RUNTIME_DIR

cd /n/data1/hms/neurobio/sabatini/rich/

date

echo "loading modules"
module load gcc/9.2.0

echo "activating environment"
source activate suite2p

echo "starting job"
python "$@"
""" for path in paths_log]

server.batch_run(
    paths_scripts=paths_scripts,
    params_list=params_list,
    sbatch_config_list=sbatch_config_list,
    max_n_jobs=max_n_jobs,
    dir_save=str(dir_save),
    name_save=name_save,
    verbose=True,
)
