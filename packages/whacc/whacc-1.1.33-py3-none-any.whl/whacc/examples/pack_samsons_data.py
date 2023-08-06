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

"""
################################################################################################
################################################################################################
################################################################################################
################################################################################################
"""
#  match the sessions


#
"""
################################################################################################
################################################################################################
################################################################################################
################################################################################################
"""

bd_fileLists = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1jFuXGPmP8QNNZxuCzCA8qVItvPJvg8hU/contactsMatter/fileLists/'
bd_binarizedContacts_All = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1jFuXGPmP8QNNZxuCzCA8qVItvPJvg8hU/contactsMatter/binarizedContacts_All/'
save_dir = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1jFuXGPmP8QNNZxuCzCA8qVItvPJvg8hU/contactsMatter/dictionary_saves/'
utils.make_path(save_dir)

final_dict = dict()
bd_fileLists = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1jFuXGPmP8QNNZxuCzCA8qVItvPJvg8hU/contactsMatter/fileLists'
f_list = utils.sort(utils.get_files(bd_fileLists, '*.mat'))
for f in tqdm(f_list):
    d = dict()
    tmp1 = utils.loadmat(f)
    fileList = tmp1['fileList']
    d['file_list'] = fileList
    add_name = os.path.basename(f).split('_fileList.mat')[0]
    contact_dir = bd_binarizedContacts_All + add_name
    all_contacts = []
    frame_nums = []
    contact_names = utils.sort(utils.get_files(contact_dir, '*.mat'))
    d['contact_names'] = contact_names

    for k in contact_names:
        tmp2 = utils.loadmat(k)['binarizedContacts']
        frame_nums.append(len(tmp2))
        all_contacts.append(tmp2)
    d['contacts'] = all_contacts
    d['frame_nums'] = frame_nums

    save_name = save_dir + add_name + '.pkl'
    utils.save_obj(d, save_name)
    final_dict[add_name] = d

save_name = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1jFuXGPmP8QNNZxuCzCA8qVItvPJvg8hU/contactsMatter/final_dict.pkl'
utils.save_obj(final_dict, save_name)

final_dict = utils.load_obj(save_name)
"""
final_dict is a dict of dicts, each inside dict is a session each ones of those has the following 

contact_names type->   list           ...ntacts_All/Session14/Session14_100.mat']
contacts      type->   list           ...y([0, 0, 0, ..., 0, 0, 0], dtype=uint8)]
frame_nums    type->   list           ...000, 3000, 3000, 3000, 3000, 3000, 3000]
file_list     type->   numpy.ndarray  ...\Session14\\AH1179X01062021x14-100.mp4']

utils.info(final_dict['Session1'])
"""


def smooth(y, box_pts):  # $%
    box = np.ones(box_pts) / box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth


def h5_to_dict(h5_in):
    d = dict()
    with h5py.File(h5_in, 'r') as h:
        for k in h.keys():
            d[k] = h[k][:]
    return d


T_V_Test_dict = [{'file_list': [], 'contact_names': [], 'contacts': [], 'frame_nums': [], 'session': [],
                  'session_index': [],
                  '80_border_inds': [], '20_border_inds': [], '10_border_inds': [], '3_border_inds': []}] * 3

for k in final_dict.keys():  # k are key strings names 'session1' etc
    L = len(final_dict[k]['frame_nums'])
    np.random.seed(0)
    T_V_Test_inds = utils.split_list_inds(range(L), [6, 2, 2])
    final_dict[k]['T_V_Test_inds'] = T_V_Test_inds
    for ind1, kk in enumerate(T_V_Test_inds):  # ind1 is 0 1 or 2 or t v and test, kk are the file inds
        for i in kk:
            T_V_Test_dict[ind1]['session_index'].append(i)
            T_V_Test_dict[ind1]['session'].append(k)
            T_V_Test_dict[ind1]['file_list'].append(final_dict[k]['file_list'][i])
            T_V_Test_dict[ind1]['contact_names'].append(final_dict[k]['contact_names'][i])
            T_V_Test_dict[ind1]['frame_nums'].append(final_dict[k]['frame_nums'][i])
            T_V_Test_dict[ind1]['contacts'].append(final_dict[k]['contacts'][i])
            for border_tmp in [80, 20, 10, 3]:
                border = border_tmp * 2 + 1
                tmp2 = smooth(T_V_Test_dict[ind1]['contacts'][-1], border)
                good_inds = tmp2 > 0
                T_V_Test_dict[ind1][str(border_tmp) + '_border_inds'].append(good_inds)
                """
                so it looks like the 80 border used the list of contacts from its own subset selection (i.e. training validation test)
                so I will need to 
                so it randomizes the files into trianing validation and test 
                then makes contact, files list etc for those mixed sets 
                then for those contacts (that are mixed and indexed) it takes teh 80 border for those meaning that the index 
                of the 80 border 
                """

