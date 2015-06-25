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
    print "1. Signature, 2. ClusterData"
    sys.exit(1)

""" LOAD DATA """
signature = pickle.load(open(sys.argv[1], 'rb'))
clusters = pickle.load(open(sys.argv[2], 'rb')) #<

token_db = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TOKENDATA")
variances_x = []
variances_y = []
variances_z = []
for varx, vary, varz in token_db.getTokenInfo(ids=None, columns="`variance_x`, `variance_y`, `variance_z`"):
    variances_x.append(varx)
    variances_y.append(vary)
    variances_z.append(varz)

variances_x = list(sorted(variances_x))
variances_y = list(sorted(variances_y))
variances_z = list(sorted(variances_z))

n = len(variances_x)

def getThreshold(t):
    pos = int(n * t)
    if t == 1:
        pos -= 1
    x = variances_x[pos]
    y = variances_y[pos]
    z = variances_z[pos]
    return (x,y,z)
""" EVALUATE """
dev_corpus = CorpusEvaluator.CorpusEvaluator(signature=signature, clusters=clusters, corpus=sys.argv[3])
dev_corpus.setDistanceThreshold(200)


# Load the evaluator:
evaluator = Weighting.InversedVarianceEvaluatorXYZ();

dev_corpus.setEvaluator(evaluator)

# Now run with different variance thresholds!
thresholds =[]
for i in range (1,100):
    i += 1
    l = i / 100.0
    thresholds.append(getThreshold(l))
#thresholds = [ getThreshold(1),getThreshold(0.75), getThreshold(0.4), getThreshold(0.3)]
c = 1
for threshold in thresholds:
    dev_corpus.setVarianceThreshold(threshold)
    #dev_corpus.createFallback()
    #print ""
    #print threshold
    #print dev_corpus.evaluateCorpus(printmsg=True)
    mean, med, valid = dev_corpus.evaluateCorpus()
    print c , ",", mean , ",", med, ",", valid
    c+=1
