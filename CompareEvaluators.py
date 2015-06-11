#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
import math
from Evaluation import CorpusEvaluator
import cPickle as pickle
from Evaluation import Weighting
from tabulate import tabulate

"""
Batch run evaluation with all the different evaluators.
The Evaluators in Evaluation.CorpusEvaluator are small modules that can be
plugged into the corpus evaluation function. They provide the weights
for each token in a tweet and can take their count and their variance into account.
This creates a lot ouf output. Make sure to save it in a file.

Usage:
python CompareEvaluators.py TokenData.pickle ClusterData.pickle   >   results.txt
                                   ^                ^
                            Data created by   A list of centroid
                     pickleTrainingCorpus()   positions, created by
                        Maps a token to its   pickleClusters().
                     position and variance.
"""

if len(sys.argv) < 3:
    print "First argument: Tokens, Second argument: Clusters"
    sys.exit(1)

token_to_data = pickle.load(open(sys.argv[1], 'rb')) #< ((lon, lat), variance, count)
clusters = pickle.load(open(sys.argv[2], 'rb')) #<

# In case one day we have a ML algorithm to learn the weights for each token,
# we can load it here and use the WeightListEvaluator. Ignored for now.
token_to_factor = {}
for token,data in token_to_data.iteritems():
    token_to_factor[token] = 1.0

""" EVALUATE ALL """
dev_corpus = CorpusEvaluator.CorpusEvaluator(corpus='DEV')
dev_corpus.setData(token_to_data, clusters)
dev_corpus.setDistanceThreshold(200)

evaluator_list = [Weighting.UnweightedEvaluator(),  # All tokens get the weight 1
                  Weighting.InversedVarianceEvaluator(zerovariance = float(math.pow(1,6))), # weight = 1/variance
                  Weighting.InversedVarianceEvaluatorComplex(pow = -1.0, sub = 0.0, zerovariance = float(math.pow(1,6))), # provides more options and different calculations
                  Weighting.NegativeVarianceEvaluator(), # wight = -1 * variance
                  Weighting.NegLogVarianceEvaluator(zerovariance = float(math.pow(1,6)))
                  ]

thresholds = [1, 0.0017138, 0.0014019, 0.000594, 0.0003886]

# Prepare data for output
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
        dist, median, cluster = dev_corpus.evaluateCorpus()
        row_distance.append(dist)
        row_cluster.append(cluster)

    results_distance.append(row_distance)
    results_cluster.append(row_cluster)

    print "\n\n"

# Use the TopTokensEvaluator. It ignores all tokens except for the n best one (sorted by variance).
print "##############\n## Look at TOP tweets!\n##############\n"
for top in range(5,1,-1):
    for evaluator in evaluator_list:
        evaluator_top = Weighting.TopTokensEvaluator(evaluator, top=top)

        dev_corpus.setEvaluator(evaluator_top)
        print "Evaluator (@TOP): " + str(evaluator_top)

        row_distance = [str(evaluator)]
        row_cluster = [str(evaluator)]

        for threshold in thresholds:
            dev_corpus.setVarianceThreshold(threshold)
            print ""
            print "threshold: ", threshold
            dist, med, cluster =  dev_corpus.evaluateCorpus()
            row_distance.append(dist)
            row_cluster.append(cluster)

        results_distance.append(row_distance)
        results_cluster.append(row_cluster)

        print "\n\n"

# Print results in latex format
print tabulate(results_distance, tablefmt="latex")
print tabulate(results_cluster, tablefmt="latex")
