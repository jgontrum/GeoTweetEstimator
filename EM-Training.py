#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
import cPickle as pickle
from Evaluation import EMEvaluator

load_pickled = None
if len(sys.argv) >= 2:
    load_pickled = sys.argv[1]
else:
    sys.exit(1)

token_to_data = pickle.load(open(load_pickled, 'rb')) #< ((lon, lat), variance, count)


""" EM-Training """
iterations = 5
dev_corpus = EMEvaluator.EMEvaluator(corpus='DEV')
tokens_to_coordinates = {}
tokens_to_factor = {}
change = 0

for token,data in token_to_data.iteritems():
    tokens_to_coordinates[token] = data[0]
    tokens_to_factor[token] = 1.0

for i in range(iterations):
    dev_corpus.setData(tokens_to_coordinates)
    score, data = dev_corpus.expectationAll()
    print i, score
    for token, problist in data.iteritems():
        avg = sum(problist) / float(len(problist))
        change += (tokens_to_factor[token] - avg)   

        lon, lat = tokens_to_coordinates[token]
        lon *= avg
        lat *= avg
        tokens_to_coordinates[token] = (lon, lat)
        tokens_to_factor[token] = avg
    print change