for k in T_V_Test_dict:
    print(len(k['contacts']))
    # print(np.sum(np.concatenate(k['80_border_inds'])))

save_name = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1jFuXGPmP8QNNZxuCzCA8qVItvPJvg8hU/contactsMatter/final_T_V_Test_dict.pkl'
utils.save_obj(T_V_Test_dict, save_name)

T_V_Test_dict = utils.load_obj(save_name)

utils.info(T_V_Test_dict[0])

utils.info(T_V_Test_dict[0]['session'])

final_dict['Session1']['file_list'][:4]

h5_bd_session = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1pUteMEgx37rAyqujJWxVN9-ywFAqaxhF/WhACC_PROCESSING_FOLDER/Session1_FINISHED/'
# fn = []
for set_dict in T_V_Test_dict:  # list of dicts each with all info needed to make sets
    # from set_dict I need the session and the video number that matches
    for sess in np.unique(set_dict['session']):  # ook through all the session
        h5_list = utils.sort(utils.get_h5s(h5_bd_session + sess))  # get list of h5s per each session
        each_h5_inds = [int(os.path.basename(k).split('-')[-1][:-4]) for k in set_dict['file_list'][:]]
        sess_inds = np.asarray(set_dict['session'][:]) == sess
        for h5 in h5_list:  # for now just session 1 TEMP
            with h5py.File(h5, 'r') as h:
                full_file_names = [n.decode("ascii", "ignore") for n in h['full_file_names'][:]]
                file_name_nums = h['file_name_nums'][:]
                np.unique(file_name_nums)

                final_features_2105 = h['final_features_2105'][:]

                print(h.keys())
                fn = h['frame_nums'][:]
                asdf

h = h5_to_dict(h5)
utils.info(h)
full_file_names = [n.decode("ascii", "ignore") for n in h['full_file_names'][:]]

utils.info(set_dict)

set_dict['file_list'][-1]
set_dict['contact_names'][-1]

all_features = []
for h5 in tqdm(h5_list):
    with h5py.File(h5, 'r') as h:
        all_features.append(h['final_features_2105'][:])


def combine_final_h5s(h5_file_list_to_combine, delete_extra_files=False):
    fn = h5_file_list_to_combine[0].split('final')[0] + 'final_combined.h5'
    h5c = image_tools.h5_iterative_creator(fn,
                                           overwrite_if_file_exists=True,
                                           max_img_height=1,
                                           max_img_width=2105,
                                           close_and_open_on_each_iteration=True,
                                           color_channel=False,
                                           add_to_existing_H5=False,
                                           ignore_image_range_warning=False,
                                           dtype_img=h5py.h5t.IEEE_F32LE,
                                           dtype_labels=h5py.h5t.IEEE_F32LE,
                                           image_key_name='final_features_2105')

    for k in tqdm(h5_file_list_to_combine):
        with h5py.File(k, 'r') as h:
            # print(h.keys())
            final_features_2105 = h['final_features_2105'][:]
            h5c.add_to_h5(final_features_2105, np.ones(final_features_2105.shape[0]) * -1)
    with h5py.File(fn, 'r+') as h:
        del h['labels']

    keys = ['file_name_nums', 'frame_nums', 'full_file_names', 'in_range', 'labels',
            'locations_x_y', 'max_val_stack']

    trial_nums_and_frame_nums = []
    for k in h5_file_list_to_combine:
        print(k)
        trial_nums_and_frame_nums.append(image_tools.get_h5_key_and_concatenate(str(k), 'trial_nums_and_frame_nums'))
    trial_nums_and_frame_nums = np.hstack(trial_nums_and_frame_nums)

    with h5py.File(fn, 'r+') as h:
        for k in keys:
            print(k)
            out = image_tools.get_h5_key_and_concatenate(h5_file_list_to_combine, k)
            h[k] = out

    utils.overwrite_h5_key(fn, 'template_img',
                           image_tools.get_h5_key_and_concatenate(h5_file_list_to_combine[0], 'template_img'))
    utils.overwrite_h5_key(fn, 'multiplier',
                           image_tools.get_h5_key_and_concatenate(h5_file_list_to_combine[0], 'multiplier'))
    utils.overwrite_h5_key(fn, 'trial_nums_and_frame_nums',
                           image_tools.get_h5_key_and_concatenate(h5_file_list_to_combine[0],
                                                                  'trial_nums_and_frame_nums'))
    if delete_extra_files:
        for k in h5_file_list_to_combine:
            os.remove(k)


