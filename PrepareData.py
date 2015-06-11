#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
import cPickle as pickle
from Wrapper import DataFunctions

if len(sys.argv) < 3:
    print "1. path for tokendata, 2. path for clusters"
    sys.exit(1)

token_to_data = DataFunctions.pickleTrainingCorpus(sys.argv[1])
#clusters = DataFunctions.pickleClusters(sys.argv[2], pickle.load(open(sys.argv[1], 'rb')), 7)

# for c in clusters:
#     print c