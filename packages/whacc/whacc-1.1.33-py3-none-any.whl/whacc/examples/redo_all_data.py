import shutil

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

from whacc import utils
import h5py
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
def foo_save(name_in, data):
    tmp1 = os.path.dirname(name_in)
    Path(tmp1).mkdir(parents=True, exist_ok=True)
    np.save(name_in, data)
from tqdm.contrib import tzip
"""
basically most of what I did is on colab 
code is kinda all over the place 
1) I took the 3lag full session H5 datasets and save frame nums, labels and frame nums to s folder structure as .NPY files
2) I then augmented the full session (didn't cut session off here because I want the final features to have little or no NAN values when shifitng and rolling 
3) in colab I then converted those full sessions to 2048 using GPU for all session 8 normal and 80 augmented 
4) in colab with CPU sessions I generated the final 2105 features
5) no I have to save the raw frame number   

"""
"""
################################################################################################
make the majority labels and the individual labels
################################################################################################
"""
bd = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/'
image_dir = bd + '/images/'
label_dir = bd + '/labels/'
image_files = natsorted(utils.get_files(image_dir, '*.npy'), alg=ns.REAL)

all_h5s = utils.get_h5s('/Volumes/GoogleDrive-114825029448473821206/My Drive/Colab data/curation_for_auto_curator/finished_contacts/')
h_cont, list_of_uniq_files, curator_names = utils._get_human_contacts_(all_h5s, return_curator_names = True)


for i, k in enumerate(list_of_uniq_files): # make sure they match
    to_end = len(k[:-4])
    print(k[:to_end])
    kk = os.path.basename(image_files[i])
    print(kk[:to_end])
    assert kk[:to_end] == k[:to_end], 'files do not match'
    print('___')

for i, k in enumerate(h_cont):
    majority_labels = 1*(np.mean(k, axis=0)>.5)
    kk = os.path.basename(image_files[i])[:-4]
    foo_save(label_dir+'/'+kk, majority_labels)

for ii, name in enumerate(curator_names):
    for i, k in enumerate(h_cont):
        kk = os.path.basename(image_files[i])[:-4]
        labels_2_save = k[ii]
        foo_save(bd+'/individual_labels/'+name+'/'+kk, labels_2_save)


"""
################################################################################################
Save images and augmented images as numpy in different folders
################################################################################################
"""

# h5_meta_data = '/Users/phil/Dropbox/Colab data/H5_data/regular/AH0407_160613_JC1003_AAAC_regular.h5'
# h5_frames = '/Users/phil/Dropbox/Colab data/H5_data/3lag/AH0407_160613_JC1003_AAAC_3lag.h5'
# h5_frames = '/Users/phil/Dropbox/Colab data/H5_data/ALT_LABELS_FINAL_PRED/AH0407_160613_JC1003_AAAC_ALT_LABELS.h5'

border = 80
d_list = ['/Users/phil/Dropbox/Colab data/H5_data/regular/',
          '/Users/phil/Dropbox/Colab data/H5_data/3lag/',
          '/Users/phil/Dropbox/Colab data/H5_data/ALT_LABELS_FINAL_PRED/',
          '/Users/phil/Dropbox/Colab data/H5_data/ALT_LABELS']

h5_meta_images_labels = []
for k in d_list: # just save all the dat to numpy in different folders
    sorted_files = natsorted(utils.get_h5s(k), alg=ns.REAL)
    h5_meta_images_labels.append(sorted_files)

