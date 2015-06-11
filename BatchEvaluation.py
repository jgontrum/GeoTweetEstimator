#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
from Evaluation import CorpusEvaluator
import cPickle as pickle
from Evaluation import Weighting

"""
Like Evaluate Corpus, but runs with a lot of different variance cut-off values for better comparison.
Use PrepareData.py to create the data that is needed as arguments.

Usage:
python EvaluateCorpus.py TokenData.pickle ClusterData.pickle
                            ^                   ^
                     Maps a token to     A list of
                     information like    centroid positions.
                     its position or
                     its variance.
"""

load_pickled = None
if len(sys.argv) <= 2:
    print "1. TokenData, 2. ClusterData"
    sys.exit(1)

""" LOAD DATA """
token_to_data = pickle.load(open(sys.argv[1], 'rb')) #< ((lon, lat), variance, count)
clusters = pickle.load(open(sys.argv[2], 'rb')) #<

variance_data = list(sorted([var for (x, var, y) in token_to_data.values()]))

""" EVALUATE """
dev_corpus = CorpusEvaluator.CorpusEvaluator(corpus='DEV')
dev_corpus.setData(token_to_data, clusters, null=False)
dev_corpus.setDistanceThreshold(200)

# Load the evaluator:
evaluator = Weighting.InversedVarianceEvaluator();
dev_corpus.setEvaluator(evaluator)

# Now run with different variance thresholds!
thresholds = [ variance_data[int(len(variance_data) * 0.32)], variance_data[int(len(variance_data) * 0.31)], variance_data[int(len(variance_data) * 0.30)]]#, 1, 0.0017138, 0.0014019, 0.000594, 0.0003886 ] #1, 0.0017138, 0.0014019, 0.000594,
for threshold in thresholds:
    dev_corpus.setVarianceThreshold(threshold)
    print dev_corpus.evaluateCorpus()[0]


