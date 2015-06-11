#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
import math
from Evaluation import CorpusEvaluator
import cPickle as pickle
from Evaluation import Weighting
from WeightLearning import AvgDistance
import numpy as np
from numpy import array

load_pickled = None
if len(sys.argv) > 2:
    load_pickled = sys.argv[1]
    load_clusters = sys.argv[2]
else:
    sys.exit(1)

token_to_data = pickle.load(open(load_pickled, 'rb')) #< ((lon, lat), variance, count)
clusters = pickle.load(open(load_clusters, 'rb')) #<

l = list(sorted([var for (x, var, y) in token_to_data.values()]))


""" EVALUATE """
dev_corpus = CorpusEvaluator.CorpusEvaluator(corpus='DEV')
dev_corpus.setData(token_to_data, clusters, null=False)
dev_corpus.setDistanceThreshold(200)


print "Data read!"
# evaluator = Weighting.NegLogVarianceEvaluator() #InversedVarianceEvaluator2(pow=-1.0)
evaluator = Weighting.InversedVarianceEvaluator();
dev_corpus.setEvaluator(evaluator)

thresholds = [  l[int(len(l) * 0.32)], l[int(len(l) * 0.31)], l[int(len(l) * 0.30)]]#, 1, 0.0017138, 0.0014019, 0.000594, 0.0003886 ] #1, 0.0017138, 0.0014019, 0.000594,
for threshold in thresholds:
    dev_corpus.setVarianceThreshold(threshold)
    print ""
    print threshold
    print dev_corpus.evaluateCorpus()
