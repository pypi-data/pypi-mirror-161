
from whacc import model_maker

from whacc.model_maker import *


import h5py

from tensorflow.keras.layers import Dense, LSTM, Flatten, TimeDistributed, Conv2D, Dropout, GRU

from tensorflow.keras.utils import plot_model
from tensorflow.keras.models import Model
from tensorflow.keras import Sequential
from tensorflow import keras
from tensorflow.keras import applications

import tensorflow as tf
from tqdm.notebook import tqdm
from tqdm import tqdm
import pickle
from whacc import utils, image_tools, transfer_learning, analysis
import matplotlib.pyplot as plt

from sklearn.utils import class_weight
import os
import copy
import numpy as np

from pathlib import Path
import shutil
import zipfile
from datetime import datetime
import pytz
import json
from math import isclose, sqrt
from IPython import display

"""# define some funcitons"""
def image_transform(raw_X):
  IMG_SIZE = 96
  if len(raw_X.shape) == 4 and raw_X.shape[3] == 3:
      rgb_batch = copy.deepcopy(raw_X)
  else:
      rgb_batch = np.repeat(raw_X[..., np.newaxis], 3, -1)
  rgb_tensor = tf.cast(rgb_batch, tf.float32)  # convert to tf tensor with float32 dtypes
  rgb_tensor = (rgb_tensor / 127.5) - 1  # /127.5 = 0:2, -1 = -1:1 requirement for mobilenetV2
  rgb_tensor = tf.image.resize(rgb_tensor, (IMG_SIZE, IMG_SIZE))  # resizing
  # IMG_SHAPE = (IMG_SIZE, IMG_SIZE, 3)
  return rgb_tensor

def inds_sorted_data(a, key_name, max_or_min):#keep
    """
  a is the data form all_data looped through
  """
    log_ind = np.where(key_name == a['logs_names'])[0][0]
    val_list = a['all_logs'][:, log_ind]
    if max_or_min == 'max':
        max_arg_sort = np.flip(np.argsort(val_list)) + 1
    elif max_or_min == 'min':
        max_arg_sort = np.argsort(val_list) + 1
    else:
        raise ValueError("""max_or_min must be a string set to 'max' or 'min'""")
    return max_arg_sort


def sorted_loadable_epochs(a, key_name, max_or_min):#keep
    """
  a is the data form all_data looped through
  """
    arg_sort_inds = inds_sorted_data(data, key_name, max_or_min)
    arg_sort_inds[np.argmax(arg_sort_inds)] = -1
    saved_epoch_numbers = np.asarray(list(data['info']['epoch_dict'].keys()))
    sorted_loadable_epochs_out = []
    for k in arg_sort_inds:
        if k in saved_epoch_numbers:
            sorted_loadable_epochs_out.append(k)
    return sorted_loadable_epochs_out


def get_automated_model_info_TL(BASE_H5, image_source_h5_directory_ending, test_data_dir, data_string_key="data"):#keep
    tz = pytz.timezone('America/Los_Angeles')
    loc_dt = pytz.utc.localize(datetime.utcnow())
    LA_TIME = loc_dt.astimezone(tz)
    todays_version = LA_TIME.strftime("%Y_%m_%d_%H_%M_%S")
    del tz
    del loc_dt
    del LA_TIME
    a = os.sep
    base_data_dir = BASE_H5 + a + data_string_key + a
    base_dir_all_h5s = BASE_H5 + a + data_string_key + a + 'single_frame' + a
    data_dir = base_data_dir + image_source_h5_directory_ending
    print('\nFOR IMAGES, 0 is train set, 1 is val set')
    print(data_dir)
    image_h5_list = utils.get_h5s(data_dir)
    # pdb.set_trace()
    h5_train = image_h5_list[0]
    h5_val = image_h5_list[1]
    # labels_dir = base_data_dir + a + "ALT_LABELS" + a
    # print('\nFOR LABELS,0 is train set, 1 is val set')
    # label_h5_list = utils.get_h5s(labels_dir)
    # print('\nSelect from the following label structures...')
    # print(labels_dir)
    # label_key_name_list = utils.print_h5_keys(label_h5_list[0], return_list=True)
    # h5_test_labels = utils.get_h5s(test_data_dir + a + "ALT_LABELS" + a, print_h5_list=False)[0]
    # h5_test = utils.get_h5s(test_data_dir + a + image_source_h5_directory_ending + a, print_h5_list=False)[0]
    return locals()



