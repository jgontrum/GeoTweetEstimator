#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

from Wrapper import MySQLConnection
import cPickle as pickle
import sys
from Wrapper import MapFunctions
import matplotlib.pyplot as plt
from Evaluation import EvaluationFunctions
import os

"""
Draws the coordinates of tweets on a map.
Demonstrates how the wrappers can be used.
"""

if len(sys.argv) < 3 :
    print "Specify to the cluster data and the output path for the graph"

clusters = pickle.load(open(sys.argv[1], 'rb')) # list of (lon, lat)

# Make connection
database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TRAIN")

# Prepare map
basemap = MapFunctions.prepareMap()

colors =  ['firebrick', 'green', 'navy', 'yellow', 'slategray', 'plum',
           'mediumorchid', 'lightskyblue', 'coral', 'lavender', 'gold', 'lime']

# Iterate over all tweets and split the tokenised texts.
# Each token maps to a list of lon, lat tuples
for lon, lat in database.getRows("`long`, `lat`"): 
    cluster = EvaluationFunctions.getCluster(lon, lat, clusters)
    col = colors[cluster]
    basemap.plot(lon, lat, '.', color = col, markeredgecolor=col, markersize=1, latlon=True)

for i in range(len(clusters)):
    lon, lat = clusters[i]
    col = colors[i]
    basemap.plot(lon, lat, 'x', color = 'black', markeredgecolor='black', markersize=5, latlon=True)



plt.savefig(sys.argv[2], format='png', bbox_inches='tight', dpi=900)
