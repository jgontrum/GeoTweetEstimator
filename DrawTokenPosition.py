#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
from Wrapper import MapFunctions
import matplotlib.pyplot as plt
import cPickle as pickle

"""
Loads pickled token data and prints them on a map.
The data is created in with DataFunctions.pickleTrainingCorpus() and maps all tokens in the training corpus
to a calculated position (e.g. median or mean).

Usage:
python PrepareData.py TokenData.pickle OutputGraphic.png    [0.5             2]
                              ^               ^               ^              ^
                          Data from   Save the graphic   Percentage of       Token must occur
             pickleTrainingCorpus()                      words to ignore     at least two times.
                                                         based on the
                                                         variance.
"""

if len(sys.argv) < 3 :
    print "Specify the path for the corpus and the output path for the graph"

token_to_data = pickle.load(open(sys.argv[1], 'rb')) #< ((lon, lat), variance, count)
basemap = MapFunctions.prepareMap() # print the positions here
coordinates_to_draw = [] # Coordinates that will be drawn to the map

# Define constants
COUNT_THRESHOLD = 1
VARIANCE_THRESHOLD = 1

# Provide values as arguments
if len(sys.argv) > 2:
    # Sort by variance in the token data
    token_to_data_sorted = sorted(token_to_data.iteritems(), key=lambda x: x[1][1])
    COUNT_THRESHOLD = sys.argv[4]
    VARIANCE_THRESHOLD = int(len(token_to_data_sorted) * float(sys.argv[3]))

# Collect data
for token, ((lon, lat), variance, count) in token_to_data.iteritems():
    if count < COUNT_THRESHOLD and variance < VARIANCE_THRESHOLD:
        coordinates_to_draw.append((lon, lat))

# Draw coordinates to the map:
for lon, lat in coordinates_to_draw:
    basemap.plot(lon, lat, '.r', markeredgecolor='r', markersize=1,latlon=True)

plt.savefig(sys.argv[2], format='png', bbox_inches='tight', dpi=900)
