#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
import cPickle as pickle
from Wrapper import DataFunctions

"""
Creates the data needed for the evaluation of Tweets.

Usage:
python PrepareData.py TokenData.pickle ClusterData.pickle
                            ^                   ^
                     Maps a token to     Creates a list of
                     information like    centroid positions.
                     its position or
                     its variance,
"""

if len(sys.argv) < 3:
    print "1. path for tokendata 2 path for signature ( 3. path for clusters)"
    sys.exit(1)

if len(sys.argv) == 2: # create only the tokendata
    token_to_data = DataFunctions.mysqlTrainingCorpus(sys.argv[1], sys.argv[2])
else:
    token_to_data = DataFunctions.mysqlTrainingCorpus(sys.argv[1], sys.argv[2])
    clusters = DataFunctions.pickleClusters(sys.argv[3], token_to_data, 7)
