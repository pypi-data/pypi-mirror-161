import matplotlib.pyplot as plt
from tqdm.auto import tqdm
from imgaug import augmenters as iaa  # optional program to further augment data

from whacc import utils
import numpy as np
from whacc import image_tools
from natsort import natsorted, ns
import pickle
import pandas as pd
import os
import copy
import seaborn as sns
from keras.preprocessing.image import ImageDataGenerator
import h5py

from whacc import utils, analysis
import h5py
import matplotlib.pyplot as plt
import numpy as np
from sklearn import metrics
from pathlib import Path

info = utils.info
of = utils.open_folder

'''##################################################################################################################'''
'''##################################################################################################################'''
"to make the data see below 2 colab files"
'https://colab.research.google.com/drive/1DwnB6_fZEpbYOlsXpEoCmJIcCGPY9_X3#scrollTo=nKX8aj2eD2j2&uniqifier=1'
'https://colab.research.google.com/drive/1pnwFcMmOJJyVv9V1eVHWNgdXoa4dH0pK#scrollTo=FJkyAxx3fl2t'

'''##################################################################################################################'''
'''##################################################################################################################'''

fn = '/Volumes/GoogleDrive-114825029448473821206/My Drive/Colab data/curation_for_auto_curator/DATA_FULL/full_in_range_and_other_useful_data.pkl'
fn2 = '/Volumes/GoogleDrive-114825029448473821206/My Drive/Colab data/curation_for_auto_curator/DATA_FULL/full_in_range_16_and_whacc_pred.pkl'
in_range_d = utils.load_obj(fn)
yhat_d = utils.load_obj(fn2)

'''##################################################################################################################'''
'''##################################################################################################################'''
data_set_inds = [0, 1, 2, 3]
save_name = '/Volumes/GoogleDrive-114825029448473821206/My Drive/Colab data/curation_for_auto_curator/DATA_FULL/full_in_range_16_and_whacc_pred_all_4.pkl'

data_set_inds = [1, 2, 3]
save_name = '/Volumes/GoogleDrive-114825029448473821206/My Drive/Colab data/curation_for_auto_curator/DATA_FULL/full_in_range_16_and_whacc_pred_no_hair.pkl'

bd = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/final_CNN_predictions_16_count_V2//'
files = utils.sort(utils.lister_it(utils.get_files(bd, '*.pkl')))
model_keys = np.unique([os.path.basename(f)[:-4] for f in files])
model_keys = np.hstack([model_keys[1:], model_keys[0]])

dataset_keys = np.unique([os.path.basename(os.path.dirname(f)) for f in files])
dataset_keys = dataset_keys[data_set_inds]
d = {'model_keys': model_keys, 'dataset_keys': dataset_keys}
for mk in model_keys:
    data = []
    for dk in dataset_keys:
        f = bd + dk + os.sep + mk + '.pkl'
        data.append(np.load(f, allow_pickle=True))
        # print(len(data[-1]))
    data = np.concatenate(data).flatten()
    # print(data.shape)
    d[mk] = data

ir = []
fn = []
sum_fn = []
labels = []
in_range_keys = np.asarray(list(in_range_d.keys())[-4:])
in_range_keys = in_range_keys[data_set_inds]
for k in in_range_keys:
    tmp1 = in_range_d[k]
    ir.append(tmp1['in_range'])
    fn.append(tmp1['frame_nums'])
    labels.append(tmp1['truth_contacts'])
    sum_fn.append(np.sum(tmp1['frame_nums']))

d['frame_nums'] = np.concatenate(fn)
d['in_range'] = np.concatenate(ir)
d['labels'] = np.concatenate(labels)
d['sum_frame_nums'] = sum_fn

utils.save_obj(d, save_name)

'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''

fn = '/Volumes/GoogleDrive-114825029448473821206/My Drive/Colab data/curation_for_auto_curator/DATA_FULL/full_in_range_and_other_useful_data.pkl'
fn2 = '/Volumes/GoogleDrive-114825029448473821206/My Drive/Colab data/curation_for_auto_curator/DATA_FULL/full_in_range_16_and_whacc_pred_all_4.pkl'
# fn2 = '/Volumes/GoogleDrive-114825029448473821206/My Drive/Colab data/curation_for_auto_curator/DATA_FULL/full_in_range_16_and_whacc_pred_no_hair.pkl'

in_range_d = utils.load_obj(fn)
yhat_d = utils.load_obj(fn2)
for k in yhat_d:
    print(k)

# t2 = utils.load_obj('/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM//final_16_and_whacc_yhat_for_plotting.pkl')
# for k in t2:
#     print(k)
# assert np.all(yhat_d['model_keys'] == t2['names']), 'model key names dont match'

