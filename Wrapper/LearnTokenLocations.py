#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import numpy as np
from Evaluation import EvaluationFunctions

def createTokenScores(listOfTokensAndPositions, count_threshold):
    token_to_data = {}
    token_distribution_cart = {}

    for tokens, cartesian in listOfTokensAndPositions:
         for token in tokens:
            token_distribution_cart.setdefault(token, []).append(cartesian)

    for token, coordinates_of_tuple in token_distribution_cart.iteritems():
        count = len(coordinates_of_tuple)
        if count > count_threshold:
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

    return token_to_data