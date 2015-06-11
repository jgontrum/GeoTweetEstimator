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

if len(sys.argv) < 2:
    print "1. path for tokendata ( 2. path for clusters)"
    sys.exit(1)

if len(sys.argv) == 1: # create only the tokendata
    token_to_data = DataFunctions.pickleTrainingCorpus(sys.argv[1])
else:
    token_to_data = DataFunctions.pickleTrainingCorpus(sys.argv[1])
    clusters = DataFunctions.pickleClusters(sys.argv[2], token_to_data, 7)