['labels', 'frame_nums', 'yhat_all', 'names']

t3 = {'yhat_all': []}  # 'frame_nums':[], 'labels':[]
for k in yhat_d['model_keys']:
    t3['yhat_all'].append(yhat_d[k].flatten() * yhat_d['in_range'])
t3['frame_nums'] = yhat_d['frame_nums']
t3['labels'] = yhat_d['labels'] * yhat_d['in_range']

# t3['labels'][yhat_d['in_range']==0] = -1

t3['names'] = yhat_d['model_keys']
t3['yhat_all'] = [k.flatten() for k in t3['yhat_all']]
t2 = t3

from scipy.signal import medfilt

t2['inds'] = [13, 11, 9, 15, 5, 3, 1, 7, 4, 2, 0, 6, 16]

utils.print_list_with_inds(t2['names'])
for k in t2['inds']:
    print(t2['names'][k])

labels = t2['labels']

t2['total_touches'] = np.sum(np.diff(t2['labels']) == 1)

frame_nums = t2['frame_nums']
t2['analysis'] = dict()
t2['analysis']['name'] = ['ghost', 'miss', 'join', 'split', 'append_4+', 'deduct_4+', 'append', 'deduct', '1 - auc']
TC_err_all = []
for smooth_by in [1, 3, 5, 7, 9, 11]:
    tmp1 = []
    for yhat in t2['yhat_all']:
        # yhat_smoothed = utils.smooth(copy.deepcopy(yhat), smooth_by)
        yhat_smoothed = medfilt(copy.deepcopy(yhat), smooth_by)
        a = analysis.thresholded_error_types(labels, yhat_smoothed, edge_threshold=4, frame_num_array=frame_nums,
                                             thresholds=np.linspace(.6, .95, 10))
        ind = np.argmin(np.sum(np.asarray(a), axis=1))
        a = np.asarray(a)[ind, :]
        x = list(np.asarray(a))
        # a = analysis.thresholded_error_types(labels, yhat_smoothed, edge_threshold=4, frame_num_array=frame_nums,
        #                                      thresholds=[.5])
        # x = list(np.asarray(a)[0])
        auc = 1 - metrics.roc_auc_score(labels, yhat_smoothed)
        x.append(auc)
        tmp1.append(x)
    t2['analysis']['smooth_by_' + str(smooth_by)] = tmp1

'''##################################################################################################################'''
'''##################################################################################################################'''
short_names = []
for k in t2['names'][:-1]:
    short_name = ''
    if '__3lag__' in k:
        short_name += 'lag'
    else:
        short_name += 'no-lag'
    if ' aug ' in k:
        short_name += '\naugmented'
    else:
        short_name += '\nnot-augmented'
    short_name += '____' + k.split('__')[1]
    short_names.append(short_name)
short_names.append('WhACC')
t2['short_names'] = short_names

'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''

