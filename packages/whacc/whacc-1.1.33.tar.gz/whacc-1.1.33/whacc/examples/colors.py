import matplotlib.pyplot as plt
import numpy as np
from whacc import utils
from whacc.utils import info
#
# color=["#E69F00", "#56B4E9", "#009E73", "#0072B2", "#D55E00", "#CC79A7", "#F0E442"]
# for i, k in enumerate(color):
#     plt.plot([0, 1], [i, i], color = k)
#
#
# CB91_Blue = '#2CBDFE'
# CB91_Green = '#47DBCD'
# CB91_Pink = '#F3A0F2'
# CB91_Purple = '#9D2EC5'
# CB91_Violet = '#661D98'
# CB91_Amber = '#F5B14C'
#
# color_list = [CB91_Blue, CB91_Pink, CB91_Green, CB91_Amber,
#               CB91_Purple, CB91_Violet]
# plt.rcParams['axes.prop_cycle'] = plt.cycler(color=color_list)
#
# plt.figure()
# for i, k in enumerate(color_list):
#     plt.plot([0, 1], [i, i], k)
#
#
#
# CB91_Blue = '#2CBDFE'
# CB91_Green = '#47DBCD'
# CB91_Pink = '#F3A0F2'
# CB91_Purple = '#9D2EC5'
# CB91_Violet = '#661D98'
# CB91_Amber = '#F5B14C'
#
# color_list = [CB91_Blue, CB91_Pink, CB91_Green, CB91_Amber,
#               CB91_Purple, CB91_Violet]
# plt.rcParams['axes.prop_cycle'] = plt.cycler(color=color_list)
#

import seaborn as sns

sns.set(rc={
 'axes.axisbelow': False,
 'axes.edgecolor': 'lightgrey',
 'axes.facecolor': 'None',
 'axes.grid': False,
 'axes.labelcolor': 'dimgrey',
 'axes.spines.right': False,
 'axes.spines.top': False,
 'figure.facecolor': 'white',
 'lines.solid_capstyle': 'round',
 'patch.edgecolor': 'w',
 'patch.force_edgecolor': True,
 'text.color': 'dimgrey',
 'xtick.bottom': False,
 'xtick.color': 'dimgrey',
 'xtick.direction': 'out',
 'xtick.top': False,
 'ytick.color': 'dimgrey',
 'ytick.direction': 'out',
 'ytick.left': False,
 'ytick.right': False})
sns.set_context("notebook", rc={"font.size":16,
                                "axes.titlesize":20,
                                "axes.labelsize":18})

fig, ax = plt.subplots(1, figsize=(4, 4))
for i, i2 in enumerate([3,0,1,2]):
  # line = ax.bar(i, np.random.rand(1))
  line = ax.plot(i, np.random.rand(1))
  print(line.get_color())


for i, i2 in enumerate([3,0,1,2]):
    plt.plot([0, 1], [i, i])


col = {}

col['base_models'] = []
