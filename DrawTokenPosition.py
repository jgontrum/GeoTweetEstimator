#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
from Wrapper import MapFunctions
import matplotlib.pyplot as plt
import cPickle as pickle
from Wrapper import MySQLConnection
import os
from Evaluation import EvaluationFunctions

"""
Loads pickled token data and prints them on a map.
The data is created in with DataFunctions.pickleTrainingCorpus() and maps all tokens in the training corpus
to a calculated position (e.g. median or mean).

Usage:
python PrepareData.py  OutputGraphic.png    [0.5             2]
                              ^               ^              ^
                          Save the graphic   Percentage of       Token must occur
                              words to ignore     at least two times.
                                                         based on the
                                                         variance.
"""

if len(sys.argv) != 4 :
    print "Specify the path for the corpus and the output path for the graph"

# basemap = MapFunctions.prepareMap() # print the positions here
coordinates_to_draw = [] # Coordinates that will be drawn to the map

# Define constants

token_to_data = {}
token_db = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TOKENDATA")
variances_x = []
variances_y = []
variances_z = []

for tid, count, medx, medy, medz, varx, vary, varz in token_db.getTokenInfo(ids=None, columns="`id`, `count`, `median_x`, `median_y`, `median_z`, `variance_x`, `variance_y`, `variance_z`"):
    variances_x.append(varx)
    variances_y.append(vary)
    variances_z.append(varz)
    token_to_data[tid] = (medx, medy, medz, (varx, vary, varz), count)

variances_x = list(sorted(variances_x))
variances_y = list(sorted(variances_y))
variances_z = list(sorted(variances_z))
n = len(variances_x)

def getThreshold(t):
    pos = int(n * t)
    if t == 1:
        pos -= 1
    x = variances_x[pos]
    y = variances_y[pos]
    z = variances_z[pos]
    return (x,y,z)

def checkVarianceThreshold((x,y,z)):
        (tx,ty,tz) = VARIANCE_THRESHOLD
        return x < tx and y < ty and z < tz

""" EVALUATE """
# Sort by variance in the token data
for i in range (1,100):
    i += 1
    l = i / 100.0
    COUNT_THRESHOLD = 10
    VARIANCE_THRESHOLD = getThreshold(l)

    # Collect data
    for tid, (medx, medy, medz, vars, count) in token_to_data.iteritems():
        if count > COUNT_THRESHOLD and checkVarianceThreshold(vars):
            coordinates_to_draw.append(EvaluationFunctions.convertCartesianToLatLong(medx, medy, medz))

    pickle.dump(coordinates_to_draw, open(sys.argv[1] + "_" + str(l) + ".pickle", 'wb'))
#
# # Draw coordinates to the map:
# for lon, lat in coordinates_to_draw:
#     basemap.plot(lon, lat, '.r', markeredgecolor='r', markersize=1,latlon=True)
#
# plt.savefig(sys.argv[1], format='png', bbox_inches='tight', dpi=900)
