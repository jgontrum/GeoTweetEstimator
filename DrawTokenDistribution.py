#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
from Wrapper import MapFunctions
import cPickle as pickle
from Wrapper import Signature
import os
from Wrapper import MySQLConnection
import numpy as np
from scipy.stats import multivariate_normal

"""
Loads pickled token data and prints them on a map.
The data is created in with DataFunctions.pickleTrainingCorpus() and maps all tokens in the training corpus
to a calculated position (e.g. median or mean).

Usage:
python PrepareData.py Signature.pickle OutputGraphic.png    [0.5             2]
                              ^               ^               ^              ^
                          Signature   Save the graphic   Percentage of       Token must occur
                                                         words to ignore     at least two times.
                                                         based on the
                                                         variance.
"""

if len(sys.argv) < 3 :
    print "Specify the path for the corpus and the output path for the graph"

signature = pickle.load(open(sys.argv[1], 'rb')) #< ((lon, lat), variance, count)

tokens = [("dresden",)]
ids = [signature.add(x) for x in tokens]

functions = []

token_db = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TOKENDATA")
for token_id, lon, lat, variance, count, \
    mean_lng, mean_lat, \
    covarA0, covarA1, \
    covarB0, covarB1 \
    in token_db.getTokenInfo(ids, columns= \
    "`id`, `long`, `lat`, `variance`, `count`, `mean_lng`, `mean_lat`, `covarA0`, `covarA1`, `covarB0`, `covarB1`"):
            covar_matrix = np.matrix([[covarA0, covarA1],[covarB0, covarB1]])
            mean = np.asarray([mean_lng, mean_lat])
            functions.append(multivariate_normal(mean=mean, cov=covar_matrix))


pickle.dump(functions, open("functions.pickle", "wb"))


# Plot functions
x = []
y = []
z = []
for lat in range(450, 560):
    for lng in range(50,180):
        lat = lat / 10.0
        lng = lng / 10.0
        x.append(lng)
        y.append(lat)
        z.append(functions[0].pdf([lng, lat]))

pickle.dump((x,y,z), open("draw.pickle", "wb"))
