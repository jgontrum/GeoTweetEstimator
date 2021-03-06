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
Loads the Tweets from a corpus and draws them on a map.

Usage:
python DrawTweetLocation.py ClusterData.pickle OutputGraphic.png
                                 ^                   ^
                        A list of centroid      The graphic that
                        positions, created by   will be created.
                        pickleClusters().
"""

if len(sys.argv) < 3 :
    print "Specify to the cluster data and the output path for the graph"

clusters = pickle.load(open(sys.argv[1], 'rb')) # list of (lon, lat)

# Make connection
database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="All")

# Prepare map
basemap = MapFunctions.prepareMap()

# Add more colors, if you have > 12 clusters!
colors =  ['firebrick', 'green', 'navy', 'yellow', 'slategray', 'plum',
           'mediumorchid', 'lightskyblue', 'coral', 'lavender', 'gold', 'lime']

# Iterate over all tweets and split the tokenised texts.
# Each token maps to a list of lon, lat tuples
for lon, lat, tweet in database.getRows("`long`, `lat`, `tokenised_low`"):
    if tweet.count("schrippe") > 0:
        #cluster = EvaluationFunctions.getCluster(lon, lat, clusters)
        #col = colors[cluster]
        col = 'lightskyblue'
        basemap.plot(lon, lat, '.', color = col, markeredgecolor=col, markersize=1, latlon=True)

for lon, lat, tweet in database.getRows("`long`, `lat`, `tokenised_low`"):
    if tweet.count("wecke") > 0:
        #cluster = EvaluationFunctions.getCluster(lon, lat, clusters)
        #col = colors[cluster]
        col = 'red'
        basemap.plot(lon, lat, '.', color = col, markeredgecolor=col, markersize=1, latlon=True)

"""
# Draw the clusters
for i in range(len(clusters)):
    lon, lat = clusters[i]
    col = colors[i]
    basemap.plot(lon, lat, 'x', color = 'black',  markersize=5, latlon=True, markeredgewidth=2, markeredgecolor='w')
    x,y = basemap(lon, lat)
    plt.text(x,y, str(i))
"""
plt.savefig(sys.argv[2], format='png', bbox_inches='tight', dpi=900)
