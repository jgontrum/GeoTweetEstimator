#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import os
from Wrapper import MySQLConnection
from Evaluation import EvaluationFunctions
import cPickle as pickle
import numpy as np
from geopy.distance import great_circle

def pickleLocatedUsers(filenameMatrix, filenameUserToTweets):
    database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TRAIN")
    user_to_coordinates = []
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

    print "Saving data"
    pickle.dump(user_to_data, open(filenameUserToTweets, 'wb'))
    pickle.dump(user_to_coordinates, open(filenameMatrix, 'wb'))


def getNeighbourUsers(position, user_and_position,  range):
    #find next user
    (lon0, lat0) = position
    users = []
    for userid, (lon1, lat1) in user_and_position:
        # lon1, lat1 = EvaluationFunctions.convertCartesianToLatLong(x1,y1,z1)
        distance = great_circle((lat1, lon1), (lat0, lon0)).meters / 1000
        if distance < range:
            users.append(userid)
    return users