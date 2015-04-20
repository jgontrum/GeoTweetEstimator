#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import os
import sys
from Wrapper import MySQLConnection
from Evaluation import CorpusEvaluator
import numpy as np

""" DEFINE CONSTANTS """
# There must be at least that many occurrences of a token
COUNT_THRESHOLD = 2
VARIANCE_THRESHOLD = float('inf')
""" ---------------- """

if len(sys.argv) != 2:
    print "Specify the output path for the graph."

""" PREPARE """
# Make connection
database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TRAIN")

# Iterate over all tweets and split the tokenised texts.
# Each token maps to a list of lon, lat tuples
token_distribution = {}
for tokens, lat, lon in database.getRows("`tokenised`, `lat`, `long`"):
    for token in tokens.split():
        token_distribution.setdefault(token, []).append((lon, lat))


# Calculate the variance for each token
token_to_data = {}    #< maps a token to a tuple of its coordinates,  variance and its count
                      #< ((lon, lat), variance, count)

# Factor for making degrees of longitude roughly equal degrees of latitude in variance calculation
longitude_factor = 0.636

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

        token_to_data[token] = ((mean_lon, mean_lon), variance, count)


""" EVALUATE """
dev_corpus = CorpusEvaluator.CorpusEvaluator(corpus='DEV')
dev_corpus.setData(token_to_data)

thresholds = [1,10,100]
for threshold in thresholds:
    dev_corpus.setVarianceThreshold(threshold)
    print dev_corpus.evaluateCorpus()
    