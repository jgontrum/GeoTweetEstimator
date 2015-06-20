#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
from Evaluation import CorpusEvaluator
import cPickle as pickle
from Evaluation import Weighting
from Wrapper import MySQLConnection
import os

"""
Evaluate the corpus. This is where the results are generated ;)
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
signature = pickle.load(open(sys.argv[1], 'rb'))
clusters = pickle.load(open(sys.argv[2], 'rb')) #<

token_db = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TOKENDATA")
variances = []
for var in token_db.getTokenInfo(ids=None, columns="`variance`"):
    variances += var

variance_data = list(sorted(variances))

""" EVALUATE """
dev_corpus = CorpusEvaluator.CorpusEvaluator(signature=signature, clusters=clusters, corpus='DEV')
dev_corpus.setDistanceThreshold(200)

# Load the evaluator:
evaluator = Weighting.InversedVarianceEvaluator();
dev_corpus.setEvaluator(evaluator)

# Now run with different variance thresholds!
thresholds = [ variance_data[int(len(variance_data) * 1)], variance_data[int(len(variance_data) * 0.75)], variance_data[int(len(variance_data) * 0.5)],  variance_data[int(len(variance_data) * 0.25)]]#, 1, 0.0017138, 0.0014019, 0.000594, 0.0003886 ] #1, 0.0017138, 0.0014019, 0.000594,
for threshold in thresholds:
    dev_corpus.setVarianceThreshold(threshold)
    print ""
    print threshold
    print dev_corpus.evaluateCorpus(printmsg=True)