h5_bd_session = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1pUteMEgx37rAyqujJWxVN9-ywFAqaxhF/WhACC_PROCESSING_FOLDER/Session1_FINISHED/'
# h5_bd_session = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1pUteMEgx37rAyqujJWxVN9-ywFAqaxhF/WhACC_PROCESSING_FOLDER/Session1_FINISHED/Session1/untitled folder/'
h5_file_list_to_combine = [str(k) for k in
                           utils.sort(utils.lister_it(utils.get_h5s(h5_bd_session), 'final_to_combine'))]
combine_final_h5s(h5_file_list_to_combine, delete_extra_files=False)

tmp1 = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1pUteMEgx37rAyqujJWxVN9-ywFAqaxhF/WhACC_PROCESSING_FOLDER/Session1_FINISHED/Session1/AH1179X23052021x1_final_combined.h5'
with h5py.File(tmp1, 'r') as h:
    for k in h.keys():
        print(k)
        try:
            print(h[k][:].shape)
        except:
            pass
        print('___')
print('___')
print('___')
print('___')
tmp1 = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1pUteMEgx37rAyqujJWxVN9-ywFAqaxhF/WhACC_PROCESSING_FOLDER/Session1_FINISHED/Session1/AH1179X23052021x1_final_to_combine_6_to_10_of_299.h5'
with h5py.File(tmp1, 'r') as h:
    for k in h.keys():
        print(k)
        try:
            print(h[k][:].shape)
        except:
            pass
        print('___')

h5_bd_session = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1pUteMEgx37rAyqujJWxVN9-ywFAqaxhF/WhACC_PROCESSING_FOLDER/Session1_FINISHED/'
utils.auto_combine_final_h5s(h5_bd_session, False)

utils.print_h5_keys(
    '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1pUteMEgx37rAyqujJWxVN9-ywFAqaxhF/WhACC_PROCESSING_FOLDER/Session1_FINISHED/Session1/untitled folder/AH1179X23052021x1_final_combined.h5')
utils.print_h5_keys(
    '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1pUteMEgx37rAyqujJWxVN9-ywFAqaxhF/WhACC_PROCESSING_FOLDER/Session1_FINISHED/Session1/untitled folder/AH1179X23052021x1_final_to_combine_1_to_5_of_299.h5')

k = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1pUteMEgx37rAyqujJWxVN9-ywFAqaxhF/WhACC_PROCESSING_FOLDER/Session1_FINISHED/Session1/untitled folder/AH1179X23052021x1_final_to_combine_1_to_5_of_299.h5'
k = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1pUteMEgx37rAyqujJWxVN9-ywFAqaxhF/WhACC_PROCESSING_FOLDER/Session1_FINISHED/Session1/untitled folder/AH1179X23052021x1_final_to_combine_1_to_5_of_299.h5'
utils.print_h5_keys(k)
trial_nums_and_frame_nums = []
trial_nums_and_frame_nums.append(image_tools.get_h5_key_and_concatenate(k, 'trial_nums_and_frame_nums'))

trial_nums_and_frame_nums = []
for k in h5_file_list_to_combine:
    print(k)
    trial_nums_and_frame_nums.append(image_tools.get_h5_key_and_concatenate(k, 'trial_nums_and_frame_nums'))

utils.auto_combine_final_h5s(h5_bd_session, False)

h5 = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1pUteMEgx37rAyqujJWxVN9-ywFAqaxhF/WhACC_PROCESSING_FOLDER/Session1_FINISHED/Session1/AH1179X23052021x1_final_combined.h5'
utils.print_h5_keys(h5)
# match the files with the contacts
utils.info(T_V_Test_dict[0])

file_name_nums_from_features = np.asarray(
    [int(os.path.basename(k.decode("ascii", "ignore")).split('-')[-1][:-4]) for k in
     image_tools.get_h5_key_and_concatenate(h5, 'full_file_names')])

save_name = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1jFuXGPmP8QNNZxuCzCA8qVItvPJvg8hU/contactsMatter/final_T_V_Test_dict.pkl'
T_V_Test_dict = utils.load_obj(save_name)

