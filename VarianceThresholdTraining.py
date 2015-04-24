#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import os
import sys
from Wrapper import MySQLConnection
from Evaluation import CorpusEvaluator
import cPickle as pickle
import numpy as np

""" DEFINE CONSTANTS """
# There must be at least that many occurrences of a token
COUNT_THRESHOLD = 0
VARIANCE_THRESHOLD = float('inf')
""" ---------------- """

load_pickled = None
if len(sys.argv) == 2:
    load_pickled = sys.argv[1]


""" PREPARE """
token_to_data = {}    #< maps a token to a tuple of its coordinates,  variance and its count
                      #< ((lon, lat), variance, count)
if load_pickled is None:
    # Make connection
    database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TRAIN")

    # Iterate over all tweets and split the tokenised texts.
    # Each token maps to a list of lon, lat tuples
    token_distribution = {}
    for tokens, lat, lon in database.getRows("`tokenised_low`, `lat`, `long`"):
        for token in tokens.split():
            token_distribution.setdefault(token, []).append((lon, lat))


    # Calculate the variance for each token
    # Factor for making degrees of longitude roughly equal degrees of latitude in variance calculation
    longitude_factor = 0.636

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

            token_to_data[token] = ((mean_lon, mean_lat), variance, count)

    pickle.dump(token_to_data, open('TokenToData.pickle', 'wb'))

else:
    token_to_data = pickle.load(open(load_pickled, 'rb'))

""" EVALUATE """
dev_corpus = CorpusEvaluator.CorpusEvaluator(corpus='DEV')
dev_corpus.setData(token_to_data)
dev_corpus.setDistanceThreshold(200)

thresholds = [2000,1700,1600, 1400, 1200, 1000, 800 , 600, 500, 1 ]
thresholds = range(1400, 1500, 10)
thresholds = [ 9, 8, 7, 6, 5, 4, 3, 2, 1 ]
thresholds = [ 2 ]
for threshold in thresholds:
    dev_corpus.setVarianceThreshold(threshold)
    print ""
    print threshold
    print dev_corpus.evaluateCorpus()
    