def re_build_model_TL(model_name_str, class_numbers, base_learning_rate=0.00001,
                      dropout_val=None, IMG_SIZE=96, labels=None, reload_weights_file=None, num_layers_unfreeze=0):#keep
    num_classes = len(class_numbers)
    IMG_SHAPE = (IMG_SIZE, IMG_SIZE, 3)
    model_function = eval('applications.' + model_name_str)
    base_model = model_function(input_shape=IMG_SHAPE, weights='imagenet', include_top=False)
    # base_model.summary()
    num_layers_in_base_model = len(base_model.layers)
    base_model_layer_names = [k.name for k in base_model.layers]
    base_model.trainable = False  ##&%&$&$&%&%&$&%&$&$&%&%&$&&$&&%&%&$&&$&$&&&$##&%&$&$&%&%&$&%&$&$&%&%&$&&$&&%&%&$&&$&$&&&$##&%&$&$&%&%&$&%&$&$&%&%&$&&$&&%&%&$&&$&$&&&$##&%&$&$&%&%&$&%&$&$&%&%&$&&$&&%&%&$&&$&$&&&$##&%&$&$&%&%&$&%&$&$&%&%&$&&$&&%&%&$&&$&$&&&$
    len_base_model = len(base_model.layers)
    x = base_model.output
    x = keras.layers.GlobalAveragePooling2D()(x)  # global spatial average pooling layer
    x = Dense(2048, activation='relu')(x)  # fully-connected layer
    if dropout_val is not None:
        x = Dropout(dropout_val)(x)
    ###### i need to name the layers
    if num_classes == 2:
        predictions = Dense(1, activation='sigmoid')(x)  # fully connected output/classification layer
    else:
        predictions = Dense(num_classes, activation='softmax')(x)  # fully connected output/classification layer
    model = Model(inputs=base_model.input, outputs=predictions)

    if num_classes == 2:

        optimizer = keras.optimizers.RMSprop(learning_rate=base_learning_rate)
        loss = keras.losses.BinaryCrossentropy()
        metrics = [keras.metrics.BinaryAccuracy(name="bool_acc", threshold=0.5),
                   keras.metrics.AUC(name='auc')]
    else:
        optimizer = keras.optimizers.Adam(learning_rate=base_learning_rate)
        loss = keras.losses.SparseCategoricalCrossentropy()
        metrics = [keras.metrics.SparseCategoricalAccuracy(name='acc')]
    if reload_weights_file is not None:
        model.load_weights(reload_weights_file)  # load model weights

    # for i, k in enumerate(model.layers):
    #   if i >= len_base_model-5:
    #     k.trainable = True
    #   else:
    #     k.trainable = False
    relu_layers = []
    for i, k in enumerate(model.layers):
        if 'relu' in k.name.lower():
            relu_layers.append(i)
    relu_layers.append(9999999)
    # relu_layers = np.flip(np.asarray(relu_layers)+1)
    relu_layers = np.flip(np.asarray(relu_layers))

    # num_layers_unfreeze =1          #0 means freeze entire model 1 means base model forzen 2 one more (group)laye runfrozen etc
    for i, k in enumerate(model.layers):
        if i >= relu_layers[
            num_layers_unfreeze] and 'batchnorm' not in k.name.lower():  # LK:J:LKJD:LKJD:LKDJ:LDKJ:DLKJD:LKJD:LKJD:LKJD:LKDJ:LKDJLK:DJ
            k.trainable = True
        else:
            k.trainable = False

    model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
    model.num_layers_in_base_model = num_layers_in_base_model
    model.base_model_layer_names = base_model_layer_names
    if labels is not None:
        rebalance = class_weight.compute_class_weight('balanced', classes=class_numbers, y=labels.flatten())
        class_weights = {i: rebalance[i] for i in class_numbers}
        wrap_vars_list = ['class_numbers',
                          'num_classes',
                          'base_learning_rate',
                          'model_name_str',
                          'IMG_SIZE',
                          'dropout_val']
        return model, class_weights
    else:
        return model


