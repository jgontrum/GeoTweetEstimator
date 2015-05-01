#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
from Wrapper import MapFunctions
import matplotlib.pyplot as plt
import numpy as np
import cPickle as pickle


""" DEFINE CONSTANTS """
# There must be at least that many occurrences of a token
COUNT_THRESHOLD = 1
VARIANCE_THRESHOLD = 2  #float('inf')
""" ---------------- """

if len(sys.argv) < 3 :
    print "Specify the path for the corpus and the output path for the graph"

token_to_data = pickle.load(open(sys.argv[1], 'rb')) #< ((lon, lat), variance, count)

# Prepare map
basemap = MapFunctions.prepareMap()

coordinates_to_draw = [] # Coordinates that will be drawn to the map

for (lon, lat), variance, count in token_to_data.itervalues():
    if variance < float(sys.argv[3]):
        coordinates_to_draw.append((lon, lat))

# Draw coordinates to the map:
for lon, lat in coordinates_to_draw:
    basemap.plot(lon, lat, '.r', markeredgecolor='r', markersize=1,latlon=True)

plt.savefig(sys.argv[2], format='png', bbox_inches='tight', dpi=900)