import pdb


def foo_save_data(save_bd, features, labels):
    utils.make_path(os.path.dirname(save_bd))
    features = np.vstack(features)
    labels = np.concatenate(labels)
    np.save(save_bd + '_features', features)
    np.save(save_bd + '_labels', labels)


border_key = '80_border_inds'
# get same session, match all the contacts

bd = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1pUteMEgx37rAyqujJWxVN9-ywFAqaxhF/WhACC_PROCESSING_FOLDER/'
save_bd = bd + '/samson_model_data/'

cnt = 0
save_cnt = 0
save_every_x = 50
dataset = T_V_Test_dict[0]
for (dataset, dataset_name) in zip(T_V_Test_dict, ['train', 'val', 'test']):
    for i in range(len(dataset['file_list'])):
        f = dataset['file_list'][i]
        f = utils.norm_path(f)
        fn_cont = dataset['frame_nums'][i]
        contacts = dataset['contacts'][i]
        border_inds = dataset[border_key][i]
        sess = os.path.basename(os.path.dirname(f))

        # h5 from matching session
        h5 = bd + sess + '_FINISHED/' + sess
        h5 = utils.get_files(h5, '*final_combined.h5')
        assert len(h5) == 1, 'asdfasdf'
        h5 = h5[0]

        frame_nums_from_features = image_tools.get_h5_key_and_concatenate(h5, 'frame_nums')
        # below matches the contact SESSION already
        file_name_nums_from_features = np.asarray(
            [int(os.path.basename(k.decode("ascii", "ignore")).split('-')[-1][:-4]) for k in
             image_tools.get_h5_key_and_concatenate(h5, 'full_file_names')])
        file_name_num_from_contacts = int(os.path.basename(f.split('-')[-1][:-4]))
        ind = np.where(file_name_num_from_contacts == file_name_nums_from_features)[0]  # ind to the feature data

        if len(ind) == 0:
            print('no match\n')
            # pass # no match
        elif len(ind) > 1:
            assert False, 'more than one match this is impossible'
        else:

            if cnt // save_every_x == cnt / save_every_x:
                if save_cnt > 0:
                    foo_save_data(save_bd + '/' + dataset_name + '/' + str(save_cnt).zfill(3), final_features_2105_TEMP,
                                  contact_TEMP)
                    pdb.set_trace()
                save_cnt += 1
                final_features_2105_TEMP = []
                contact_TEMP = []
                cnt = 0
            cnt += 1
            ind = ind[0]
            loop_segs = np.asarray(utils.loop_segments(frame_nums_from_features, True))
            with h5py.File(h5, 'r') as h:
                final_features_2105 = h['final_features_2105'][loop_segs[0, ind]:loop_segs[1, ind]]
            # final_features_2105 = image_tools.get_h5_key_and_concatenate(h5, 'final_features_2105')
            fn_f = frame_nums_from_features[ind]
            assert fn_f == fn_cont, 'frame number miss match WTF'
            contact_TEMP.append(contacts[border_inds])
            final_features_2105_TEMP.append(final_features_2105[border_inds, :])
            print(len(contacts[border_inds]))
    if cnt != save_every_x:  # save remainder files
        foo_save_data(save_bd + '/' + dataset_name + '/' + str(save_cnt).zfill(3), final_features_2105_TEMP,
                      contact_TEMP)

np.asarray(tmp1)
loop_segs = np.asarray(utils.loop_segments(frame_nums_from_features, True))

"""
chekc if file synced for samsons data

24 core convert all of the h5s into a single H5 file. 
"""

cnt1 = 0
cnt2 = 0
bd = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1pUteMEgx37rAyqujJWxVN9-ywFAqaxhF/WhACC_PROCESSING_FOLDER/'
from whacc.utils import get_files, load_obj, sort

finished_sessions = get_files(bd, '*file_list_for_batch_processing.pkl')
for f in tqdm(finished_sessions):
    file_dict = load_obj(f)
    if np.all(file_dict['is_processed'] == True):
        print(f)
        h5_file_list_to_combine = sort(get_files(os.path.dirname(f), '*_final_to_combine_*'))
        print(len(h5_file_list_to_combine))
        if len(h5_file_list_to_combine) > 0:
            cnt1 += 1
        else:
            cnt2 += 1

