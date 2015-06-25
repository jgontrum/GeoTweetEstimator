#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import sys
import cPickle as pickle
from Wrapper import MySQLConnection
import os
from Evaluation import EvaluationFunctions
"""
Print the most regional tokens for a given cluster.

Usage:
python PrintRegionalTokens.py Signature Lon Lat range

"""

if len(sys.argv) < 4:
    print "1. TokenData, 2. ClusterData, 3. Cluster to analyse"
    sys.exit(1)

signature = pickle.load(open(sys.argv[1], 'rb'))
lon = sys.argv[2]
lat = sys.argv[2]
rang = 50 #km

token_to_data = {}
token_db = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TOKENDATA")

for tid, count, medx, medy, medz, varx, vary, varz in token_db.getTokenInfo(ids=None, columns="`id`, `count`, `median_x`, `median_y`, `median_z`, `variance_x`, `variance_y`, `variance_z`"):
    lon_, lat_ = EvaluationFunctions.convertCartesianToLatLong(medx, medy, medz)
    distance = EvaluationFunctions.getDistance(lon, lat, lon_, lat_)
    if distance < rang and count > 20:
        print signature.get(tid), ",", (varx,vary,varz), ",", count

