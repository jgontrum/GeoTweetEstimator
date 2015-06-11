#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import os
from Wrapper import MySQLConnection
from Evaluation import EvaluationFunctions
import numpy as np
from sklearn.cluster import KMeans
from scipy.spatial import distance
import cPickle as pickle
from collections import Counter

def blah():
    database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TRAIN")

    user_to_coordinates = []
    # Each token maps to a list of lon, lat tuples
    token_distribution_cart = {}

    user_to_data = {}
    print "Getting data"
    for tokens, lat, lon, user in database.getRows(columns="`tokenised_low`, `lat`, `long`, `user_id`"):
        cartesian = EvaluationFunctions.convertLatLongToCartesian(lon, lat)
        user_to_data.setdefault(user, []).append((tokens.split(), cartesian))

    print "Processing user"
    for user_id, tokens_and_coords in user_to_data.iteritems():
        coordinate_list = [coords for (tokens, coords) in tokens_and_coords]

        # Calculate the median for the user
        locations_np = np.asarray(coordinate_list, dtype=float)
        x,y,z = tuple(np.median(locations_np, axis=0))

        user_to_coordinates.append((user_id, (x,y,z)))

    print "Clustering..."
    cluster_to_users = {}
    n = len(user_to_coordinates) / 1000
    data = np.asarray([coord for user_id, coord in user_to_coordinates], dtype=float)
    kmeans = KMeans(n_clusters=n)
    result = kmeans.fit_predict(data)
    for i in range(len(user_to_coordinates)):
        label = result[i]
        user_id = user_to_coordinates[i][0]
        cluster_to_users.setdefault(label, []).append(user_id)

    cluster_to_prob_dist = {}
    print "Calculate Token Probability Distribution"
    for cluster, user in cluster_to_users.iteritems():
        documents = []
        for user_id in user:
            for tokens, cords in user_to_data[user_id]:
                documents += tokens

        type_to_rel_freq = {}
        total = float(len(documents))
        for type, count in Counter(documents).iteritems(): # type -> count map
            type_to_rel_freq[type] = count / total
        cluster_to_prob_dist[cluster] = type_to_rel_freq

    for cluster, probd in cluster_to_prob_dist.iteritems():
        print cluster
        print probd
        print "--"
    #pickle.dump(kmeans.cluster_centers_, open(filename, 'wb'))