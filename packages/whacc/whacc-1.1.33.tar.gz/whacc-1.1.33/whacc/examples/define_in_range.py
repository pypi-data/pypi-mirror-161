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


def pole_relative_first_and_last_touch_arrays(h5_file, truth_contacts, frame_nums=None, pole_times=None):
    if pole_times is None:
        pole_times = image_tools.get_h5_key_and_concatenate([h5_file], 'pole_times')
    if frame_nums is None:
        try:
            frame_nums = image_tools.get_h5_key_and_concatenate([h5_file], 'frame_nums')
        except:
            tnfn = image_tools.get_h5_key_and_concatenate([h5_file], 'trial_nums_and_frame_nums')
            frame_nums = tnfn[1, :]

    first_touches = []
    last_touches = []
    for ii, (i1, i2) in enumerate(utils.loop_segments(frame_nums)):
        x = truth_contacts[i1:i2]
        tmp1 = np.where(x)[0]
        if tmp1.size != 0:
            first_touches.append(int(tmp1[0] - pole_times[0, ii]))
            last_touches.append(int(tmp1[-1] - pole_times[1, ii]))
        else:
            first_touches.append(np.nan)
            last_touches.append(np.nan)
    return np.asarray(first_touches), np.asarray(last_touches)


def pole_touch_latencies(first_touches, last_touches, pole_up_min=40, pole_down_min=40):
    print('min_first_touch is positive and max_last_touch is negative, was this the best choice? IDK, but know this!')
    first_touches = copy.deepcopy(first_touches)
    last_touches = copy.deepcopy(last_touches)
    # first_touches, last_touches = pole_relative_first_and_last_touches(h5_file, truth_contacts, frame_nums = None, pole_times = None)
    first_touches[first_touches <= pole_up_min] = 99999999999
    last_touches[last_touches >= -pole_down_min] = -99999999999
    min_first_touch = np.nanmin(first_touches)
    max_last_touch = np.nanmax(last_touches)
    return min_first_touch, max_last_touch


from whacc.utils import get_frame_nums, overwrite_h5_key, loop_segments


def define_in_range(h5_file, pole_up_set_time=0, pole_down_add_to_trigger=0, write_to_h5=True, return_in_range=False,
                    pole_times=None):
    with h5py.File(h5_file, 'r+') as hf:
        if pole_times is None:
            pole_times = hf['pole_times'][:]

        try:
            new_in_range = np.zeros_like(hf['in_range'][:])
        except:
            new_in_range = np.zeros_like(hf['labels'][:])

        fn = get_frame_nums(h5_file)
        for i, (i1, i2) in enumerate(loop_segments(fn)):
            pt = pole_times[:, i] + i1
            x1 = pt[0] + pole_up_set_time
            x2 = pt[1] - pole_down_add_to_trigger
            x2 = min([x2, i2])
            new_in_range[int(x1):int(x2)] = 1
    if write_to_h5:
        overwrite_h5_key(h5_file, 'in_range', new_data=new_in_range)
    if return_in_range:
        return new_in_range


base_dir = '/Volumes/GoogleDrive-114825029448473821206/My Drive/Colab data/curation_for_auto_curator/DATA_FULL/'
h5_list_to_write = utils.sort(utils.lister_it(utils.get_h5s(base_dir, 0), '/3lag/'))
all_in_range = []
custom_modifier_list = [0, 0, 0, 0, 973, 973, 0, 0]

pole_up_min_all = [40, 40, 40, 40, 40, 40, 40, 40, ]
pole_down_min_all = [40, 40, 40, 40, 40, 40, 200, 40, ]
d = dict()

