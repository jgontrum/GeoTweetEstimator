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
from scipy.stats import multivariate_normal
import unicodecsv
import gzip
import gc

def mysqlTrainingCorpus_lat(filenamecsv, filenamesig):
    log = open("log.txt", "w")
    COUNT_THRESHOLD = 2
    signature = Signature.Signature()
    # Make connection
    database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus="TRAIN")
    # Iterate over all tweets and split the tokenised texts.
    # Each token maps to a list of lon, lat tuples
    token_distribution_cart = {}
    tweet_coordinates = []
    for tokens, lat, lon in database.getRows("`tokenised_low`, `lat`, `long`"):
        tweet_coordinates.append((lon, lat))
        for token in EvaluationFunctions.getCoOccurrences(tokens.split()):
            token_distribution_cart.setdefault(token, []).append((lon, lat))
            signature.add(token)
    
    pickle.dump(signature, open(filenamesig, 'wb'))
    
    #csvfile = gzip.open(filenamecsv + ".gz", "wb")
    csvfile = open(filenamecsv , "wb")
    writer = unicodecsv.writer(csvfile, delimiter=',', quotechar='"',escapechar='\\', quoting=unicodecsv.QUOTE_ALL, encoding='utf-8')
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
            (mean_lng, mean_lat) = tuple(mean)

            (median_lng, median_lat) = tuple(np.median(np_list, axis=0))

            variance_num = 0
            for lng, lat in coordinates_of_tuple:
                variance_num += (lng - mean_lng)**2 + (lat - median_lat)**2

            # Calculate the variance
            variance = variance_num / count
            np_list = np_list.T
            covariance = np.cov(np_list)
            v = None
            try:
                v = multivariate_normal(mean=mean, cov=covariance,allow_singular=True)
            except Exception, e:
                print e
                print covariance.shape, covariance.dtype
                print np_list.shape, np_list.dtype
                print count
                continue

            writer.writerow([
                tokenID,"|".join(list(token)),
                median_lng,
                median_lat,
                variance,
                count,
                base64.b64encode(pickle.dumps(v))
            ])
            del covariance
            del variance
            del mean
            del np_list
            if count > 10000:
                gc.collect()

    log.close()
    csvfile.close()
    return tweet_coordinates

def mysqlTrainingCorpus_xyz(filenamecsv, filenamesig):
    COUNT_THRESHOLD = 2
    signature = Signature.Signature()
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


    pickle.dump(signature, open(filenamesig, 'wb'))

    csvfile = open(filenamecsv , "wb")
    writer = unicodecsv.writer(csvfile, delimiter=',', quotechar='"',escapechar='\\', quoting=unicodecsv.QUOTE_ALL, encoding='utf-8')

    for token, coordinates_of_tuple in token_distribution_cart.iteritems():
        count = len(coordinates_of_tuple)
        if count > COUNT_THRESHOLD:
            tokenID = signature.add(token)
            # Convert coordinate list to numpy array
            np_list = np.asarray(coordinates_of_tuple, dtype=float)

            # Calculate the mean values for
            mean = tuple(np.mean(np_list, axis=0))
            (mean_x, mean_y, mean_z) = mean

            (median_x, median_y, median_z) = tuple(np.median(np_list, axis=0))

            variance = np.var(np_list, dtype=np.float64)
            variance_x = np.var(np_list, axis=0, dtype=np.float64)
            variance_y = np.var(np_list, axis=1, dtype=np.float64)
            variance_z = np.var(np_list, axis=2, dtype=np.float64)

            np_list = np_list.T
            covariance = np.cov(np_list)
            v = None
            try:
                v = multivariate_normal(mean=mean, cov=covariance,allow_singular=True)
            except Exception, e:
                print e
                print covariance.shape, covariance.dtype
                print np_list.shape, np_list.dtype
                print count
                continue

            writer.writerow([
                tokenID,"|".join(list(token)),
                median_x,
                median_y,
                median_z,
                variance,
                variance_x,
                variance_y,
                variance_z,
                count,
                base64.b64encode(pickle.dumps(v))
            ])
            del covariance
            del variance
            del mean
            del np_list
            if count > 10000:
                gc.collect()

    csvfile.close()
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

