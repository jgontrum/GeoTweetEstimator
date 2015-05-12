#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
import cPickle as pickle
from Evaluation import EvaluationFunctions


""" DEFINE CONSTANTS """
# There must be at least that many occurrences of a token
COUNT_THRESHOLD = 2000
VARIANCE_PERCENTAGE = 75
""" ---------------- """

load_pickled = None
if len(sys.argv) == 4:
    load_pickled = sys.argv[1]
    load_clusters = sys.argv[2]
    cluster = int(sys.argv[2])
else:
    sys.exit(1)


""" PREPARE """
token_to_data = {}    #< maps a token to a tuple of its coordinates,  variance and its count
                      #< ((lon, lat), variance, count)

token_to_data = pickle.load(open(load_pickled, 'rb'))

""" ---------------- """

token_to_data_filtered = {}

for token, items in token_to_data.iteritems():
    if items[2] >= COUNT_THRESHOLD:
        token_to_data_filtered[token] = items

if cluster != -1:
    clusters = pickle.load(open(load_clusters, 'rb')) #<

    token_to_data_filtered_cluster = {}
    for token, items in token_to_data_filtered.iteritems():
        lon, lat = items[0]
        c = EvaluationFunctions.getCluster(lon,lat, clusters)
        if c == cluster:
            token_to_data_filtered_cluster[token] = items

    token_to_data_filtered = token_to_data_filtered_cluster


sorted_by_variance = sorted(token_to_data_filtered.iteritems(),key=lambda x: x[1][1], reverse=True)

num_tokens = len(sorted_by_variance)
print num_tokens
# sort by variance
for token in sorted_by_variance:
    print token[0] + " (" + str(token[1][2]) + ")"
sys.exit()