cnt = 0
for h5_meta_data, h5_frames, h5_labels2, h5_labels in tqdm(np.asarray(h5_meta_images_labels).T):
    cnt+=1
    print(cnt)
    if cnt >=7:
        h5_meta_data, h5_frames, h5_labels2, h5_labels = str(h5_meta_data), str(h5_frames), str(h5_labels), str(h5_labels2)

        y = image_tools.get_h5_key_and_concatenate(h5_labels, '[0, 1]- (no touch, touch)')
        OG_frame_nums = image_tools.get_h5_key_and_concatenate(h5_meta_data, 'frame_nums')
        images = image_tools.get_h5_key_and_concatenate(h5_frames, 'images')

        end_name = os.path.basename(h5_frames)[:-3]
        save_dir = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/'
        name = save_dir + '/images/' + end_name
        if not os.path.isfile(name):
            foo_save(name, images)

            name = save_dir + '/frame_nums/' + end_name
            foo_save(name, OG_frame_nums)

            # name = save_dir + '/labels/' + end_name ##### WRONGGGGGGGG
            # foo_save(name, y)

        for aug_num in tqdm(range(10)): # Augment images
            name = save_dir + '/images_AUG_'+ str(aug_num) +'/' + end_name
            if not os.path.isfile(name):
                datagen = ImageDataGenerator(rotation_range=360,  #
                                                width_shift_range=.1,  #
                                                height_shift_range=.1,  #
                                                shear_range=.00,  #
                                                zoom_range=.25,
                                                brightness_range=[0.2, 1.2])  #
                gaussian_noise = iaa.AdditiveGaussianNoise(loc = 0, scale=3)
                num_aug = 1


                aug_img_stack = []
                for image, label in zip(images, y):
                    aug_img, _ = image_tools.augment_helper(datagen, num_aug, 0, image, label)
                    aug_img = gaussian_noise.augment_images(aug_img) # optional
                    aug_img_stack.append(aug_img)

                aug_img_stack = np.squeeze(np.asarray(aug_img_stack))
                foo_save(name, aug_img_stack)
        del images



# RESNET_MODEL = model_maker.load_final_model()
# features = model.predict(x)
"""
################################################################################################
################################################################################################
these are all the inds to the good videos so I can multiply the labels by this and it will 
cancel out all the bad videos by setting the labels to 0 so border extraction will not happen on them!
################################################################################################
################################################################################################
"""


from scipy import stats
ind_naming = '/keep_inds_no_skip_frames/'
bd = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/frame_nums'
bd2 = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/'
all_fn  =[]
sorted_files = natsorted(utils.get_files(bd, '*.npy'), alg=ns.REAL)
for k in sorted_files:
    fn = np.load(k, allow_pickle=True)
    all_fn.append(fn)
    mode = stats.mode(fn)[0][0]
    good_vids = fn==mode
    label_multiply_by = []
    for ii, num_frames in enumerate(fn):
        if good_vids[ii]:
            label_multiply_by.append([1] * num_frames)
        else:
            label_multiply_by.append([0] * num_frames)
    label_multiply_by = np.concatenate(label_multiply_by)
    save_name = bd2 +ind_naming+ '/' + os.path.basename(k)
    if '________________________AH1120_200322' in os.path.basename(k): # remove samsons bad data
        print('AH1120_200322    AH1120_200322    AH1120_200322    AH1120_200322    AH1120_200322    ')
        label_multiply_by = label_multiply_by*0 # remove all of one of samson's datasets
    foo_save(save_name, label_multiply_by)




"""
################################################################################################
################################################################################################
these are all the inds to the good videos so I can multiply the labels by this and it will 
cancel out all the bad videos by setting the labels to 0 so border extraction will not happen on them!
################################################################################################
################################################################################################
"""

from scipy import stats
ind_naming = '/keep_inds_no_skip_frames/'
ind_naming = 'keep_inds_no_pole_hair_no_skip_frames_for_CNN_compare'
bd = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/frame_nums'
bd2 = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/'
all_fn  =[]
sorted_files = natsorted(utils.get_files(bd, '*.npy'), alg=ns.REAL)
for k in sorted_files:
    fn = np.load(k, allow_pickle=True)
    all_fn.append(fn)
    mode = stats.mode(fn)[0][0]
    good_vids = fn==mode
    label_multiply_by = []
    for ii, num_frames in enumerate(fn):
        if good_vids[ii]:
            label_multiply_by.append([1] * num_frames)
        else:
            label_multiply_by.append([0] * num_frames)
    label_multiply_by = np.concatenate(label_multiply_by)
    save_name = bd2 +ind_naming+ '/' + os.path.basename(k)
    if 'AH1120_200322' in os.path.basename(k): # remove samsons bad data
        print('AH1120_200322    AH1120_200322    AH1120_200322    AH1120_200322    AH1120_200322    ')
        label_multiply_by = label_multiply_by*0 # remove all of one of samson's datasets
    foo_save(save_name, label_multiply_by)

