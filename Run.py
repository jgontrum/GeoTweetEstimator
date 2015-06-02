#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
import math
from Evaluation import CorpusEvaluator
import cPickle as pickle
from Evaluation import Weighting
from WeightLearning import AvgDistance

load_pickled = None
if len(sys.argv) > 3:
    load_pickled = sys.argv[1]
    load_clusters = sys.argv[2]
else:
    sys.exit(1)

token_to_data = pickle.load(open(load_pickled, 'rb')) #< ((lon, lat), variance, count)
clusters = pickle.load(open(load_clusters, 'rb')) #<

""" EVALUATE """
"""
weights = None
try:
    weights = pickle.load(open("AvgDistanceWeights.pickle", 'rb'))
except:
    weights = AvgDistance.createWeightedList(token_to_data)
    pickle.dump(weights, open("AvgDistanceWeights.pickle", 'wb'))

evaluator_list = Weighting.WeightListEvaluator(weights, "AvgDistance")
"""

evaluator = Weighting.InversedVarianceEvaluator()
dev_corpus = CorpusEvaluator.CorpusEvaluator(corpus='DEV')
dev_corpus.setData(token_to_data, clusters, null=True)
dev_corpus.setDistanceThreshold(200)
dev_corpus.setEvaluator(evaluator)

thresholds = [ float(sys.argv[3]) ]
for threshold in thresholds:
    dev_corpus.setVarianceThreshold(threshold)
    print ""
    print threshold
    print dev_corpus.evaluateCorpus()
