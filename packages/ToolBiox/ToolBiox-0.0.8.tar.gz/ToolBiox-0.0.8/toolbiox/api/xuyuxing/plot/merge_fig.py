# coding:utf-8

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
import pylab
import matplotlib.patches as patches
import matplotlib.cbook as cbook
import Image
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from pylab import *
import Image

img=Image.open('Cluster_0.U.seq.pdf')

with open('Cluster_0.U.seq.pdf', 'rb') as image_file:
    image = plt.imread(image_file)


fig, ax = plt.subplots()
im = ax.imshow(image)
patch = patches.Circle((260, 200), radius=200, transform=ax.transData)
im.set_clip_path(patch)

ax.axis('off')
plt.show()