"""
######################## make inds for training data for comparing to CNN ##############################################
"""
bd = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/keep_inds_no_pole_hair_no_skip_frames/80_border/T_V_TS_set_inds/'
bd = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/keep_inds_no_skip_frames/80_border/T_V_TS_set_inds/'
for k in utils.get_files(bd, '*.npy'):
    inds = np.load(k, allow_pickle=True)
    inds = np.sort(np.concatenate(inds))

"""
"""
# bd = '/Users/phil/Dropbox/HIRES_LAB/GitHub/Phillip_AC/model_testing/all_data/all_models/regular_80_border/data/3lag/'
# for k in utils.get_h5s(bd):
#     utils.print_h5_keys(k)
#
#
#
# h5 = '/Users/phil/Dropbox/HIRES_LAB/GitHub/Phillip_AC/model_testing/all_data/all_models/regular_80_border/data/3lag/val_3lag.h5'
# utils.print_h5_keys(h5)

"""
################################################################################################
################################################################################################
make the majority labels and the individual labels
################################################################################################
################################################################################################
################################################################################################
"""

border = 80
second_border = 3
split_ratio = [7, 2, 1]
label_dir = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/labels'
regular_dir = '/Users/phil/Dropbox/Colab data/H5_data/regular/'

bd_good_vids = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/keep_inds_no_pole_hair_no_skip_frames/'
bd_good_vids = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/keep_inds_no_pole_hair_no_skip_frames_for_CNN_compare/'
# bd_good_vids = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/keep_inds_no_skip_frames/'
# bd_good_vids = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/keep_inds_no_pole_hair_no_skip_frames_cnn_compare/'

bd_80 = bd_good_vids+'/80_border/'
bd_3 = bd_good_vids+'/3_border/'
# utils.rmtree(bd_3)
# utils.rmtree(bd_80)
"""
get split ratio to copy it 
use it for the first 4 videos and then done 

full set multiply by the 80 border for the train and Val 
"""
split_ratio_list = [[.7, .3], [.7, .3], [.7, .3], [.7, .3], [0,0,1], [0,0,1], [0,0,1], [0,0,1]]
label_files = natsorted(utils.get_files(label_dir, '*.npy'), alg=ns.REAL)
h5_meta_data_files = natsorted(utils.get_files(regular_dir, '*.h5'), alg=ns.REAL)

