#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
import cPickle as pickle
from Evaluation import EMEvaluator
from Evaluation import CorpusEvaluator

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
    dev_corpus.setData(tokens_to_coordinates,tokens_to_factor)
    score, data = dev_corpus.expectationAll()
    print i, score
    for token, problist in data.iteritems():
        avg = sum(problist) / float(len(problist))
        change += (tokens_to_factor[token] - avg)   

        tokens_to_factor[token] = avg
    print change
    change = 0

dev_corpus_eval = CorpusEvaluator.CorpusEvaluator(corpus='DEV')
dev_corpus_eval.setData(token_to_data, tokens_to_factor)
dev_corpus_eval.setDistanceThreshold(200)

threshold = 5
dev_corpus_eval.setVarianceThreshold(threshold)
print ""
print threshold
print dev_corpus_eval.evaluateCorpus()

for key in tokens_to_factor.iterkeys():
    tokens_to_factor[key] = 1

print dev_corpus_eval.evaluateCorpus()


