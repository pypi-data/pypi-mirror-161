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

"""SECTION 1 -- LOAD DATA THIS IS ALREADY DONE SO I WILL COMMENT THIS OUT NOW"""
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''
# T1V1t2_data = utils.load_obj('/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/T1V1t2_data_dict.pkl')
# bd_16_test_yhat = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/final_CNN_predictions_16_count'
# names_list = []
# data_list = []
# for f in utils.sort(utils.get_files(bd_16_test_yhat, '*pkl')):
#     bn = os.path.basename(f)
#     data_list.append(utils.load_obj(f)[:, 0])
#     names_list.append(bn[:-4])
# T1V1t2_data['test_2']['yhat_all'] = data_list
# T1V1t2_data['names'] = names_list
# '''############################# only has #####################################################################'''
# # all_data = utils.load_obj('/Volumes/GoogleDrive-114825029448473821206/My Drive/colab_data2/all_data.pkl')
# # for k in all_data:
# #     if k['full_name'] in T1V1t2_data['names']:
# '''##################################################################################################################'''
# # # dont need this for this analysis
# # T1V1t2_data['train_1']['yhat_all'] = []
# # T1V1t2_data['val_1']['yhat_all'] = []
# '''########################################### figur eout which model to load for whacc###########################################'''
# bd = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/LGBM_models_for_cnn_comparison_all/LGBM_models_for_cnn_comparison_T1V1t2_V3/'
# # yhat_files = utils.sort(utils.get_files(bd, '*model_results.pkl'))
# # val_TCE = []
# # test_TCE = []
# # val_AUC = []
# # test_AUC = []
# # for f in tqdm(yhat_files):
# #     tmp1 = utils.load_obj(f)
# #     val_TCE.append(np.asarray(tmp1['metrics']['touch_count_errors_per_touch']))
# #     test_TCE.append(np.asarray(tmp1['metrics_test']['touch_count_errors_per_touch']))
# #     val_AUC.append(np.asarray(tmp1['metrics']['auc']))
# #     test_AUC.append(np.asarray(tmp1['metrics_test']['auc']))
# #
# # best_ind = np.argmin(1-np.concatenate(val_AUC))
# # model_ind = np.where(best_ind<np.cumsum([len(k) for k in val_AUC]))[0][0]
# # np.max(val_AUC[model_ind])
#
# mod_files = utils.sort(utils.get_files(bd, '*model.pkl'))
# mod = utils.load_obj(mod_files[26])
#
# whacc_yhat = mod.predict(T1V1t2_data['test_2']['data'])
# T1V1t2_data['test_2']['yhat_all'].append(whacc_yhat)
# T1V1t2_data['names'].append('WhACC')
#
# T1V1t2_data['test_2']['names'] = T1V1t2_data['names']
# del T1V1t2_data['test_2']['data']
#
# bd = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/'
# utils.save_obj(T1V1t2_data['test_2'], bd+os.sep+'final_16_and_whacc_yhat_for_plotting')


'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''

t2 = utils.load_obj(
    '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM//final_16_and_whacc_yhat_for_plotting.pkl')
t2['inds'] = [13, 11, 9, 15, 5, 3, 1, 7, 4, 2, 0, 6, 16]

utils.print_list_with_inds(t2['names'])

labels = t2['labels']

t2['total_touches'] = np.sum(np.diff(t2['labels']) == 1)

frame_nums = t2['frame_nums']
t2['analysis'] = dict()
t2['analysis']['name'] = ['ghost', 'miss', 'join', 'split', 'append_4+', 'deduct_4+', 'append', 'deduct', '1 - auc']
TC_err_all = []
for smooth_by in [1, 3, 5, 7, 9, 11]:
    tmp1 = []
    for yhat in t2['yhat_all']:
        yhat_smoothed = utils.smooth(copy.deepcopy(yhat), smooth_by)
        a = analysis.thresholded_error_types(labels, yhat_smoothed, edge_threshold=4, frame_num_array=frame_nums,
                                             thresholds=[.5])
        x = list(np.asarray(a)[0])
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

x = t2['analysis']['smooth_by_5']

tc_err = []
for x2 in x:
    # x2 = x[k]
    TC_tmp = np.sum(x2[:-3]) / t2['total_touches']
    tc_err.append(TC_tmp)
    # print(t2['names'][k])
    # print(TC_tmp)
    # print('----')
names = np.asarray(t2['names'])[t2['inds']]

fig, ax = plt.subplots(figsize=[10, 6])

color = ['r', 'b', 'g', 'y']
tick_centers = []
names = []
for i, k in enumerate(t2['inds'][:-1]):
    print(i // 4)
    i2 = i % 4  # cycle 1 to 4
    i3 = (i // 4) * 5  # for each 4 goes up by 5
    i4 = i3 + i2  # proper spacing for bar fig
    i5 = i3 + 2  # center text for groups of 4 bars
    tick_centers.append(i5)
    names.append(t2['short_names'][k].split('____')[0])

    ax.bar(i4, tc_err[k], color=color[i2])

ax.set_xticks(np.unique(tick_centers))

ax.set_xticklabels()

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