for i, (label_f, h5_meta_data) in enumerate(zip(label_files, h5_meta_data_files)):
    split_ratio = split_ratio_list[i]
    good_vid_inds = np.load(bd_good_vids+os.path.basename(label_f), allow_pickle=True)
    base_name = os.path.basename(label_f)
    labels = np.load(label_f, allow_pickle=True)
    labels = good_vid_inds*labels # this will remove all the bad videos by making the labels == 0

    if not np.all(labels==0):
        """
        label_f had continious variable, need to source the human data directly and stor ein the folders under the names
        then make a final npy ile with all labels 
        """
        b = utils.inds_around_inds(labels, border * 2 + 1)
        group_inds, _ = utils.group_consecutives(b)
        new_frame_nums = []
        for tmp2 in group_inds:
            new_frame_nums.append(len(tmp2))

        OG_frame_nums = image_tools.get_h5_key_and_concatenate(h5_meta_data, 'frame_nums')
        OG_frame_nums_cumulative = np.cumsum(OG_frame_nums)

        trial_ind_1 = []
        trial_ind_2 = []
        for k in group_inds:
            trial_ind_1.append(np.sum(k[0]>=OG_frame_nums_cumulative))
            trial_ind_2.append(np.sum(k[0]>=OG_frame_nums_cumulative))
        assert np.all(trial_ind_2 == trial_ind_1), 'there are overlapping images from one video to the next, which should be ' \
                                                   'impossible unless the pole stays up between trials '

        np.random.seed(0)
        tmp_sets = utils.split_list(group_inds, split_ratio)
        if len(tmp_sets)==2:
            tmp_sets.append([])

        T_V_TS_sets = []
        frame_nums_set = []
        labels_80 = []
        # labels = np.asarray(labels)
        for k in tmp_sets:
            if len(k) == 0:
                T_V_TS_sets.append(sorted(k))
            else:
                T_V_TS_sets.append(sorted(np.concatenate(k)))
            frame_nums_set.append(len(k))
            labels_80.append(labels[T_V_TS_sets[-1]])
        foo_save(bd_80 + '/T_V_TS_set_inds_CNN_COMPARE/'+base_name, list(T_V_TS_sets))
        # foo_save(bd_80 + '/labels/'+ base_name, labels_80)

        # T_V_TS_sets_3_border = []
        # labels_3 = []
        # for k in T_V_TS_sets:
        #     tmp_labels = labels[k]
        #     b = utils.inds_around_inds(tmp_labels, second_border * 2 + 1)
        #     group_inds, _ = utils.group_consecutives(b)
        #     border_3_inds = np.asarray(k)[np.concatenate(group_inds)]
        #     T_V_TS_sets_3_border.append(border_3_inds)
        #     labels_3.append(labels[T_V_TS_sets_3_border[-1]])
        #
        # # foo_save(bd_3 + '/T_V_TS_set_inds_cnn_compare/'+ base_name, T_V_TS_sets_3_border)
        # foo_save(bd_3 + '/T_V_TS_set_inds/'+ base_name, T_V_TS_sets_3_border)
        # foo_save(bd_3 + '/labels/'+ base_name, labels_3)
bd = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/keep_inds_no_pole_hair_no_skip_frames_for_CNN_compare/80_border/T_V_TS_set_inds_CNN_COMPARE'

for k in utils.get_files(bd, '*.npy'):
    tmp1 = np.load(k, allow_pickle=True)
    print(len(tmp1))
    asdf


bd = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/keep_inds_no_pole_hair_no_skip_frames/80_border/'
ind_dir = bd+'/T_V_TS_set_inds/'
save_data_dir = bd + '/final_2105/'
feature_dir = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/final_2105/'
feature_files = utils.sort(utils.get_files(feature_dir, '*.npy'))
feature_files_base_names = np.asarray([os.path.basename(k) for k in feature_files])
for k in tqdm(utils.sort(utils.get_files(ind_dir, '*.npy'))):
    tmp1 = np.load(k, allow_pickle=True)

    basename_inds = os.path.basename(k)
    iii = np.where(basename_inds == feature_files_base_names)[0][0]
    data_file = feature_files[iii]




    # label_file = utils.norm_path(save_data_dir+os.path.basename(data_file), '/').split('/')
    # label_file[-2] = 'labels'
    # label_file = '/' + '/'.join(label_file)
    # labels = np.load(label_file, allow_pickle=True)

    base_name = '_'+os.path.basename(data_file)
    run_it = False
    for (inds, save_name) in zip(tmp1, ['train', 'val', 'test']):
        fn = save_data_dir+save_name+base_name
        # labels_name = os.path.dirname(fn)+'_labels/'+os.path.basename(fn)
        # x = labels[inds]
        # foo_save(labels_name, x)
        if os.path.isfile(fn):
            run_it = True
    if run_it:
        final_2105 = np.load(data_file, allow_pickle=True)
        for (inds, save_name) in zip(tmp1, ['train', 'val', 'test']):
            x = final_2105[inds, :]
            foo_save(save_data_dir+save_name+base_name, x)
            #make new folder

"""
need to add the labels here too

"""



bd = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/keep_inds_no_pole_hair_no_skip_frames/3_border/'
ind_dir = bd+'/T_V_TS_set_inds/'