def add_lstm_to_model(model_in, num_layers_in_base_model, base_learning_rate=10 ** -5, lstm_len=7):#keep
    # model_in.base_model_layer_names
    base_model = Model(model_in.input, model_in.layers[num_layers_in_base_model - 1].output)
    model_out = Sequential()
    model_out.add(TimeDistributed(base_model, input_shape=(lstm_len, 96, 96, 3)))
    model_out.add(TimeDistributed(Flatten()))
    model_out.add(LSTM(256, activation='relu', return_sequences=False))
    model_out.add(Dense(64, activation='relu'))
    # is 64 here the final number of features if so i want both of these to be bigger, check what I did for the OG models
    model_out.add(Dropout(.2))
    model_out.add(Dense(1, activation='sigmoid'))

    optimizer = keras.optimizers.RMSprop(learning_rate=base_learning_rate)
    loss = keras.losses.BinaryCrossentropy()
    metrics = [keras.metrics.BinaryAccuracy(name="bool_acc", threshold=0.5), keras.metrics.AUC(name='auc')]
    model_out.compile(optimizer=optimizer, loss=loss, metrics=metrics)
    return model_out


def rename_content_folder(instr):# keep
    if isinstance(instr, str) and '/content/' in instr:
        return '/Users/phil/Desktop/content' + instr.split('content')[-1]
    else:
        return instr

# these last 2 are used to change the directories easily when running on local
def foo_rename2(instr):#keep
    if isinstance(instr, str) and '/My Drive/' in instr:
        return '/Volumes/GoogleDrive-114825029448473821206/My Drive' + instr.split('My Drive')[-1]
    else:
        return instr


def make_D_local(D):#keep
    for key in D:
        if isinstance(D[key], str):
            D[key] = foo_rename2(D[key])
    for key in D['epoch_dict']:
        if isinstance(D['epoch_dict'][key], str):
            D['epoch_dict'][key] = foo_rename2(D['epoch_dict'][key])
    return D

"""# Load all_data for reload models and settings """

def save_obj(obj, name):#keep
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):#keep
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

def foo_rename(instr):#keep
    if isinstance(instr, list):
        for i, k in enumerate(instr):
            instr[i] = foo_rename(k)
        return instr
    else:
        return '/Volumes/GoogleDrive-114825029448473821206/My Drive' + instr.split('My Drive')[-1]

all_data = utils.load_obj(foo_rename('/content/gdrive/My Drive/colab_data2/all_data'))

h5_in = '/Users/phil/Desktop/pipeline_test/AH0407x160609_3lag.h5'
key_name = 'acc_test'
max_or_min = 'max'

names = [os.path.basename(data['full_name']) for data in all_data]
lag_names, lag_inds = utils.lister_it(names, keep_strings='3lag__regular', return_bool_index=True)
regular_names, regular_inds = utils.lister_it(names, keep_strings='regular__regular', remove_string='__EfficientNetB7__', return_bool_index=True)

all_inds = np.logical_or(regular_inds, lag_inds)
all_inds = np.where(all_inds)[0]
# all_names = regular_names+lag_names

batch_size = 500
data_in = np.random.rand(100, 96, 96, 3)
final_save_dir = foo_rename('/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/final_CNN_predictions_16_count/')
utils.make_path(final_save_dir)

for model_ind in all_inds:
    data = all_data[model_ind]
    best_epochs = sorted_loadable_epochs(data, key_name, max_or_min)
    reload_model_epoch = best_epochs[0]
    D = copy.deepcopy(data['info'])

    epoch_model_file = D['epoch_dict'][reload_model_epoch]
    epoch_model_file = foo_rename(epoch_model_file)

    model = re_build_model_TL(D['model_name_str'],
                              D['class_numbers'],
                              base_learning_rate=0,
                              dropout_val=0,
                              IMG_SIZE=D['IMG_SIZE'],
                              reload_weights_file=epoch_model_file,
                              num_layers_unfreeze=0)

    i1 = 0
    i2 = 0
    cnn_predictions = []
    for k in tqdm(range(int(np.ceil(data_in.shape[0]/batch_size)))):
        i2 += batch_size ##############################
        x_temp = image_transform(data_in[i1:i2])
        cnn_predictions.append(model.predict(x_temp))
        i1 += batch_size ##############################
    cnn_predictions = np.concatenate(cnn_predictions)
    utils.save_obj(cnn_predictions, final_save_dir+os.path.basename(data['full_name']))