x = t2['analysis']['smooth_by_11']
save_dir = '/Users/phil/Dropbox/HIRES_LAB/WhACC PAPER/figures/auc and TC errors smoothing test/'
add_to_name = ' Optimal threshold'
for iii in [1, 3, 5, 7, 9, 11]:
    x = t2['analysis']['smooth_by_' + str(iii)]

    tc_err = []
    one_min_auc = []
    for x2 in x:
        # x2 = x[k]
        one_min_auc.append(x2[-1])
        TC_tmp = np.sum(x2[:-3]) / t2['total_touches']
        tc_err.append(TC_tmp)
        # print(t2['names'][k])
        # print(TC_tmp)
        # print('----')
    names = np.asarray(t2['names'])[t2['inds']]
    '''##################################################################################################################'''
    '''##################################################################################################################'''

    fig, ax = plt.subplots(figsize=[10, 6])
    color = ['r', 'b', 'g', 'y']
    tick_centers = []
    names = []
    for i, k in enumerate(t2['inds'][:]):
        print(i // 4)
        i2 = i % 4  # cycle 1 to 4
        i3 = (i // 4) * 5  # for each 4 goes up by 5
        i4 = i3 + i2  # proper spacing for bar fig
        i5 = i3 + 2  # center text for groups of 4 bars
        tick_centers.append(i5 - .5)
        names.append(t2['short_names'][k].split('____')[0])

        ax.bar(i4, tc_err[k], color=color[i2])

    ax.set_xticks(tick_centers[0::4])
    ax.set_xticklabels(names[0::4])
    # plt.ylim([0, 1])
    plt.title('smooth_by_' + str(iii) + ' ' + 'TC-error' + add_to_name)
    plt.savefig(save_dir + 'smooth_by_' + str(iii) + ' ' + 'TC-error' + add_to_name)
    '''##################################################################################################################'''
    '''##################################################################################################################'''

    fig, ax = plt.subplots(figsize=[10, 6])
    color = ['r', 'b', 'g', 'y']
    tick_centers = []
    names = []
    for i, k in enumerate(t2['inds'][:]):
        print(i // 4)
        i2 = i % 4  # cycle 1 to 4
        i3 = (i // 4) * 5  # for each 4 goes up by 5
        i4 = i3 + i2  # proper spacing for bar fig
        i5 = i3 + 2  # center text for groups of 4 bars
        tick_centers.append(i5 - .5)
        names.append(t2['short_names'][k].split('____')[0])

        ax.bar(i4, one_min_auc[k], color=color[i2])

    ax.set_xticks(tick_centers[0::4])
    ax.set_xticklabels(names[0::4])
    plt.ylim([0, .1])
    plt.title('smooth_by_' + str(iii) + ' ' + '1 - AUC' + add_to_name)
    plt.savefig(save_dir + 'smooth_by_' + str(iii) + ' ' + '1 - AUC' + add_to_name)

'''##################################################################################################################'''
'''##################################################################################################################'''

ax.get_xticklabels()
ax.get_t

loc = i // 4
t2['short_names'][k]

plt.bar(range(len(tc_err)), tc_err)

for k in t2['inds']:
    x2 = x[k]
    print(t2['names'][k])
    print(x2[-1])
    print('----')
"""
ok so this is really bad I am getting weird info and it seems that inception net is better than resnet and also that 
mobile net is better as well holy shit. 
further, incetion net regular images and no augmentation is better than WITH augmention regular images, which seems so unlikly especially for a 
model like inception net that is so deep


OKAYYYYY still need to apply in range data, for TC errors you can just times the whole thing and use the same framenums
for the AUC data just cut it out and we dont need AUC for this 
"""
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''

'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''

'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''

all_data = utils.load_obj('/Volumes/GoogleDrive-114825029448473821206/My Drive/colab_data2/all_data.pkl')

full_names = []
for k in all_data:
    full_names.append(k['full_name'])

utils.print_h5_keys(h5_in)

# get the top model inds (NO-LAG) aug models
keys_to_plot = utils.print_h5_keys(h5_in, 1, 0)
keys_to_plot, index = utils.lister_it(keys_to_plot, keep_strings=['regular 80 border aug'],
                                      remove_string=['__3lag__', '3lag diff', 'EfficientNet', '__only', '__overlap',
                                                     '__on-off'], return_bool_index=True)
model_ind_list = np.where(index)[0]
keys_to_plot

h5 = '/Volumes/GoogleDrive-114825029448473821206/My Drive/Colab data/curation_for_auto_curator/DATA_FULL/data_AH0407_160613_JC1003_AAAC/3lag/AH0407_160613_JC1003_AAAC_3lag.h5'
d = utils.h5_to_dict(h5)
d.keys()
utils.info(d)

import cv2
import numpy as np

color_explore = np.zeros((150, 150, 3), np.uint8)
color_selected = np.zeros((150, 150, 3), np.uint8)


# save selected color RGB in file
def write_to_file(R, G, B):
    f = open("saved_color.txt", "a")
    RGB_color = str(R) + "," + str(G) + "," + str(B) + str("\n")
    f.write(RGB_color)
    f.close()


# Mouse Callback function
def show_color(event, x, y, flags, param):
    B = img[y, x][0]
    G = img[y, x][1]
    R = img[y, x][2]
    color_explore[:] = (B, G, R)

    if event == cv2.EVENT_LBUTTONDOWN:
        color_selected[:] = (B, G, R)

    if event == cv2.EVENT_RBUTTONDOWN:
        B = color_selected[10, 10][0]
        G = color_selected[10, 10][1]
        R = color_selected[10, 10][2]
        print(R, G, B)
        write_to_file(R, G, B)
        print(hex(R), hex(G), hex(B))


# live update color with cursor
cv2.namedWindow('color_explore')
cv2.resizeWindow("color_explore", 50, 50);

# Show selected color when left mouse button pressed
cv2.namedWindow('color_selected')
cv2.resizeWindow("color_selected", 50, 50);

# image window for sample image
cv2.namedWindow('image')

# sample image path
img_path = "/Users/phil/Dropbox/HIRES_LAB/WhACC PAPER/Picture1.png"

# read sample image
img = cv2.imread(img_path)

# mouse call back function declaration
cv2.setMouseCallback('image', show_color)

# while loop to live update
while (1):

    cv2.imshow('image', img)
    cv2.imshow('color_explore', color_explore)
    cv2.imshow('color_selected', color_selected)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()