"""
checks 
same ending file name number 
same number of frames 

INSERT SAMSONS PREDICTIONS INTO THE FINAL H5 FILES 
"""
bd = 'H:\My Drive\WhACC_PROCESSING_FOLDER'
sess_list = utils.sort(utils.lister_it(utils.get_files(bd, '*_final_combined.h5'), remove_string='\\processing'))
save_key = 'contacts_samson_curated_for_transfer_learning_220707'
for h5 in tqdm(sess_list):
    sess_string = os.path.basename(os.path.dirname(utils.norm_path(h5, '/')))
    d = None
    samsons_contacts_list = []
    if sess_string in final_dict.keys():
        d = final_dict[sess_string]
        file_list_2 = [os.path.basename(k) for k in d['file_list']]

        with h5py.File(h5, 'r+') as h:
            labels = h['labels'][:]
            frame_nums_1 = h['frame_nums'][:]
            full_file_names_1 = h['full_file_names'][:]
            file_list_1 = [k.decode("ascii", "ignore") for k in full_file_names_1]
            for iii, k in enumerate(file_list_1):
                fn_1 = int(frame_nums_1[iii])
                vid_ind_to_contacts_dict = np.where(k == np.asarray(file_list_2))[0]

                if vid_ind_to_contacts_dict.shape[0] == 1:
                    assert fn_1 == d['frame_nums'][vid_ind_to_contacts_dict[0]]
                    contacts_tmp = d['contacts'][vid_ind_to_contacts_dict[0]]
                else:
                    #                     print(' no file overlap for this file --> ' + k)
                    contacts_tmp = np.ones(fn_1) * -1
                contacts_tmp = contacts_tmp.astype(np.float32)
                samsons_contacts_list.append(contacts_tmp)
        assert len(np.concatenate(samsons_contacts_list)) == len(labels), 'mismatch size'
#         utils.overwrite_h5_key(h5, save_key, np.concatenate(samsons_contacts_list))


"""
####################################################################################################

####################################################################################################
CREATING THE INDS TO THE SPLIT DATA FOR DIFFERENT BORDERS 
####################################################################################################
"""



split_ratio = np.asarray([6, 2, 2])
split_ratio = np.round(100*(split_ratio/np.sum(split_ratio))).astype(int)
tvt_name_string = ['train', 'val', 'test']

border_contact_lists = [[],[],[]]
for border in [3, 10, 20, 40, 80]:
    for h5 in tqdm(sess_list):
        with h5py.File(h5, 'r') as h:
            fn = h['frame_nums'][:]
            c = h['contacts_samson_curated_for_transfer_learning_220707'][:]
        good_trials = []
        for i, (f1, f2) in enumerate(utils.loop_segments(fn)):
            good_trials.append(not np.any(c[f1:f2]==-1))
        np.random.seed(42)
        good_trial_inds = np.where(good_trials)[0]
        T_V_Test_inds = utils.split_list(good_trial_inds, split_ratio)
        T_V_Test_inds = [sorted(k) for k in T_V_Test_inds]
        border_contact_lists = [[],[],[]]
        for i, (f1, f2) in enumerate(utils.loop_segments(fn)):
            c2 = c[f1:f2] # make new contacts ans set other trials to -1
            for ii, tmp1 in enumerate(T_V_Test_inds):
                if i in tmp1:
                    border_contact_lists[ii].append(c2)
                else:
                    border_contact_lists[ii].append(np.ones_like(c2)*-1)

#         border_inds_TVT = [[],[],[]]
        for i, TVT_inds in enumerate(border_contact_lists):
            border_inds = []
            for k in TVT_inds:
                x = utils.smooth(k, border)
                border_inds.append(x>0)
            final_save_inds = np.concatenate(border_inds)
            assert len(c) == len(final_save_inds), 'mis match size'
            save_name = str(border)+'_border_' + tvt_name_string[i] + '_set_' + str(split_ratio[i])+'%_data'
            utils.overwrite_h5_key(h5, save_name, final_save_inds)
"""
####################################################################################################
MAKE A FINAL SUBSET OF NUMPY ARRAYS 
####################################################################################################
"""

def foo_save(name_in, data):
    tmp1 = os.path.dirname(name_in)
    Path(tmp1).mkdir(parents=True, exist_ok=True)
    np.save(name_in, data)
bd = r'Q:\SAMSONS_DATA\\'
tmp_key = '80_border_test_set_20%_data'
utils.print_h5_keys(sess_list[0], 1, 0)
selected_keys = utils.lister_it(utils.print_h5_keys(sess_list[0], 1, 0), '80_border')

