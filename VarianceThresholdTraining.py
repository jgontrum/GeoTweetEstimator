#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
from Evaluation import CorpusEvaluator
import cPickle as pickle

load_pickled = None
if len(sys.argv) >= 3:
    load_pickled = sys.argv[1]
    load_clusters = sys.argv[2]
else:
    sys.exit(1)

token_to_data = pickle.load(open(load_pickled, 'rb')) #< ((lon, lat), variance, count)
clusters = pickle.load(open(load_clusters, 'rb')) #<

token_to_factor = {}
for token,data in token_to_data.iteritems():
    token_to_factor[token] = 1.0

""" EVALUATE """
dev_corpus = CorpusEvaluator.CorpusEvaluator(corpus='DEV')
dev_corpus.setData(token_to_data, token_to_factor, clusters)
dev_corpus.setDistanceThreshold(200)

thresholds = [2000,1700,1600, 1400, 1200, 1000, 800 , 600, 500, 1 ]
thresholds = range(1400, 1500, 10)
thresholds = [ float(sys.argv[3]) ]
for threshold in thresholds:
    dev_corpus.setVarianceThreshold(threshold)
    print ""
    print threshold
    print dev_corpus.evaluateCorpus()
    
