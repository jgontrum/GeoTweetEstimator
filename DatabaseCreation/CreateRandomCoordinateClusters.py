#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import random
import cPickle as pickle
from TweetValidator import TweetFilter
import numpy as np
from sklearn.cluster import KMeans
import sys

"""
Creates clusters based on random data.

Usage:
python CreateRandomCoordinateClusters.py ClusterData.pickle 7
                                                ^           ^
                                        Output file.        # of clusters
"""

filter = TweetFilter()
countries = set(['DE', 'AT', 'CH'])
count = 0
ret = []

while count < 10000:
    lat = random.uniform(5.0, 18.0)
    lon = random.uniform(45.7, 55.5)
    if filter.getCountry(lon, lat) in countries:
        count += 1
        ret.append((lat, lon))

data = np.asarray(ret, dtype=float)
kmeans = KMeans(n_clusters=int(sys.argv[2]))
kmeans.fit(data)
pickle.dump(kmeans.cluster_centers_, open(sys.argv[2], 'wb'))
