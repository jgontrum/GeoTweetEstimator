#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import cPickle as pickle
from Wrapper import MapFunctions
import matplotlib.pyplot as plt
#from scipy.stats import multivariate_normal
import numpy as np
#functions = pickle.load(open("functions.pickle", "rb"))

# Prepare map
basemap = MapFunctions.prepareMap()

# Plot functions
x = []
y = []
z = []
for lat in np.linspace(45,56,0,endpoint=False):
	for lng in  np.linspace(5,18,0,endpoint=False):
		x.append(lng)
		y.append(lat)
		z.append(functions[0].pdf([lng, lat]))
		#basemap.plot(lng, lat, '.', color = 'red', markeredgecolor='red', markersize=5, latlon=True)


plt.show()	
#plt.savefig("/tmp/1.png", format='png', bbox_inches='tight', dpi=100)