for folder_num in range(10):
    feature_dir = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/final_2105_AUG_'+str(folder_num)+os.sep
    save_data_dir = bd + '/final_2105'+'_AUG_'+str(folder_num)+os.sep
    feature_files = utils.sort(utils.get_files(feature_dir, '*.npy'))
    feature_files_base_names = np.asarray([os.path.basename(k) for k in feature_files])
    for k in tqdm(utils.sort(utils.get_files(ind_dir, '*.npy'))):
        basename_inds = os.path.basename(k)
        iii = np.where(basename_inds == feature_files_base_names)[0][0]
        data_file = feature_files[iii]
        base_name = '_'+os.path.basename(data_file)
        run_it = False

        for save_name in ['train', 'val', 'test']:
            fn = save_data_dir+save_name+base_name
            if not os.path.isfile(fn):
                run_it = True

        if run_it:
            tmp1 = np.load(k, allow_pickle=True)
            final_2105 = np.load(data_file, allow_pickle=True)
            for (inds, save_name) in zip(tmp1, ['train', 'val', 'test']):
                x = final_2105[inds, :]
                foo_save(save_data_dir+save_name+base_name, x)


        #
        # base_name = '_'+os.path.basename(data_file)
        # for (inds, save_name) in zip(tmp1, ['train', 'val', 'test']):
        #     x = final_2105[inds, :]
        #     foo_save(save_data_dir+save_name+base_name, x)
        # if run_it:
        #     final_2105 = np.load(data_file, allow_pickle=True)
        #


"""
################################################################################################
################################################################################################
################################################################################################
################################################################################################
generate the final datasets 
need to account for missing frame datasets and samsons dataset 

shit I realized i need to remove the bad ones and then chose the final indexes otherwise it can reduce the 
total number of in any particular set 


ok so to re
"""
h5 = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/keep_inds_no_pole_hair_no_skip_frames/80_border/T_V_TS_set_inds/AH0407_160613_JC1003_AAAC_3lag.npy'
h5 = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/keep_inds_no_pole_hair_no_skip_frames/80_border/T_V_TS_set_inds/AH0407_160613_JC1003_AAAC_3lag.npy'
h5_list = utils.get_h5s('/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/keep_inds_no_pole_hair_no_skip_frames/80_border/T_V_TS_set_inds')
utils.print_h5_keys(h5)
np_in = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/keep_inds_no_pole_hair_no_skip_frames/80_border/T_V_TS_set_inds/AH0407_160613_JC1003_AAAC_3lag.npy'
tmp1 = np.load(np_in, allow_pickle=True)

tmp1[0]


################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################

def foo_save(name_in, data):
        tmp1 = os.path.dirname(name_in)
        Path(tmp1).mkdir(parents=True, exist_ok=True)
        np.save(name_in, data)
# h5_meta_data = '/Users/phil/Dropbox/Colab data/H5_data/regular/AH0407_160613_JC1003_AAAC_regular.h5'
# h5_frames = '/Users/phil/Dropbox/Colab data/H5_data/3lag/AH0407_160613_JC1003_AAAC_3lag.h5'
# h5_frames = '/Users/phil/Dropbox/Colab data/H5_data/ALT_LABELS_FINAL_PRED/AH0407_160613_JC1003_AAAC_ALT_LABELS.h5'

border = 80
d_list = ['/Users/phil/Dropbox/Colab data/H5_data/regular/',
          '/Users/phil/Dropbox/Colab data/H5_data/3lag/',
          '/Users/phil/Dropbox/Colab data/H5_data/ALT_LABELS_FINAL_PRED/',
          '/Users/phil/Dropbox/Colab data/H5_data/ALT_LABELS']

h5_meta_images_labels = []
for k in d_list:
    sorted_files = natsorted(utils.get_h5s(k), alg=ns.REAL)
    h5_meta_images_labels.append(sorted_files)

