#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
import math
from Evaluation import CorpusEvaluator
import cPickle as pickle
from Evaluation import Weighting
from tabulate import tabulate

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

""" EVALUATE ALL """
dev_corpus = CorpusEvaluator.CorpusEvaluator(corpus='DEV')
dev_corpus.setData(token_to_data, clusters)
dev_corpus.setDistanceThreshold(200)

evaluator_list = [Weighting.UnweightedEvaluator(),
                  Weighting.InversedVarianceEvaluator(zerovariance = float(math.pow(10,6))),
                  Weighting.NegativeVarianceEvaluator(),
                  Weighting.WeightListEvaluator(token_to_factor, "all = 1")]

thresholds = [ 1, 0.0017138, 0.0014019, 0.000594, 0.0003886]

# for i in range(1,15):
#     evaluator =  Weighting.InversedVarianceEvaluator(zerovariance = float(math.pow(1,i))),
#
#     dev_corpus.setEvaluator(evaluator)
#     print "Evaluator: " + str(evaluator)
#
#     for threshold in thresholds:
#         dev_corpus.setVarianceThreshold(threshold)
#         print ""
#         print "threshold: ", threshold
#         print dev_corpus.evaluateCorpus()
#
#     print "\n\n"

results_distance = [["Evaluator", 100, 75, 50, 25, 20]]

results_cluster = [["Evaluator", 100, 75, 50, 25, 20]]

for evaluator in evaluator_list:
    dev_corpus.setEvaluator(evaluator)
    print "Evaluator: " + str(evaluator)

    row_distance = [str(evaluator)]
    row_cluster = [str(evaluator)]

    for threshold in thresholds:
        dev_corpus.setVarianceThreshold(threshold)
        print ""
        print "threshold: ", threshold
        dist, cluster = dev_corpus.evaluateCorpus()
        row_distance.append(dist)
        row_cluster.append(cluster)

    results_distance.append(row_distance)
    results_cluster.append(row_cluster)

    print "\n\n"

print "TOP"
for top in range(5,1,-1):
    for evaluator in evaluator_list:
        evaluator_top = Weighting.TopTokensEvaluator(evaluator, top=top)

        dev_corpus.setEvaluator(evaluator_top)
        print "Evaluator: " + str(evaluator_top)

        row_distance = [str(evaluator)]
        row_cluster = [str(evaluator)]

        for threshold in thresholds:
            dev_corpus.setVarianceThreshold(threshold)
            print ""
            print "threshold: ", threshold
            dist, cluster =  dev_corpus.evaluateCorpus()
            row_distance.append(dist)
            row_cluster.append(cluster)

        results_distance.append(row_distance)
        results_cluster.append(row_cluster)

        print "\n\n"

print tabulate(results_distance, tablefmt="latex")
print tabulate(results_cluster, tablefmt="latex")
