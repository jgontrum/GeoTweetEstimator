#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import cPickle as pickle
import sys
from Wrapper import MapFunctions
import matplotlib.pyplot as plt
from Evaluation import EvaluationFunctions

"""
Draws the coordinates of tweets on a map.
Demonstrates how the wrappers can be used.
"""

if len(sys.argv) < 4 :
    print "Specify the path for the corpus, the cluster data and the output path for the graph"

token_to_data = pickle.load(open(sys.arv[1], 'rb')) #< ((lon, lat), variance, count)
clusters = pickle.load(open(sys.arv[2], 'rb')) # list of (lon, lat)

# Prepare map
basemap = MapFunctions.prepareMap()

colors =  ['firebrick', 'green', 'navy', 'yellow', 'slategray', 'plum',
           'mediumorchid', 'gold', 'coral', 'lavender', 'lightskyblue', 'lime']

# Iterate over all tweets and split the tokenised texts.
# Each token maps to a list of lon, lat tuples
token_distribution = {}
for tokens, values in token_to_data.iteritems():
    (lon, lat), variance, count = values

    cluster = EvaluationFunctions.getCluster(lon, lat, clusters)
    col = colors[cluster]

    basemap.plot(lon, lat, ',', color = col, latlon=True)

for i in range(len(clusters)):
    lon, lat = clusters[i]
    col = colors[i]
    basemap.plot(lon, lat, '.', color = col,  latlon=True)


plt.savefig(sys.arv[3], format='png')