for h5_meta_data, h5_frames, h5_labels2, h5_labels in tqdm(np.asarray(h5_meta_images_labels).T):
    # for k in [h5_meta_data, h5_frames, h5_labels2, h5_labels]:
    #     print(os.path.basename(k))
    # print('______')
    h5_meta_data, h5_frames, h5_labels2, h5_labels = str(h5_meta_data), str(h5_frames), str(h5_labels), str(h5_labels2)

    # get the 80 border indices and the 3 border indices
    y = image_tools.get_h5_key_and_concatenate(h5_labels, '[0, 1]- (no touch, touch)')


    # y = np.zeros(4001)
    # y[2000] = 1
    OG_frame_nums = image_tools.get_h5_key_and_concatenate(h5_meta_data, 'frame_nums')
    b = utils.inds_around_inds(y, border * 2 + 1)
    group_inds, result_ind = utils.group_consecutives(b)
    new_frame_nums = []
    for tmp2 in group_inds:
        new_frame_nums.append(len(tmp2))

    OG_frame_nums_cumulative = np.cumsum(OG_frame_nums)
    trial_ind_1 = []
    trial_ind_2 = []
    for k in group_inds:
        trial_ind_1.append(np.sum(k[0]>=OG_frame_nums_cumulative))
        trial_ind_2.append(np.sum(k[0]>=OG_frame_nums_cumulative))
    assert np.all(trial_ind_2 == trial_ind_1), 'there are overlapping images from one video to the next'

    images = image_tools.get_h5_key_and_concatenate(h5_frames, 'images')
    extracted_images = images[np.concatenate(group_inds), :, :, :]

    del images
    labels = np.asarray(y)[np.concatenate(group_inds)]
    end_name = os.path.basename(h5_frames)[:-3]
    name = '/Users/phil/Dropbox/Colab data/H5_data/3lag_80_border_numpy/images/' + end_name
    foo_save(name, extracted_images)
    name = '/Users/phil/Dropbox/Colab data/H5_data/3lag_80_border_numpy/80_border_inds/' + end_name
    foo_save(name, group_inds)
    name = '/Users/phil/Dropbox/Colab data/H5_data/3lag_80_border_numpy/frame_nums/' + end_name
    foo_save(name, new_frame_nums)
    # name = '/Users/phil/Dropbox/Colab data/H5_data/3lag_80_border_numpy/labels/' + end_name # WRONGGGGGG
    # foo_save(name, labels)
    del extracted_images

    #
    # for aug_num in range(10):
    #     datagen = ImageDataGenerator(rotation_range=360,  #
    #                                     width_shift_range=.1,  #
    #                                     height_shift_range=.1,  #
    #                                     shear_range=.00,  #
    #                                     zoom_range=.25,
    #                                     brightness_range=[0.2, 1.2])  #
    #     gaussian_noise = iaa.AdditiveGaussianNoise(loc = 0, scale=3)
    #     num_aug = 1
    #
    #
    #     aug_img_stack = []
    #     # labels_stack = []
    #     for image, label in tzip(zip(images, labels)):
    #         aug_img, label_copy = image_tools.augment_helper(datagen, num_aug, 0, image, label)
    #         aug_img = gaussian_noise.augment_images(aug_img) # optional
    #         aug_img_stack.append(aug_img)
    #         # labels_stack.append(label_copy)
    #     name = '/Users/phil/Dropbox/Colab data/H5_data/3lag_80_border_numpy/images_AUG_'+ str(aug_num) +'/' + end_name
    #
    #     np.squeeze(np.asarray(aug_img_stack))
    #     foo_save(name, extracted_images)




################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################

new_keys = 'src_file'  # ull
# src_file - full directory of all source files


ID_keys = ['file_name_nums',
           'frame_nums',
           'in_range',
           'labels',
           'trial_nums_and_frame_nums',
           'full_file_names',]
for key in ID_keys:
    value = image_tools.get_h5_key_and_concatenate(h5_meta_data, key)

    print(key)
    utils.info(value)
    print('________')
    # for k in trial_ind_1:
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
# for k in utils.get_files(bd, '*.npy'):
#     os.rename(k, k.replace('.h5', ''))


bd = '/Users/phil/Dropbox/Colab data/H5_data/3lag_80_border_numpy/'
fold_list = sorted(next(os.walk(bd))[1])

