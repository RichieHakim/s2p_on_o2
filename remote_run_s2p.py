### batch_run stuff
from pathlib import Path

import sys
path_script, path_params, dir_save = sys.argv
dir_save = Path(dir_save)
                
import json
with open(path_params, 'r') as f:
    params = json.load(f)

import shutil
shutil.copy2(path_script, str(Path(dir_save) / Path(path_script).name));


def write_to_log(text, path_log, mode='a', start_on_new_line=True, pref_print=True, pref_save=True):
    if pref_print:
        print(text)
    if pref_save:
        with open(path_log, mode=mode) as log:
            if start_on_new_line==True:
                log.write('\n')
            log.write(text)




### script

import suite2p
from functools import partial
import time

write_to_log = partial(write_to_log, path_log=str(dir_save / 'log.txt'), pref_print=params['prefs']['log_print'], pref_save=params['prefs']['log_save'])

ops = params['ops']
db = params['db']



write_to_log(f'BATCH RUN STARTED. time: {time.ctime()}')
write_to_log(' ')

suite2p.run_s2p(ops=ops, db=db)

write_to_log(f'BATCH RUN FINISHED. time: {time.ctime()}')
write_to_log(' ')