#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import os
from Wrapper import MySQLConnection
from Evaluation import EvaluationFunctions
import numpy as np
import cPickle as pickle

def pickleUserToMidpoint(filename):
    database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TRAIN")

    user_to_coordinates = {}
    # Each token maps to a list of lon, lat tuples
    token_distribution_cart = {}

    user_to_data = {}

    print "Getting data"
    for tokens, lat, lon, user in database.getRows(columns="`tokenised_low`, `lat`, `long`, `user_id`"):
        tokenised = tokens.split()
        cartesian = EvaluationFunctions.convertLatLongToCartesian(lon, lat)
        user_to_data.setdefault(user, []).append((tokenised, cartesian))

    print "Processing user"
    for user_id, tokens_and_coords in user_to_data.iteritems():
        coordinate_list = [coords for (tokens, coords) in tokens_and_coords]

        # Calculate the median for the user
        locations_np = np.asarray(coordinate_list, dtype=float)
        x,y,z = tuple(np.median(locations_np, axis=0))

        user_to_coordinates[user_id] = EvaluationFunctions.convertCartesianToLatLong(x,y,z)


    pickle.dump(user_to_coordinates, open(filename, 'wb'))


def pickleUserToUserTokenData(filename):
    COUNT_THRESHOLD = 1

    database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TRAIN")

    # token_to_data = {}    #< maps a token to a tuple of its coordinates,  variance and its count
                          #< ((lon, lat), variance, count)

    # Each token maps to a list of lon, lat tuples

    user_to_token_to_data = {}

    user_to_data = {}
    tweet_coordinates = []
    print "Getting data"
    for tokens, lat, lon, user in database.getRows(columns="`tokenised_low`, `lat`, `long`, `user_id`"):
        tokenised = tokens.split()
        tweet_coordinates.append((lon, lat))
        cartesian = EvaluationFunctions.convertLatLongToCartesian(lon, lat)
        user_to_data.setdefault(user, []).append((tokenised, cartesian))

    print "Processing users"
    for user_id, tokens_and_coords in user_to_data.iteritems():

        token_to_data = {}
        token_distribution_cart = {}
        for tokens, cartesian in tokens_and_coords:
            for token in tokens:
                token_distribution_cart.setdefault(token, []).append(cartesian)

        for token, coordinates_of_tuple in token_distribution_cart.iteritems():
            count = len(coordinates_of_tuple)
            # Convert coordinate list to numpy array
            np_list = np.asarray(coordinates_of_tuple, dtype=float)

            # Calculate the mean values for
            (mean_x, mean_y, mean_z) = tuple(np.mean(np_list, axis=0))

            variance_num = 0
            for (x, y, z) in coordinates_of_tuple:
                variance_num += (x - mean_x)**2 + (y - mean_y)**2 + (z - mean_z)**2

            # Calculate the variance
            variance = variance_num / count

            # calculate the median
            (mean_x, mean_y, mean_z) = tuple(np.median(np_list, axis=0))

            token_to_data[token] = (EvaluationFunctions.convertCartesianToLatLong(mean_x, mean_y, mean_z), variance, count)
        user_to_token_to_data[user_id] = token_to_data

    pickle.dump(user_to_token_to_data, open(filename, 'wb'))
    return tweet_coordinates
