#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import os
from Wrapper import MySQLConnection
from Wrapper import MapFunctions
import matplotlib.pyplot as plt
from Evaluation import EvaluationFunctions
from random import randint
from tabulate import tabulate
import numpy as np
import math

class CorpusEvaluator:
    def __init__(self, corpus='DEV'):
        self.tweets = []        # list of tokenised tweets
        self.location = []      # list of lat, lan tuples
        self.n = 0              # The size of the corpus
        self.token_data = None  # Token data from pickleTrainingCorpus()
        self.clusters = None    # List of centroid coordinates
        self.variance_threshold = 0
        self.distance_threshold = 0
        self.draw = False       # Toggle weather each tweet should be saved to a PNG file
        self.evaluator = None   # Creates the weights for the tokens in a tweet
        self.null = False       # Test 0-hypothesis

        # Load corpus from database:
        database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus=corpus)

        for tokens, lat, lon, user in database.getRows("`tokenised_low`, `lat`, `long`, `user_id`"):
            self.tweets.append(tokens.split())
            self.location.append((lon, lat))
        self.n = len(self.tweets)
        assert len(self.tweets) == len(self.location)

    def setData(self, data, clusters, null=False):
        self.token_data = data
        self.clusters = clusters
        self.null = null

    def setEvaluator(self, evaluator):
        self.evaluator = evaluator

    def setVarianceThreshold(self, threshold):
        self.variance_threshold = threshold

    def setDistanceThreshold(self, threshold):
        self.distance_threshold = threshold

    # Takes a list of tokens and a location.
    # Calculates the position of the tweet and compares it to the actual
    # position.
    def evaluateTweet(self, tokens, location):
        token_data_here = []

        failed = 0
        if self.draw:
            basemap = MapFunctions.prepareMap()

        text_pos = 1890000
        
        # Look up the data for each token in the tweet
        for token in tokens:
            if token not in self.token_data:
                failed += 1
                if self.draw:
                    plt.text(10000, text_pos, token.decode('utf8', 'ignore') + ' | (fail)', color='grey', fontsize=6)
                    text_pos -= 42000
                continue

            coordinates, variance, count = self.token_data[token]
            lon, lat = coordinates

            if variance < self.variance_threshold:
                # 0-hypothese
                if self.null:
                    token = self.token_data.keys()[randint(0,len(self.token_data.keys()))]
                    coordinates, variance, count = self.token_data[token]

                if self.draw:
                    plt.text(10000, text_pos, token.decode('utf8', 'ignore') + ' | ' + str(round(variance,1)) + ' | ' + str(count), color='black', fontsize=6)
                    text_pos -= 42000
                    current_color = EvaluationFunctions.getColorForValue(variance)
                    basemap.plot(lon, lat, 'o', latlon=True, markeredgecolor=current_color, color=current_color, markersize=EvaluationFunctions.getSizeForValue(count), alpha=0.7)

                token_data_here.append((token, variance, count, coordinates))

            else:
                failed += 1
                if self.draw:
                    plt.text(10000, text_pos,   token.decode('utf8', 'ignore') + ' | ' + str(round(variance,1)) + ' | ' + str(count),color='grey', fontsize=6)
                    text_pos -= 40000
                    current_color = 'gray'
                    basemap.plot(lon, lat, 'o', latlon=True, markeredgecolor=current_color, color=current_color, markersize=EvaluationFunctions.getSizeForValue(count), alpha=0.1)

        if float(len(tokens) - failed) == 0.0:
            plt.clf()
            return None

        # Generate the data for the weighted midpoint
        coordinate_list, weight_list = self.evaluator.evaluate(token_data_here)

        # Calculate the midpoint
        lon_score, lat_score = EvaluationFunctions.getWeightedMidpoint(coordinate_list, weight_list)

        distance = EvaluationFunctions.getDistance(lon_score, lat_score, location[0], location[1])

        if self.draw:
            basemap.plot(location[0], location[1], '^', mfc='none' , markeredgecolor='black', latlon=True, alpha=1)
            basemap.plot(lon_score, lat_score, 'v',  mfc='none',  markeredgecolor='black', latlon=True, alpha=1)
           
            plt.text(10000,10000,'Distance: '+ str(round(distance,1)) + 'km')
            plt.text(10000,80000, 'Threshold: ' + str(self.variance_threshold))
            plt.savefig('img/tweet_' + str(self.variance_threshold) + "_" + str(self.i) + ".png", format='png')
            plt.clf()

        return (lon_score, lat_score, location[0], location[1], distance)


    def evaluateCorpus(self):
        distances = []
        valids = 0
        invalids = 0

        distance_matches = 0
        distance_mismatches = 0

        cluster_matches = 0
        cluster_mismatches = 0
        
        n = len(self.clusters)
        real_to_calc_matches = [[0 for x in range(n+1)] for x in range(n)] 
        for i in range(n):
            real_to_calc_matches[i][0] = i

       # self.n = 3
        for self.i in range(0,self.n):
            values = self.evaluateTweet(self.tweets[self.i], self.location[self.i])
            if values is None:
                invalids += 1
            else:
                lon_calculated, lat_calculated, lon_real, lat_real, distance = values
                distances.append(distance)

                if EvaluationFunctions.evaluateDistance(distance, self.distance_threshold):
                    distance_matches += 1
                else:
                    distance_mismatches += 1

                if EvaluationFunctions.evaluateCluster(lon_calculated, lat_calculated, lon_real, lat_real, self.clusters, real_to_calc_matches):
                    cluster_matches += 1
                else:
                    cluster_mismatches += 1

                valids += 1

        distances_np = np.asarray(distances, dtype=float)
        print 'valid: ', valids, 'invalid: ', invalids

        print 'distance_match: ', distance_matches, 'distance_mismatches: ', distance_mismatches
        if distance_matches + distance_mismatches > 0:
            print 'distance_ratio: ', str(float(distance_matches) / (distance_matches + distance_mismatches))

        print 'cluster_matches: ', cluster_matches, 'cluster_mismatches: ', cluster_mismatches
        if cluster_matches + cluster_mismatches > 0:
            print 'cluster_ratio: ', str(float(cluster_matches) / (cluster_matches + cluster_mismatches))

        # print "not used: ", self.tmpscore
        #print tabulate(real_to_calc_matches, tablefmt="latex",headers=range(n))
        
        #print tabulate(EvaluationFunctions.transformStatistice(real_to_calc_matches), tablefmt="latex",headers=range(n))

        if valids > 0:
            return  (np.mean(distances_np), np.median(distances_np), float(cluster_matches) / (cluster_matches + cluster_mismatches))
        else:
            return  (float('inf') , float('inf'))

