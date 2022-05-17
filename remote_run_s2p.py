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


ops = suite2p.default_ops()
for key in params['ops']:
    ops[key] = params['ops'][key]

db = params['db']


write_to_log(f'BATCH RUN STARTED. time: {time.ctime()}')
write_to_log(' ')

output_ops = suite2p.run_s2p(ops=ops, db=db)

write_to_log(f'BATCH RUN FINISHED. time: {time.ctime()}')
write_to_log(' ')


## TODO: save images of output_ops stuff

# stats_file = Path(output_ops['save_path']).joinpath('stat.npy')
# iscell = np.load(Path(output_ops['save_path']).joinpath('iscell.npy'), allow_pickle=True)[:, 0].astype(int)
# stats = np.load(stats_file, allow_pickle=True)
# print(stats[0].keys())


# n_cells = len(stats)

# h = np.random.rand(n_cells)
# hsvs = np.zeros((2, Ly, Lx, 3), dtype=np.float32)

# for i, stat in enumerate(stats):
#     ypix, xpix, lam = stat['ypix'], stat['xpix'], stat['lam']
#     hsvs[iscell[i], ypix, xpix, 0] = h[i]
#     hsvs[iscell[i], ypix, xpix, 1] = 1
#     hsvs[iscell[i], ypix, xpix, 2] = lam / lam.max()

# from colorsys import hsv_to_rgb
# rgbs = np.array([hsv_to_rgb(*hsv) for hsv in hsvs.reshape(-1, 3)]).reshape(hsvs.shape)

# plt.figure(figsize=(18,18))
# plt.subplot(3, 1, 1)
# plt.imshow(output_ops['max_proj'], cmap='gray')
# plt.title("Registered Image, Max Projection")

# plt.subplot(3, 1, 2)
# plt.imshow(rgbs[1])
# plt.title("All Cell ROIs")

# plt.subplot(3, 1, 3)
# plt.imshow(rgbs[0])
# plt.title("All non-Cell ROIs");

# plt.tight_layout()