for iii, k in enumerate(h5_list_to_write):
    # if iii == 6:
    #     sadf
    pole_up_min = pole_up_min_all[iii]
    pole_down_min = pole_down_min_all[iii]

    truth_contacts = image_tools.get_h5_key_and_concatenate([k], '[0, 1]- (no touch, touch)')
    pole_times = image_tools.get_h5_key_and_concatenate([k], 'pole_times')
    frame_nums = image_tools.get_h5_key_and_concatenate(k, 'frame_nums')
    custom_modifier = custom_modifier_list[iii]
    pole_times = pole_times - custom_modifier
    # if iii in [4, 5]: # samsons offset
    #     pole_times = pole_times - 973
    first_touches, last_touches = pole_relative_first_and_last_touch_arrays(k,
                                                                            truth_contacts,
                                                                            frame_nums=frame_nums,
                                                                            pole_times=pole_times)

    min_first_touch, max_last_touch = pole_touch_latencies(first_touches,
                                                           last_touches,
                                                           pole_up_min=pole_up_min,
                                                           pole_down_min=pole_down_min)

    in_range = define_in_range(k,
                               pole_up_set_time=min_first_touch,
                               pole_down_add_to_trigger=max_last_touch,
                               write_to_h5=False,
                               return_in_range=True,
                               pole_times=pole_times)
    all_in_range.append(in_range)
    print(os.path.basename(k))
    print(min_first_touch)
    print(max_last_touch)
    print(np.sum(abs(in_range - 1) * truth_contacts))
    print('\n')
    d2 = dict()
    d2['truth_contacts'] = truth_contacts
    d2['pole_times'] = pole_times
    d2['frame_nums'] = frame_nums
    d2['first_touches'] = first_touches
    d2['last_touches'] = last_touches
    d2['min_first_touch'] = min_first_touch
    d2['max_last_touch'] = max_last_touch
    d2['in_range'] = in_range
    d2['custom_modifier'] = custom_modifier
    d2['pole_up_min'] = pole_up_min
    d2['pole_down_min'] = pole_down_min
    d[os.path.basename(k)[:-3]] = d2



"""
look at full traces and make sure that the touches and in range match up well enough
"""
for k in d.values():
    in_range = k['in_range']
    truth_contacts = k['truth_contacts']
    x = np.sum([in_range*2, truth_contacts], axis = 0)
    print(len(np.where(x==1)[0]))

k = list(d.values())[-2]
for k in d.values():
    plt.figure()
    frame_nums = k['frame_nums']
    in_range = k['in_range']
    truth_contacts = k['truth_contacts']
    for i1, i2 in utils.loop_segments(frame_nums):
        x1 = in_range[i1:i2] * 2
        x2 = truth_contacts[i1:i2]
        plt.plot(np.arange(i1, i2), x1 + x2)
    x = np.sum([in_range*2, truth_contacts], axis = 0)
    for kk in np.where(x==1)[0]:
        plt.plot(kk, 2, 'k*')


base_dir = '/Volumes/GoogleDrive-114825029448473821206/My Drive/Colab data/curation_for_auto_curator/DATA_FULL/'
utils.save_obj(d, base_dir+'full_in_range_and_other_useful_data')