borderINDS_frame_NUMS_images_labels = []
for k in fold_list:
    sorted_files = natsorted(utils.get_files(bd+k, '*.npy'), alg=ns.REAL)
    borderINDS_frame_NUMS_images_labels.append(sorted_files)

for border_inds, frame_nums, images, labels in tqdm(np.asarray(borderINDS_frame_NUMS_images_labels).T):
    # for k in [border_inds, frame_nums, images, labels]:
    #     print(os.path.basename(k))
    # print('______')
    border_inds, frame_nums, images, labels = str(border_inds), str(frame_nums), str(images), str(labels)
    border_inds, frame_nums, images, labels = np.load(border_inds, allow_pickle=True), np.load(frame_nums, allow_pickle=True), np.load(images, allow_pickle=True), np.load(labels, allow_pickle=True)


datagen = ImageDataGenerator(rotation_range=360,  #
                                width_shift_range=.1,  #
                                height_shift_range=.1,  #
                                shear_range=.00,  #
                                zoom_range=.25,
                                brightness_range=[0.2, 1.2])  #
gaussian_noise = iaa.AdditiveGaussianNoise(loc = 0, scale=3)
num_aug = 1

ind = 80
aug_img_stack = []
labels_stack = []
for image, label in tqdm(zip(images, labels)):
    aug_img, label_copy = image_tools.augment_helper(datagen, num_aug, 0, image, label)
    aug_img = gaussian_noise.augment_images(aug_img) # optional
    aug_img_stack.append(aug_img)
    labels_stack.append(label_copy)





h5creator.add_to_h5(aug_img_stack[:, :, :, :], labels_stack)
utils.copy_h5_key_to_another_h5(each_h5, new_H5_file, 'frame_nums', 'frame_nums') # copy the frame nums to the sug files
# combine all the
image_tools.split_h5_loop_segments(combine_list,
                                     [1],
                                     each_h5.split('.h5')[0]+'_AUG.h5',
                                     add_numbers_to_name = False,
                                     set_seed=0,
                                     color_channel=True)


"""
#### add frame nums 
"""

bd = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/keep_inds_no_pole_hair_no_skip_frames/80_border/T_V_TS_set_inds'
bd = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/keep_inds_no_pole_hair_no_skip_frames/3_border/T_V_TS_set_inds'
bd = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/keep_inds_no_pole_hair_no_skip_frames_for_CNN_compare/80_border/T_V_TS_set_inds_CNN_COMPARE/'
replace_string = 'T_V_TS_set_inds'
for f in tqdm(utils.sort(utils.get_files(bd, '*.npy'))):
    data_list = np.load(f, allow_pickle=True)
    frame_nums_list = []
    for k in data_list:
        result, result_ind = utils.group_consecutives(k)
        fn = [len(kk) for kk in result]
        frame_nums_list.append(fn)
    f2 = f.replace(replace_string, 'frame_nums')
    utils.make_path(os.path.dirname(f2))
    np.save(f2, frame_nums_list)



"""
everything about indexing can be done later
just get the images for now 
that mean just get the images for 3 and 80 
upload and start running the 80 through colab
then augment the 3 
then run the 3 augmented 
worry about the labels later tonight  
"""



"""
loop through group inds 
assert they are between some value of the loop segments

"""




"""
##########################################################################################
##########################################################################################
MAKE THE REGULAR IMAGES FROM THE 3LAG IMAGES FOR THE CNN DIRECT COMPARISONS
##########################################################################################
##########################################################################################
"""

bd = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/images'
replace_string = 'regular_numpy_for_final_CNN_comparison_to_LGBM'
for k in tqdm(utils.get_files(bd, '*.npy')):
    images = np.load(k, allow_pickle=True)
    reg_images = images[:, :, :, 2]
    reg_images = np.repeat(reg_images[:, :, :, None], 3, axis=3)
    foo_save(k.replace('3lag_numpy_aug_for_final_LGBM', replace_string), reg_images)
