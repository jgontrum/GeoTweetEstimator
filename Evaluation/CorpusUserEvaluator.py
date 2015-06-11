#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import os
from Wrapper import MySQLConnection
from Wrapper import MapFunctions
from Wrapper import LocateUsers
import matplotlib.pyplot as plt
from Evaluation import EvaluationFunctions
from random import randint
from tabulate import tabulate
import numpy as np
import math
import itertools
from Wrapper import LearnTokenLocations
from Evaluation import Weighting

class CorpusEvaluator:
    def __init__(self, corpus='DEV'):
        self.tweets = [] # list of tokenised tweets
        self.location = [] # list of lat, lan tuples
        self.users = []
        self.n = 0
        self.data = None
        self.clusters = None
        self.variance_threshold = 0
        self.distance_threshold = 0
        self.draw = False
        self.evaluator = None
        self.null = False # test 0-hypo
        self.user_to_midpoint = None
        self.user_data = {}

        database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus=corpus)

        for tokens, lat, lon, user in database.getRows("`tokenised_low`, `lat`, `long`, `user_id`"):
            self.tweets.append(tokens.split())
            self.location.append((lon, lat))
            self.users.append(user)
        self.n = len(self.tweets)
        assert len(self.tweets) == len(self.location)

    def setData(self, data, clusters, null=False):
        self.data = data
        self.clusters = clusters
        self.null = null

    def setEvaluator(self, evaluator):
        self.evaluator = evaluator
        self.simpleEvaluator = Weighting.TopTokensEvaluator(self.evaluator,2)

    def setVarianceThreshold(self, threshold):
        self.variance_threshold = threshold

    def setDistanceThreshold(self, threshold):
        self.distance_threshold = threshold

    def setUserToMidpoint(self, user_to_midpoint):
        self.user_to_midpoint = user_to_midpoint

    def setUserToTokenData(self, user_to_token_data):
        self.user_data = user_to_token_data

    def setUserToTweets(self, user_to_tweets):
        self.user_to_tweets = user_to_tweets

    def classifyUnknownUsers(self):
        user_to_tweets = {}
        local_user_to_mp = {}
        for i in range(len(self.users)):
            if self.users[i] not in self.user_data:
                user_to_tweets.setdefault(self.users[i],[]).append((self.tweets[i], self.location[i]))
        print "Classifying unknown users... "
        neighbours_count = 0
        for userID, tweets in user_to_tweets.iteritems():
            cart_coordinates = []
            real_coordinates = []
            # Now calculate the positions for all tweets of this user
            for tweet, loc in tweets:
                lon, lat = self.getPositionForTweet(tweet)
                real_coordinates.append(EvaluationFunctions.convertLatLongToCartesian(loc[0], loc[1]))
                cart_coordinates.append(EvaluationFunctions.convertLatLongToCartesian(lon, lat))
            # Find the median / midpoint of the user.
            np_list = np.asarray(cart_coordinates, dtype=float)
            (mean_x, mean_y, mean_z) = tuple(np.mean(np_list, axis=0)) # or mean

            np_list2 = np.asarray(real_coordinates, dtype=float)
            (mean_x2, mean_y2, mean_z2) = tuple(np.mean(np_list2, axis=0)) # or mean

            print EvaluationFunctions.getDistance(EvaluationFunctions.convertCartesianToLatLong(mean_x, mean_y, mean_z)[0],
                                                  EvaluationFunctions.convertCartesianToLatLong(mean_x, mean_y, mean_z)[1],
                                                  EvaluationFunctions.convertCartesianToLatLong(mean_x2, mean_y2, mean_z2)[0],
                                                  EvaluationFunctions.convertCartesianToLatLong(mean_x2, mean_y2, mean_z2)[1])


            # Find users that are < 50km away
            neighbours = LocateUsers.getNeighbourUsers(
                EvaluationFunctions.convertCartesianToLatLong(mean_x, mean_y, mean_z),
                self.user_to_midpoint.iteritems(),
                50)

            # Compute new token data for the tweets of all these users
            tweet_and_location = []
            for uid in neighbours:
                # for x,y in self.user_to_tweets[uid]:
                tweet_and_location += self.user_to_tweets[uid]

            neighbours_count == len(neighbours)
            # for item in tweet_and_location:
            #     print tweet_and_location

            new_token_data = LearnTokenLocations.createTokenScores(tweet_and_location, 1)
            self.user_data[userID] = new_token_data
            local_user_to_mp[userID] = EvaluationFunctions.convertCartesianToLatLong(mean_x, mean_y, mean_z)

        print "Done!"
        print "Avg Neighbours: " + str(neighbours_count / float(len(user_to_tweets.keys())))
        for uid, mp in local_user_to_mp.iteritems():
            self.user_to_midpoint[uid] = mp

    # The simple position calculation based on the over all data
    def getPositionForTweet(self, tokens):
        use_data = self.data
        failed = 0
        token_data = []

        for token in tokens:
            if token not in use_data:
                failed += 1
                continue
            coordinates, variance, count = use_data[token]
            if variance < self.variance_threshold:
                token_data.append((token, variance, count, coordinates))
            else:
                failed += 1

        denumerator = float(len(tokens) - failed)
        if denumerator == 0.0:
            return None
        else:
            coordinate_list, weight_list = self.simpleEvaluator.evaluate(token_data)
            lon_score, lat_score = EvaluationFunctions.getWeightedMidpoint(coordinate_list, weight_list)
            return (lon_score, lat_score)


    def evaluateTweet(self, tokens, location, user_id):
        token_data = []
        failed = 0

        use_data = None
        if user_id in self.user_data:
            use_data = self.user_data[user_id]
        else:
            use_data = self.data
        if self.draw:
            basemap = MapFunctions.prepareMap()

        text_pos = 1890000
        for token in tokens:
            if token not in use_data:
                failed += 1
                if self.draw:
                    plt.text(10000, text_pos, token.decode('utf8', 'ignore') + ' | (fail)', color='grey', fontsize=6)
                    text_pos -= 42000
                continue

            coordinates, variance, count = use_data[token]
            lon, lat = coordinates

            if variance < self.variance_threshold:
                # 0-hypothese
                if self.null:
                    token = use_data.keys()[randint(0,len(use_data.keys()))]
                    coordinates, variance, count = use_data[token]

                if self.draw:
                    plt.text(10000, text_pos, token.decode('utf8', 'ignore') + ' | ' + str(round(variance,1)) + ' | ' + str(count), color='black', fontsize=6)
                    text_pos -= 42000
                    current_color = EvaluationFunctions.getColorForValue(variance)
                    basemap.plot(lon, lat, 'o', latlon=True, markeredgecolor=current_color, color=current_color, markersize=EvaluationFunctions.getSizeForValue(count), alpha=0.7)

                token_data.append((token, variance, count, coordinates))

            else:
                failed += 1
                if self.draw:
                    plt.text(10000, text_pos,   token.decode('utf8', 'ignore') + ' | ' + str(round(variance,1)) + ' | ' + str(count),color='grey', fontsize=6)
                    text_pos -= 40000
                    current_color = 'gray'
                    basemap.plot(lon, lat, 'o', latlon=True, markeredgecolor=current_color, color=current_color, markersize=EvaluationFunctions.getSizeForValue(count), alpha=0.1)

        denumerator = float(len(tokens) - failed)
        if denumerator == 0.0 and user_id in self.user_to_midpoint:
            token_data.append(("", 1, 1, self.user_to_midpoint[user_id]))
        elif denumerator == 0.0 and user_id not in self.user_data:
            plt.clf()
            return None

        coordinate_list, weight_list = self.evaluator.evaluate(token_data)
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
        self.classifyUnknownUsers()

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

        for self.i in range(0,self.n):
            values = self.evaluateTweet(self.tweets[self.i], self.location[self.i], self.users[self.i])
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

