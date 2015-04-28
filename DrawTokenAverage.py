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

token_to_data = pickle.load(open(sys.arv[1], 'rb')) #< ((lon, lat), variance, count)

# Prepare map
basemap = MapFunctions.prepareMap()

# Iterate over all tweets and split the tokenised texts.
# Each token maps to a list of lon, lat tuples
token_distribution = {}
for tokens, values in token_to_data.iteritems():
    (lon, lat), variance, count = values
    for token in tokens.split():
        token_distribution.setdefault(token, []).append((lon, lat))


# Calculate the variance for each token

# Factor for making degrees of longitude roughly equal degrees of latitude in variance calculation
longitude_factor = 0.636

coordinates_to_draw = [] # Coordinates that will be drawn to the map

for token, coordinates_of_tuple in token_distribution.iteritems():
    count = len(coordinates_of_tuple)
    if count > COUNT_THRESHOLD:
        # Convert coordinate list to numpy array
        np_list = np.asarray(coordinates_of_tuple, dtype=float)

        # Calculate the mean values for
        (mean_lon, mean_lat) = tuple(np.mean(np_list, axis=0))

        variance_num = 0
        for (point_lon, point_lat) in coordinates_of_tuple:
            variance_num += (point_lon - mean_lon)**2 + (longitude_factor*(point_lat - mean_lat))**2

        # Calculate the variance
        variance = variance_num / count
        if variance < VARIANCE_THRESHOLD:
            coordinates_to_draw.append((mean_lon,mean_lat))


# Draw coordinates to the map:
for lon, lat in coordinates_to_draw:
    basemap.plot(lon, lat, 'r,', latlon=True)

plt.savefig(sys.argv[2], format='png')
