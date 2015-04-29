#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

from Wrapper import MySQLConnection
import os
import numpy as np
import cPickle as pickle
from sklearn.cluster import KMeans
from Evaluation import EvaluationFunctions

def pickleTrainingCorpus(filename):
    token_to_data = {}    #< maps a token to a tuple of its coordinates,  variance and its count
                          #< ((lon, lat), variance, count)
    COUNT_THRESHOLD = 1

    # Make connection
    database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TRAIN")

    # Iterate over all tweets and split the tokenised texts.
    # Each token maps to a list of lon, lat tuples
    token_distribution_cart = {}
    tweet_coordinates = []
    for tokens, lat, lon in database.getRows("`tokenised_low`, `lat`, `long`"):
        tweet_coordinates.append((lon, lat))
        cartesian = EvaluationFunctions.convertLatLongToCartesian(lon, lat)
        for token in tokens.split():
            token_distribution_cart.setdefault(token, []).append(cartesian)

    for token, coordinates_of_tuple in token_distribution_cart.iteritems():
        count = len(coordinates_of_tuple)
        if count > COUNT_THRESHOLD:
            # Convert coordinate list to numpy array
            np_list = np.asarray(coordinates_of_tuple, dtype=float)

            # Calculate the mean values for
            (mean_x, mean_y, mean_z) = tuple(np.mean(np_list, axis=0))

            variance_num = 0
            for (x, y, z) in coordinates_of_tuple:
                variance_num += (x - mean_x)**2 + (y - mean_y)**2 + (z - mean_z)**2

            # Calculate the variance
            variance = variance_num / count

            token_to_data[token] = (EvaluationFunctions.convertCartesianToLatLong(mean_x, mean_y, mean_z), variance, count)

    pickle.dump(token_to_data, open(filename, 'wb'))
    return tweet_coordinates 

def pickleClusters(filename, coordinate_list, k):
    data = np.asarray(coordinate_list, dtype=float)
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(data)
    pickle.dump(kmeans.cluster_centers_, open(filename, 'wb'))
    return list(kmeans.cluster_centers_)