for tmp_key in selected_keys:
    tvt_name = tmp_key.split('_set_')[0].split('_')[-1]
    save_dir = bd + tmp_key.split('border')[0]+'border' + os.sep
    for h5 in tqdm(sess_list):
        add_name = os.path.basename(h5).split('_final_combined.h5')[0] + '_'
        with h5py.File(h5, 'r') as h:
            inds = h[tmp_key][:]

    #         print(sum(inds))
            final_2105 = h['final_features_2105'][inds, :]
            labels = h['contacts_samson_curated_for_transfer_learning_220707'][inds]
            assert final_2105.shape[0] == len(labels), 'labels and features dont match'
            name_in = save_dir+'/'+tvt_name + '/'+add_name
            foo_save(name_in+'final_2105', final_2105)
            foo_save(name_in+'labels', labels)


"""
####################################################################################################
LOAD THE DATA FOR MODELING 
####################################################################################################
"""

bd = r'Q:\SAMSONS_DATA\40_border\\'
tvt_x = [[],[],[]]
tvt_y = [[],[],[]]
for ii, k in enumerate(['train', 'val', 'test']):
    bd2 = bd+k
    final_2105 = utils.sort(utils.get_files(bd2, '*final_2105.npy'))
    labels = utils.sort(utils.get_files(bd2, '*labels.npy'))
    for i, (f1, f2) in enumerate(zip(final_2105, labels)):
        assert os.path.basename(f1)[:-15]==os.path.basename(f2)[:-11], 'files do not match'
        tvt_x[ii].append(np.load(f1, allow_pickle=True))
        tvt_y[ii].append(np.load(f2, allow_pickle=True))
    tvt_x[ii] = np.concatenate(tvt_x[ii])
    tvt_y[ii] = np.concatenate(tvt_y[ii])



"""
####################################################################################################
MAKE INDS FOR FULL TRIALS 
####################################################################################################
"""

bd = '/Volumes/GoogleDrive-114825029448473821206/.shortcut-targets-by-id/1pUteMEgx37rAyqujJWxVN9-ywFAqaxhF/WhACC_PROCESSING_FOLDER/'
files = utils.lister_it(utils.get_files(bd, '*final_combined.h5'), remove_string='processing_')

for h5 in tqdm(files):
    test_inds = image_tools.get_h5_key_and_concatenate(h5, '80_border_test_set_20%_data')
    frame_nums = image_tools.get_h5_key_and_concatenate(h5, 'frame_nums')
    full_trial_test_inds = np.zeros_like(test_inds)
    for k1, k2 in utils.loop_segments(frame_nums):
        if np.any(test_inds[k1:k2]):
            full_trial_test_inds[k1:k2] = 1
    utils.overwrite_h5_key(h5, 'full_trial_test_inds', full_trial_test_inds)




"""

"""

def track(self, video_file, match_method='cv2.TM_CCOEFF'):
        """this function scans a template image across each frame of the video to identify the pole location.
        This assumes there is a pole at each frame. Cropping optimizes scanning by ~80% and uses the first frame
        as a point of reference.

        Parameters
        ----------
        video_file :

        match_method :
             (Default value = 'cv2.TM_CCOEFF')

        Returns
        -------

        """

        # width and height of img_stacks will be that of template (61x61)
        w, h = self.template_image.shape[::-1]
        max_match_val = []
        # open video at directory
        video = cv2.VideoCapture(video_file)
        if (video.isOpened() == False):
            print('error opening video file')
        frame_numbers = int(video.get(7))

        img_list = []
        loc_list = []
        # video.set(cv2.cv2.CAP_PROP_POS_FRAMES, 0)
        # success, og_frame = video.read()
        method = eval(match_method)
        crop_top_left = 0
        pole_center = 0
        for fn in range(frame_numbers):
            # iterate to next frame and crop using current details
            video.set(cv2.cv2.CAP_PROP_POS_FRAMES, fn)
            success, og_frame = video.read()

            # preprocess image
            if 'frame' in locals() and self.use_narrow_search_to_speed_up:
                frame, crop_top_left, crop_bottom_right = self.crop_image_from_top_left(og_frame,
                                                                                        crop_top_left2,
                                                                                        [w, h],
                                                                                        3)
            else:
                frame = og_frame
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype('uint8').copy()

            # Apply template Matching
            res = cv2.matchTemplate(img, self.template_image, method)
            min_val, max_val, min_loc, top_left = cv2.minMaxLoc(res)
            max_match_val.append(max_val)
            top_left = np.flip(np.asarray(top_left))

            # crop image and store
            crop_img, crop_top_left2, crop_bottom_right2 = self.crop_image_from_top_left(og_frame,
                                                                                         top_left + crop_top_left,
                                                                                         [w, h])
            img_list.append(crop_img)
            loc_list.append(np.flip(crop_top_left2))



        img_stack = np.array(img_list, dtype=np.uint8)
        loc_stack = np.array(loc_list)
        return img_stack, loc_stack, max_match_val