fn = '/Volumes/GoogleDrive-114825029448473821206/My Drive/Colab data/curation_for_auto_curator/DATA_FULL/full_in_range_and_other_useful_data.pkl'
fn2 = '/Volumes/GoogleDrive-114825029448473821206/My Drive/Colab data/curation_for_auto_curator/DATA_FULL/full_in_range_16_and_whacc_pred.pkl'
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''
'''##################################################################################################################'''
#
#
# #
# # def pole_relative_first_and_last_touches(h5_file, truth_contacts):
# #   try:
# #     frame_nums = image_tools.get_h5_key_and_concatenate([h5_file], 'frame_nums')
# #   except:
# #
# #     tnfn = image_tools.get_h5_key_and_concatenate([h5_file], 'trial_nums_and_frame_nums')
# #     frame_nums = tnfn[1, :]
# #
# #   pt = image_tools.get_h5_key_and_concatenate([h5_file], 'pole_times')
# #   first_touches = []
# #   last_touches = []
# #   for ii, (i1, i2) in enumerate(utils.loop_segments(frame_nums)):
# #
# #     x = truth_contacts[i1:i2]
# #     tmp1 = np.where(x)[0]
# #     if tmp1.size !=0:
# #       first_touches.append(tmp1[0]-pt[0, ii])
# #       last_touches.append(tmp1[-1]-pt[1, ii])
# #     else:
# #       first_touches.append(np.nan)
# #       last_touches.append(np.nan)
# #   min_first_touch = np.nanmin(first_touches)
# #   max_last_touch = np.nanmax(last_touches)
# #
# #   return min_first_touch, max_last_touch, first_touches, last_touches
# '''##################################################################################################################'''
# '''##################################################################################################################'''
# '''##################################################################################################################'''
#
#
# def pole_relative_first_and_last_touch_arrays(h5_file, truth_contacts, frame_nums=None, pole_times=None):
#     if pole_times is None:
#         pole_times = image_tools.get_h5_key_and_concatenate([h5_file], 'pole_times')
#     if frame_nums is None:
#         try:
#             frame_nums = image_tools.get_h5_key_and_concatenate([h5_file], 'frame_nums')
#         except:
#             tnfn = image_tools.get_h5_key_and_concatenate([h5_file], 'trial_nums_and_frame_nums')
#             frame_nums = tnfn[1, :]
#
#     first_touches = []
#     last_touches = []
#     for ii, (i1, i2) in enumerate(utils.loop_segments(frame_nums)):
#         x = truth_contacts[i1:i2]
#         tmp1 = np.where(x)[0]
#         if tmp1.size != 0:
#             first_touches.append(int(tmp1[0] - pole_times[0, ii]))
#             last_touches.append(int(tmp1[-1] - pole_times[1, ii]))
#         else:
#             first_touches.append(np.nan)
#             last_touches.append(np.nan)
#     return np.asarray(first_touches), np.asarray(last_touches)
#
#
# def pole_touch_latencies(first_touches, last_touches, pole_up_min=40, pole_down_min=40):
#     print('min_first_touch is positive and max_last_touch is negative, was this the best choice? IDK, but know this!')
#     first_touches = copy.deepcopy(first_touches)
#     last_touches = copy.deepcopy(last_touches)
#     # first_touches, last_touches = pole_relative_first_and_last_touches(h5_file, truth_contacts, frame_nums = None, pole_times = None)
#     first_touches[first_touches <= pole_up_min] = 99999999999
#     last_touches[last_touches >= -pole_down_min] = -99999999999
#     min_first_touch = np.nanmin(first_touches)
#     max_last_touch = np.nanmax(last_touches)
#     return min_first_touch, max_last_touch
#
#
# from whacc.utils import get_frame_nums, overwrite_h5_key, loop_segments
# def define_in_range(h5_file, pole_up_set_time=0, pole_down_add_to_trigger=0, write_to_h5=True, return_in_range=False, pole_times = None):
#     with h5py.File(h5_file, 'r+') as hf:
#         if pole_times is None:
#             pole_times = hf['pole_times'][:]
#
#         try:
#             new_in_range = np.zeros_like(hf['in_range'][:])
#         except:
#             new_in_range = np.zeros_like(hf['labels'][:])
#
#         fn = get_frame_nums(h5_file)
#         for i, (i1, i2) in enumerate(loop_segments(fn)):
#             pt = pole_times[:, i] + i1
#             x1 = pt[0] + pole_up_set_time
#             x2 = pt[1] - pole_down_add_to_trigger
#             x2 = min([x2, i2])
#             new_in_range[int(x1):int(x2)] = 1
#     if write_to_h5:
#         overwrite_h5_key(h5_file, 'in_range', new_data=new_in_range)
#     if return_in_range:
#         return new_in_range
#
# base_dir = '/Volumes/GoogleDrive-114825029448473821206/My Drive/Colab data/curation_for_auto_curator/DATA_FULL/'
# h5_list_to_write = utils.sort(utils.lister_it(utils.get_h5s(base_dir, 0), '/3lag/'))
#
# # k = h5_list_to_write[2]
# # truth_contacts = image_tools.get_h5_key_and_concatenate([k], '[0, 1]- (no touch, touch)')
# # first_touches, last_touches = pole_relative_first_and_last_touch_arrays(k, truth_contacts, frame_nums=None,
# #                                                                         pole_times=None)
# # min_first_touch, max_last_touch = pole_touch_latencies(first_touches, last_touches, pole_up_min=40, pole_down_max=40)
#
# # utils.pole_relative_first_and_last_touches = pole_relative_first_and_last_touches
#
# k = '/Volumes/GoogleDrive-114825029448473821206/My Drive/Colab data/curation_for_auto_curator/DATA_FULL/data_AH0698_170601_PM0121_AAAA/regular/AH0698_170601_PM0121_AAAA_regular.h5'
# for iii, k in enumerate(h5_list_to_write):
#     truth_contacts = image_tools.get_h5_key_and_concatenate([k], '[0, 1]- (no touch, touch)')
#     pole_times = image_tools.get_h5_key_and_concatenate(k, 'pole_times')
#     frame_nums = image_tools.get_h5_key_and_concatenate(k, 'frame_nums')
#     if iii in [4, 5]:
#         pole_times = pole_times - 973
#
#         # first_touches = first_touches + 973
#         # last_touches = last_touches + 973
#     first_touches, last_touches = pole_relative_first_and_last_touch_arrays(k,
#                                                                             truth_contacts,
#                                                                             frame_nums=frame_nums,
#                                                                             pole_times=pole_times)
#
#     min_first_touch, max_last_touch = pole_touch_latencies(first_touches, last_touches, pole_up_min=40, pole_down_min=40)
#
#     in_range = define_in_range(k,
#                                  pole_up_set_time=min_first_touch,
#                                  pole_down_add_to_trigger=max_last_touch,
#                                  write_to_h5=False,
#                                  return_in_range=True,
#                                  pole_times = pole_times)
#
#     print(os.path.basename(k))
#     print(min_first_touch)
#     print(max_last_touch)
#     print(np.sum(abs(in_range - 1) * truth_contacts))
#     print('\n')
#
# # actual is 2111 set is 3084
# # actual is 110 set is 1083
# # 1083 - 110
# # 3084 - 2111
# # 973
#
# plt.hist(first_touches+pole_times[0, :], bins=np.arange(150, 300, 1))
# #    last_touches+pole_times[1, :]
#
# k = h5_list_to_write[4]
# k = k.replace('/3lag/', '/regular/')
#
# k = '/Volumes/GoogleDrive-114825029448473821206/My Drive/Colab data/curation_for_auto_curator/DATA_FULL/data_AH1120_200322__/regular/AH1120_200322___regular.h5'
# utils.print_h5_keys(k)
# frame_nums = image_tools.get_h5_key_and_concatenate(k, 'frame_nums')
# # labels = image_tools.get_h5_key_and_concatenate(k, 'labels')
# # pole_times = image_tools.get_h5_key_and_concatenate(k, 'pole_times')
# for i1, i2 in utils.loop_segments(frame_nums):
#     x1 = in_range[i1:i2]*2
#     x2 = truth_contacts[i1:i2]
#     plt.plot(np.arange(i1, i2), x1+x2)
#
# import pdb
# fig, ax = plt.subplots()
# for i, k in enumerate(x3):
#     if i>100:
#         ax.imshow(k)
#         print(i)
#         plt.show()
#         pdb.set_trace()
#
# from whacc import image_tools, utils
# from whacc.touch_curation_GUI import touch_gui
# h5 = '/Volumes/GoogleDrive-114825029448473821206/My Drive/Colab data/curation_for_auto_curator/DATA_FULL/data_AH1131_200326__/regular/AH1131_200326___regular.h5'
# touch_gui(h5, 'labels', label_write_key=None)
# k = h5
#
# h5 = '/Volumes/GoogleDrive-114825029448473821206/My Drive/Colab data/curation_for_auto_curator/DATA_FULL/data_AH1120_200322__/3lag_diff/AH1120_200322___3lag_diff.h5'
# touch_gui(h5, 'labels', label_write_key=None)
# k = h5
# """
# use analyis to plot samsons pole find real pole time and adjust
# """
#
#
#
#
# utils.open_folder()
