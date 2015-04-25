#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import os
import sys
from Wrapper import MySQLConnection
from operator import itemgetter
import cPickle as pickle
import numpy as np
import unicodecsv


""" DEFINE CONSTANTS """
# There must be at least that many occurrences of a token
COUNT_THRESHOLD = 2
VARIANCE_THRESHOLD = float('inf')
""" ---------------- """

load_pickled = None
if len(sys.argv) == 2:
    load_pickled = sys.argv[1]


""" PREPARE """
token_to_data = {}    #< maps a token to a tuple of its coordinates,  variance and its count
                      #< ((lon, lat), variance, count)
if load_pickled is None:
    # Make connection
    database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TRAIN")

    # Iterate over all tweets and split the tokenised texts.
    # Each token maps to a list of lon, lat tuples
    token_distribution = {}
    for tokens, lat, lon in database.getRows("`tokenised_low`, `lat`, `long`"):
        for token in tokens.split():
            token_distribution.setdefault(token, []).append((lon, lat))


    # Calculate the variance for each token
    # Factor for making degrees of longitude roughly equal degrees of latitude in variance calculation
    longitude_factor = 0.636

    for token, coordinates_of_tuple in token_distribution.iteritems():
        count = len(coordinates_of_tuple)
        if count > COUNT_THRESHOLD:
            # Convert coordinate list to numpy array
            np_list = np.asarray(coordinates_of_tuple, dtype=float)

            # Calculate the mean values for
            (mean_lon, mean_lat) = tuple(np.mean(np_list, axis=0))

            variance_num = 0
            for (point_lon, point_lat) in coordinates_of_tuple:
                variance_num += (point_lon - mean_lon)**2 + (longitude_factor*(point_lat - mean_lat))**2

            # Calculate the variance
            variance = variance_num / count

            token_to_data[token] = ((mean_lon, mean_lat), variance, count)

    pickle.dump(token_to_data, open('TokenToData.pickle', 'wb'))

else:
    token_to_data = pickle.load(open(load_pickled, 'rb'))
""" ---------------- """

sorted_by_variance = sorted(token_to_data.iteritems(),key=lambda x: x[1][2] )

outFile = 'var.csv'
writer = unicodecsv.writer(open(outFile, 'wb'), delimiter=',', quotechar='"',escapechar='\\', quoting=unicodecsv.QUOTE_ALL, encoding='utf-8')
for k,v in sorted_by_variance:
    writer.writerow([k, v[1], v[2]])

# sort by variance
c = 10
for token, values in sorted_by_variance:
    if c > 0:
        if values[1] > 20:
            print token, values 
            c -= 1
    else:
        break

print "---"

c = 10
for token, values in reversed(sorted_by_variance):
    if c > 0:
        if values[1] < 1 and values[2] > 500:
            print token, values
            c -= 1
    else:
        break