def crop_image_from_top_left(im, crop_top_left, size_crop, inflation=1):
        """This is an accessory function to track to improve tracking speed. This crops the initial large image into a smaller one, based on the inflation rate.
        Inflation rate of 3 = 3 x 3 template image size around the first guessed pole location.

        Parameters
        ----------
        im :

        crop_top_left :

        size_crop :

        inflation :
             (Default value = 3)

        Returns
        -------

        """
        inflation_shift = np.floor((np.asarray(size_crop) * (inflation - 1)) / 2).astype(int)

        size_crop = np.asarray(size_crop) * inflation
        imshape = np.asarray(im.shape[:2])

        # adjust for inflation and make copies of origianl crop inds
        crop_top_left = crop_top_left - inflation_shift
        crop_top_left2 = crop_top_left.copy()
        crop_bottom_right = crop_top_left + np.asarray(size_crop)
        crop_bottom_right2 = crop_bottom_right.copy()

        # adjust crop in case of out of bounds
        crop_top_left[crop_top_left < 0] = 0
        crop_bottom_right[crop_bottom_right > imshape] = np.asarray(imshape)[crop_bottom_right > imshape]

        # for placing cropped image in random noise image tensor (we do this in case of out of bounds issues all outputs are the same size)
        TL_adj = crop_top_left - crop_top_left2

        c_cropped = im[crop_top_left[0]:crop_bottom_right[0], crop_top_left[1]:crop_bottom_right[1], ...].astype(
            'uint8')

        # make random noise image tensor
        crop_dim = list(c_cropped.shape)
        crop_dim[:2] = size_crop.tolist()
        cropped_image = np.random.randint(256, size=crop_dim).astype('uint8')

        if len(crop_dim) > 2:  # crop 3D or more
            cropped_image[TL_adj[0]:TL_adj[0] + c_cropped.shape[0], TL_adj[1]:TL_adj[1] + c_cropped.shape[1],
            ...] = c_cropped
        else:  # crop 2D
            cropped_image[TL_adj[0]:TL_adj[0] + c_cropped.shape[0],
            TL_adj[1]:TL_adj[1] + c_cropped.shape[1]] = c_cropped

        return cropped_image, crop_top_left2, crop_bottom_right2

import cv2
from whacc.utils import h5_key_exists
def del_h5_key(h5_in, key_in):
    if h5_key_exists(h5_in, key_in):
        with h5py.File(h5_in, 'r+') as h:
            del h[key_in]
utils.del_h5_key = del_h5_key


mp4_bd = '/Users/phil/Desktop/samsons_eval/'
h5 = '/Users/phil/Desktop/samsons_eval/AH1179X24052021x4_final_to_combine_1_to_5_of_310.h5'
def insert_images_into_feature_data_h5(h5, mp4_bd, image_key = 'images'):
    frame_nums = image_tools.get_h5_key_and_concatenate(h5, 'frame_nums')
    # max_val_stack = image_tools.get_h5_key_and_concatenate(h5, 'max_val_stack')
    locations_x_y = image_tools.get_h5_key_and_concatenate(h5, 'locations_x_y')
    template_img = image_tools.get_h5_key_and_concatenate(h5, 'template_img')
    img_size = list(template_img.shape[:2])
    mp4_list = [mp4_bd+os.sep+os.path.basename(k.decode("ascii", "ignore")) for k in image_tools.get_h5_key_and_concatenate(h5, 'full_file_names')]

    h5_creator = image_tools.h5_iterative_creator(h5,
                                                 overwrite_if_file_exists=False,
                                                 max_img_height=img_size[0],
                                                 max_img_width=img_size[1],
                                                 close_and_open_on_each_iteration=True,
                                                 color_channel=True,
                                                 add_to_existing_H5=True,
                                                 ignore_image_range_warning=False,
                                                 dtype_img=h5py.h5t.STD_U8BE,
                                                 dtype_labels=h5py.h5t.STD_I32LE,
                                                 image_key_name = image_key,
                                                 label_key_name = 'TRASH')

    utils.del_h5_key(h5, h5_creator.img_key)
    utils.del_h5_key(h5, h5_creator.label_key_name)
    utils.del_h5_key(h5, 'multiplier')

    for i, (k1, k2) in enumerate(tqdm(utils.loop_segments(frame_nums), total=len(frame_nums))):
        video_file = mp4_list[i]
        video = cv2.VideoCapture(video_file)
        tmp_location = locations_x_y[k1:k2]
        if (video.isOpened() == False):
            print('error opening video file')
        frame_numbers = int(video.get(7))
        images = []
        for fn in range(frame_numbers):
            video.set(cv2.cv2.CAP_PROP_POS_FRAMES, fn)
            success, og_frame = video.read()
            locations = tmp_location[fn]
            crop_img, crop_top_left2, crop_bottom_right2 = crop_image_from_top_left(og_frame, [locations[1], locations[0]], img_size)
            images.append(crop_img)
        images = np.asarray(images)
        h5_creator.add_to_h5(images, -1*np.ones(images.shape[0]))

