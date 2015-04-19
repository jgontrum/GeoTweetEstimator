#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import os
import sys
from Wrapper import MySQLConnection
from Wrapper import MapFunctions
import matplotlib.pyplot as plt
import numpy as np

""" DEFINE CONSTANTS """
# There must be at least that many occurrences of a token
COUNT_THRESHOLD = 2
VARIANCE_THRESHOLD = float('inf')
""" ---------------- """

if len(sys.argv) != 2:
    print "Specify the output path for the graph."


# Make connection
database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TRAIN")

# Prepare map
basemap = MapFunctions.prepareMap()

# Iterate over all tweets and split the tokenised texts.
# Each token maps to a list of lon, lat tuples
token_distribution = {}
for tokens, lat, lon in database.getRows("`tokenised`, `lat`, `long`"):
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
        (mean_lon, mean_lon) = tuple(np.mean(np_list, axis=0))

        variance_num = 0
        for (point_lon, point_lat) in coordinates_of_tuple:
            variance_num += (point_lon - mean_lon)**2 + (longitude_factor*(point_lat - mean_lon))**2

        # Calculate the variance
        variance = variance_num / count
        if variance < VARIANCE_THRESHOLD:
            coordinates_to_draw.append((mean_lon,mean_lon))


# Draw coordinates to the map:
for lon, lat in coordinates_to_draw:
    basemap.plot(lon, lat, 'r,', latlon=True)

plt.savefig(sys.argv[1], format='png')