import os

from whacc import utils, image_tools
import numpy as np
from tqdm.autonotebook import tqdm

bd_2105 = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/FEATURE_DATA/colab_data2/model_testing/all_data/all_models_2105/regular_80_border/data/3lag/'
tmp1 = utils.get_h5s(bd_2105)
train_1_2105 = tmp1[0]
val_1_2105 = tmp1[1]

bd_labels = '/Volumes/GoogleDrive-114825029448473821206/My Drive/colab_data2/model_testing/all_data/all_models/regular_80_border/data/ALT_LABELS/'
tmp1 = utils.get_h5s(bd_labels)
train_1_labels = tmp1[0]
val_1_labels = tmp1[1]

bd_full_h5 = '/Volumes/GoogleDrive-114825029448473821206/My Drive/colab_data2/model_testing/all_data/all_models/regular_80_border/data/3lag/'
tmp1 = utils.get_h5s(bd_full_h5)
train_1_fn = tmp1[0]
val_1_fn = tmp1[1]

data_dict = dict()
data_dict['train_1'] = dict()#{'data', 'frame_nums', 'labels'}
data_dict['val_1'] = dict()#{'data', 'frame_nums', 'labels'}
data_dict['test_2'] = dict()#{'data', 'frame_nums', 'labels'}


data_dict['train_1']['data'] = image_tools.get_h5_key_and_concatenate(train_1_2105, 'final_features_2105')
data_dict['val_1']['data'] = image_tools.get_h5_key_and_concatenate(val_1_2105, 'final_features_2105')

data_dict['train_1']['labels'] = image_tools.get_h5_key_and_concatenate(train_1_labels, '[0, 1]- (no touch, touch)')
data_dict['val_1']['labels'] = image_tools.get_h5_key_and_concatenate(val_1_labels, '[0, 1]- (no touch, touch)')

data_dict['train_1']['frame_nums'] = image_tools.get_h5_key_and_concatenate(train_1_fn, 'frame_nums')
data_dict['val_1']['frame_nums'] = image_tools.get_h5_key_and_concatenate(val_1_fn, 'frame_nums')


tmp1 = [data_dict['train_1']['data'].shape[0], data_dict['train_1']['labels'].shape[0], np.sum(data_dict['train_1']['frame_nums'])]
assert np.all(tmp1[0]==np.asarray(tmp1)), 'dataset doesnt match labels and/or frame nums'

tmp1 = [data_dict['val_1']['data'].shape[0], data_dict['val_1']['labels'].shape[0], np.sum(data_dict['val_1']['frame_nums'])]
assert np.all(tmp1[0]==np.asarray(tmp1)), 'dataset doesnt match labels and/or frame nums'

"""
LOAD DATA 
"""
# bd_fn = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/frame_nums_for_cnn_comparison'
# bd_data = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/final_2105_for_cnn_comparison'
# bd_labels = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/labels_for_cnn_comparison'

replace_data = r'final_2105_for_cnn_comparison'
replace_labels = r'labels_for_cnn_comparison'
replace_frame_nums = r'frame_nums_for_cnn_comparison'

bd = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/'
bd_data = bd + replace_data

data_files = utils.sort(utils.get_files(bd_data, '*.npy'))

tvt_x = [[],[],[]]
tvt_y = [[],[],[]]
tvt_fn = [[],[],[]]

for set_i, set_type in enumerate(['test_']):
    data_files_set = utils.sort(utils.lister_it(data_files, set_type))
    for f_data in tqdm(data_files_set):
        f_label = f_data.replace(replace_data, replace_labels)
        f_fn = f_data.replace(replace_data, replace_frame_nums)

        tvt_x[set_i].append(np.load(f_data, allow_pickle=True))
        tvt_y[set_i].append(np.load(f_label, allow_pickle=True))
        tvt_fn[set_i].append(np.load(f_fn, allow_pickle=True))

    data_dict['test_2']['data'] = np.concatenate(tvt_x[set_i])
    data_dict['test_2']['labels'] = np.concatenate(tvt_y[set_i])
    data_dict['test_2']['frame_nums'] = np.concatenate(tvt_fn[set_i])
del tvt_x, tvt_y, tvt_fn

tmp1 = [data_dict['test_2']['data'].shape[0], data_dict['test_2']['labels'].shape[0], np.sum(data_dict['test_2']['frame_nums'])]
assert np.all(tmp1[0]==np.asarray(tmp1)), 'dataset doesnt match labels and/or frame nums'


bd = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/'
utils.save_obj(data_dict, bd + os.sep + 'T1V1t2_data_dict')



tmp_dict = utils.load_obj(bd+os.sep+'T1V1t2_data_dict.pkl')

tvt_x = [[],[],[]]
tvt_y = [[],[],[]]
tvt_fn = [[],[],[]]

tvt_x[0] = tmp_dict['train_1']['data']
tvt_x[1] = tmp_dict['val1']['data']
tvt_x[2] = tmp_dict['test_2']['data']

tvt_y[0] = tmp_dict['train_1']['frame_nums']
tvt_y[1] = tmp_dict['val1']['frame_nums']
tvt_y[2] = tmp_dict['test_2']['frame_nums']

tvt_fn[0] = tmp_dict['train_1']['labels']
tvt_fn[1] = tmp_dict['val1']['labels']
tvt_fn[2] = tmp_dict['test_2']['labels']

del tmp_dict