mp4_bd = '/Users/phil/Desktop/samsons_eval/'
h5 = '/Users/phil/Desktop/samsons_eval/AH1179X24052021x4_final_to_combine_1_to_5_of_310.h5'
utils.insert_images_into_feature_data_h5(h5, mp4_bd, image_key = 'images')


mod = utils.load_obj('/Users/phil/Downloads/model_save.pkl') # replace with the model file full path
utils.foo_predict(mod, '/Users/phil/Desktop/samsons_eval/')


from whacc import image_tools, utils
from whacc.touch_curation_GUI import touch_gui
h5 = '/Users/phil/Desktop/samsons_eval/AH1179X24052021x4_final_to_combine_1_to_5_of_310.h5'
temp_yhat = image_tools.get_h5_key_and_concatenate(h5, 'temp_yhat')
temp_labels_smoothed = 1*(utils.smooth(temp_yhat, 5)>0.5)
utils.overwrite_h5_key(h5, 'temp_labels_smoothed', temp_labels_smoothed)
touch_gui(h5, 'temp_yhat', label_write_key=None)






maxshape = list(images.shape)
maxshape[0] = None
maxshape

hf_file.create_dataset('images',
                        np.shape(images),
                        h5py.h5t.STD_U8BE,
                        # jk need this to not explode the size of the data... commented this out because I wanted to use not 0-255 numbers
                        maxshape=maxshape,
                        chunks=True,
                        data=images)




    video.set(cv2.cv2.CAP_PROP_POS_FRAMES, 1000)
    success, og_frame = video.read()
    plt.figure()
    plt.imshow(og_frame)

    tmp1 = locations_x_y[i*3000+1000]

    plt.plot(tmp1[0], tmp1[1], '+')

    crop_img, crop_top_left2, crop_bottom_right2 = crop_image_from_top_left(og_frame, [tmp1[1], tmp1[0]], [71,71])

    asdfasdf








for fn in range(frame_numbers):
    video.set(cv2.cv2.CAP_PROP_POS_FRAMES, fn)
    success, og_frame = video.read()


    crop_img, crop_top_left2, crop_bottom_right2 = self.crop_image_from_top_left(og_frame,
                                                                             top_left + crop_top_left,
                                                                             [w, h])


crop_img, crop_top_left2, crop_bottom_right2 = crop_image_from_top_left(og_frame, locations_x_y[0]-30, [71,71])

plt.imshow(crop_img)
plt.imshow(og_frame)
locations_x_y[0]

np.unique(locations_x_y, axis=0)



h5_dir= '\WhACC_PROCESSING_FOLDER\\' # replace this with a directory to any of the h5 files
##############################
utils.auto_combine_final_h5s(h5_dir, delete_extra_files=True)
##############################
mod = utils.load_obj(r'X:\PHILLIP\Samsons_models\model_saves_2\model_save.pkl') # replace with the model file full path
h5_files = utils.get_files(h5_dir, '*final_combined.h5') # list of your completed H5 data files
label_key = 'samsons_next_top_model' # key to find your raw predictions later
for h5 in h5_files:
    if not utils.h5_key_exists(h5, label_key) # if the key exists, skip it
        fd = image_tools.get_h5_key_and_concatenate(h5, 'final_features_2105') # get the x feature data
        yhat = mod.predict(fd) # predictions
        utils.overwrite_h5_key(h5, label_key, yhat) # write to H5 file with new name
