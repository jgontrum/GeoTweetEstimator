#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

from Wrapper import MySQLConnection
from Evaluation import EvaluationFunctions
import os

#< ((lon, lat), variance, count)
def createWeightedList(token_to_data):
    token_to_weight = {}
    token_to_distance_list = {}

    database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TRAIN")

    for tokens, lat, lon in database.getRows("`tokenised_low`, `lat`, `long`"):
        for token in tokens.split():
            if token in token_to_data:
                token_lon, token_lat = token_to_data[token][0]
                distance = EvaluationFunctions.getDistance(lon, lat, token_lon, token_lat)
                token_to_distance_list.setdefault(token, []).append(distance)

    for token, distance_list in token_to_distance_list.iteritems():
        avg_distance = sum(distance_list) / float(len(distance_list))
        if avg_distance == 0:
            avg_distance = 0.0000001
        token_to_weight[token] =  1 / avg_distance

    return token_to_weight
