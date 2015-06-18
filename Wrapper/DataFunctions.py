#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

from Wrapper import MySQLConnection
from Wrapper import Signature
import os
import numpy as np
import cPickle as pickle
import base64
from sklearn.cluster import KMeans
from Evaluation import EvaluationFunctions
import unicodecsv
import gzip
import gc

def mysqlTrainingCorpus(filenamecsv, filenamesig):
    log = open("log.txt", "w")
    COUNT_THRESHOLD = 2
    signature = Signature.Signature()
    # Make connection
    database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TRAIN")
    database2 = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TEST")
    database3 = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="DEV")

    good_tokens = []
    for tokens in database2.getRows("`tokenised_low`"):
        for token in EvaluationFunctions.getCoOccurrences(tokens[0].split()):
            good_tokens.append(token)
    for tokens in database3.getRows("`tokenised_low`"):
        for token in EvaluationFunctions.getCoOccurrences(tokens[0].split()):
            good_tokens.append(token)

    good_tokens = set(good_tokens)

    print len(good_tokens)
    # Iterate over all tweets and split the tokenised texts.
    # Each token maps to a list of lon, lat tuples
    token_distribution_cart = {}
    tweet_coordinates = []
    for tokens, lat, lon in database.getRows("`tokenised_low`, `lat`, `long`"):
        tweet_coordinates.append((lon, lat))
        cartesian = EvaluationFunctions.convertLatLongToCartesian(lon, lat)
        for token in EvaluationFunctions.getCoOccurrences(tokens.split()):
            token_distribution_cart.setdefault(token, []).append(cartesian)

    csvfile = gzip.open(filenamecsv + ".gz", "wb")
    writer = unicodecsv.writer(csvfile, delimiter=',', quotechar='"',escapechar='\\', quoting=unicodecsv.QUOTE_ALL, encoding='utf-8')
    
    pickle.dump(token_distribution_cart, open("Data/rawtokens.pikle","wb"))
    
    for token, coordinates_of_tuple in token_distribution_cart.iteritems():
        count = len(coordinates_of_tuple)
        if count > COUNT_THRESHOLD:
            tokenID = signature.add(token)
            # Convert coordinate list to numpy array
            if count > 20000:
                coordinates_of_tuple = coordinates_of_tuple[:20000]
            np_list = np.asarray(coordinates_of_tuple, dtype=float)

            # Calculate the mean values for
            mean = np.mean(np_list, axis=0)
            (mean_x, mean_y, mean_z) = tuple(mean)

            (median_x, median_y, median_z) = tuple(np.median(np_list, axis=0))

            variance_num = 0
            for (x, y, z) in coordinates_of_tuple:
                variance_num += (x - mean_x)**2 + (y - mean_y)**2 + (z - mean_z)**2

            # Calculate the variance
            variance = variance_num / count
            lon, lat = EvaluationFunctions.convertCartesianToLatLong(median_x, median_y, median_z)

            covariance = [[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]]
            if token in good_tokens:
                log.write(str(count) + "," + token[0] + "\n")
                log.flush()
                covariance = np.cov(np_list).tolist()

            writer.writerow([
                tokenID,"|".join(list(token)),
                lon,
                lat,
                variance,
                count,
                mean_x,
                mean_y,
                mean_z,
                covariance[0][0],
                covariance[0][1],
                covariance[0][2],
                covariance[1][0],
                covariance[1][1],
                covariance[1][2],
                covariance[2][0],
                covariance[2][1],
                covariance[2][2]
            ])
            del covariance
            del variance
            del mean
            del np_list
            if count > 10000:
                gc.collect()

    log.close()
    csvfile.close()
    pickle.dump(signature, open(filenamesig, 'wb'))
    return tweet_coordinates

def pickleTrainingCorpus(filename):
    token_to_data = {}    #< maps a token to a tuple of its coordinates,  variance and its count
                          #< ((lon, lat), variance, count, (meanx, meany, meanz), covar_matrix)
    COUNT_THRESHOLD = 0

    # Make connection
    database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TRAIN")

    # Iterate over all tweets and split the tokenised texts.
    # Each token maps to a list of lon, lat tuples
    token_distribution_cart = {}
    tweet_coordinates = []
    for tokens, lat, lon in database.getRows("`tokenised_low`, `lat`, `long`"):
        tweet_coordinates.append((lon, lat))
        cartesian = EvaluationFunctions.convertLatLongToCartesian(lon, lat)
        for token in EvaluationFunctions.getCoOccurrences(tokens.split()):
            token_distribution_cart.setdefault(token, []).append(cartesian)

    for token, coordinates_of_tuple in token_distribution_cart.iteritems():
        count = len(coordinates_of_tuple)
        if count > COUNT_THRESHOLD:
            # Convert coordinate list to numpy array
            np_list = np.asarray(coordinates_of_tuple, dtype=float)

            # Calculate the mean values for
            mean = tuple(np.mean(np_list, axis=0))
            (mean_x, mean_y, mean_z) = mean

            (median_x, median_y, median_z) = tuple(np.median(np_list, axis=0))

            covariance = np.cov(np_list).tolist()

            variance_num = 0
            for (x, y, z) in coordinates_of_tuple:
                variance_num += (x - mean_x)**2 + (y - mean_y)**2 + (z - mean_z)**2

            # Calculate the variance
            variance = variance_num / count

            # calculate the median


            token_to_data[token] = (EvaluationFunctions.convertCartesianToLatLong(median_x, median_y, median_z), variance, count, mean, covariance)

    pickle.dump(token_to_data, open(filename, 'wb'))
    return tweet_coordinates


def pickleClusters(filename, coordinate_list, k):
    data = np.asarray(coordinate_list, dtype=float)
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(data)
    pickle.dump(kmeans.cluster_centers_, open(filename, 'wb'))
    return list(kmeans.cluster_centers_)

