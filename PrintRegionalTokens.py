#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
import cPickle as pickle
from Evaluation import EvaluationFunctions

"""
Print the most regional tokens for a given cluster.

Usage:
python PrintRegionalTokens.py TokenData.py ClusterData.py          0
                                    ^            ^                 ^
                            Data created by   A list of centroid   The ID of the cluster
                     pickleTrainingCorpus()   positions, created   to analyse. To find overall
                        Maps a token to its   by pickleClusters(). common words, use -1.
                     position and variance.
"""

""" DEFINE CONSTANTS """
# There must be at least that many occurrences of a token
COUNT_THRESHOLD = 1500
VARIANCE_PERCENTAGE = 75
""" ---------------- """

if len(sys.argv) < 4:
    print "1. TokenData, 2. ClusterData, 3. Cluster to analyse"
    sys.exit(1)


""" PREPARE """
token_to_data = {}    #< maps a token to a tuple of its coordinates,  variance and its count
                      #< ((lon, lat), variance, count)

token_to_data = pickle.load(open(sys.argv[1], 'rb'))

""" ---------------- """

cluster = int(sys.argv[3])

token_to_data_filtered = {}

# Filter by count
for token, items in token_to_data.iteritems():
    if items[2] >= COUNT_THRESHOLD:
        token_to_data_filtered[token] = items

if cluster != -1: # Print the common words (for all of DE,AT,CH)
    clusters = pickle.load(open(sys.argv[2], 'rb')) #<

    token_to_data_filtered_cluster = {}
    for token, items in token_to_data_filtered.iteritems():
        lon, lat = items[0]
        c = EvaluationFunctions.getCluster(lon,lat, clusters)
        if c == cluster:
            token_to_data_filtered_cluster[token] = items

    token_to_data_filtered = token_to_data_filtered_cluster


sorted_by_variance = sorted(token_to_data_filtered.iteritems(),key=lambda x: x[1][1], reverse=True)

num_tokens = len(sorted_by_variance)
# sort by variance
for token in sorted_by_variance:
    print token[0] + " (" + str(token[1][2]) + ")"
print num_tokens

