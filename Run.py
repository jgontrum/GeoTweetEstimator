#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
import math
from Evaluation import CorpusEvaluator
import cPickle as pickle
from Evaluation import Weighting

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
evaluator_un = Weighting.UnweightedEvaluator()

evaluator_var = Weighting.InversedVarianceEvaluator(zerovariance = float(math.pow(1,6)))

evaluator_net_var = Weighting.NegativeVarianceEvaluator()

evaluator_list = Weighting.WeightListEvaluator(token_to_factor,"all = 1")

evaluator_top = Weighting.TopTokensEvaluator(evaluator_un, top = 3)

dev_corpus = CorpusEvaluator.CorpusEvaluator(corpus='DEV')
dev_corpus.setData(token_to_data, clusters)
dev_corpus.setDistanceThreshold(200)
dev_corpus.setEvaluator(evaluator_un)

thresholds = [ float(sys.argv[3]) ]
for threshold in thresholds:
    dev_corpus.setVarianceThreshold(threshold)
    print ""
    print threshold
    print dev_corpus.evaluateCorpus()
