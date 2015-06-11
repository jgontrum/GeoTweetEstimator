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
if len(sys.argv) > 2:
    load_pickled = sys.argv[1]
    load_clusters = sys.argv[2]
else:
    sys.exit(1)

token_to_data = pickle.load(open(load_pickled, 'rb')) #< ((lon, lat), variance, count)
clusters = pickle.load(open(load_clusters, 'rb')) #<

""" EVALUATE """
dev_corpus = CorpusEvaluator.CorpusEvaluator(corpus='DEV')
dev_corpus.setData(token_to_data, clusters, null=False)
dev_corpus.setDistanceThreshold(200)
dev_corpus.setVarianceThreshold(0.0003886)

iter = 1000
step = 0.5

old_pow = -1.0
new_pow = old_pow

evaluator = Weighting.InversedVarianceEvaluator2(pow=old_pow)
dev_corpus.setEvaluator(evaluator)

first_score = dev_corpus.evaluateCorpus()
old_score = first_score[0]
new_score = old_score

while new_score <= old_score and new_pow > -9.0 and iter > 0:
    print old_pow
    old_score = new_score
    new_pow = old_pow - step

    evaluator = Weighting.InversedVarianceEvaluator2(pow=new_pow)
    dev_corpus.setEvaluator(evaluator)
    res = dev_corpus.evaluateCorpus()

    new_score = res[0]
    print "0:" , new_score
    sub = 0.00001
    while sub > 0:
        print sub
        evaluator = Weighting.InversedVarianceEvaluator2(sub=sub, pow=new_pow)
        dev_corpus.setEvaluator(evaluator)
        res = dev_corpus.evaluateCorpus()
        sub -= 0.000001
        print res[0]

    old_pow = new_pow
    iter -= 1


evaluator = Weighting.InversedVarianceEvaluator2(pow=old_pow)
dev_corpus.setEvaluator(evaluator)
print old_pow
print dev_corpus.evaluateCorpus()
print "vs:"
print first_score