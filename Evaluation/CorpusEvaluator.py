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

class CorpusEvaluator:
    def __init__(self, corpus='DEV'):
        self.tweets = [] # list of tokenised tweets
        self.location = [] # list of lat, lan tuples
        self.n = 0
        self.data = None
        self.token_to_factor = None
        self.clusters = None
        self.variance_threshold = 0
        self.distance_threshold = 0
        self.draw = False
        self.mode = "naive" # null, variance, top
        self.top = 2

        database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus=corpus)

        for tokens, lat, lon in database.getRows("`tokenised_low`, `lat`, `long`"):
            self.tweets.append(tokens.split())
            self.location.append((lon, lat))
        self.n = len(self.tweets)
        assert len(self.tweets) == len(self.location)

    def setData(self, data, token_to_factor, clusters):
        self.data = data
        self.token_to_factor = token_to_factor
        self.clusters = clusters

    def setMode(self, mode, top=2):
        self.mode = mode
        self.top = top

    def setVarianceThreshold(self, threshold):
        self.variance_threshold = threshold

    def setDistanceThreshold(self, threshold):
        self.distance_threshold = threshold

    def evaluateTweet(self, tokens, location):
        coordinate_list = []
        weight_list = []
        failed = 0
        var_sum = 0

        if self.draw:
            basemap = MapFunctions.prepareMap()

        text_pos = 1890000
        for token in tokens:
            if token not in self.data:
                failed += 1
                if self.draw:
                    plt.text(10000, text_pos, token.decode('utf8', 'ignore') + ' | (fail)', color='grey', fontsize=6)
                    text_pos -= 42000
                continue

            coordinates, variance, count = self.data[token]
            
            lon, lat = coordinates
            weight = self.token_to_factor[token]

            if variance < self.variance_threshold:
                # 0-hypothese
                if self.mode == "null":
                    token = self.data.keys()[randint(0,len(self.data.keys()))]
                    coordinates, variance, count = self.data[token]
                
                if self.draw:
                    plt.text(10000, text_pos, token.decode('utf8', 'ignore') + ' | ' + str(round(variance,1)) + ' | ' + str(count), color='black', fontsize=6)
                    text_pos -= 42000
                    current_color = EvaluationFunctions.getColorForValue(variance)
                    basemap.plot(lon, lat, 'o', latlon=True, markeredgecolor=current_color, color=current_color, markersize=EvaluationFunctions.getSizeForValue(count), alpha=0.7)

                coordinate_list.append(coordinates)
                if self.mode == 'variance':
                    if variance == 0:
                        variance = 0.0000000000000000001
                    weight = variance
                if self.mode == 'top':
                    weight = variance
                weight_list.append(weight)
                var_sum += variance

            else:
                failed += 1
                if self.draw:
                    plt.text(10000, text_pos,   token.decode('utf8', 'ignore') + ' | ' + str(round(variance,1)) + ' | ' + str(count),color='grey', fontsize=6)
                    text_pos -= 40000
                    current_color = 'gray' 
                    basemap.plot(lon, lat, 'o', latlon=True, markeredgecolor=current_color, color=current_color, markersize=EvaluationFunctions.getSizeForValue(count), alpha=0.1)

        denumerator = float(len(tokens) - failed)

        if denumerator == 0.0:
            plt.clf()
            return None

        if self.mode == "top":
            c = 0
            c_list = []
            w_list = []
            for i in sorted(range(len(weight_list)), key=lambda k: weight_list[k], reverse=True):
                c += 1
                if c <= self.top:
                    c_list.append(coordinate_list[i])
                    w_list.append(weight_list[i])
            coordinate_list = c_list
            weight_list = w_list

        lon_score, lat_score = EvaluationFunctions.getWeightedMidpoint(coordinate_list, weight_list)

        distance = EvaluationFunctions.getDistance(lon_score, lat_score, location[0], location[1])
        #print distance

        if self.draw:
            basemap.plot(location[0], location[1], '^', mfc='none' , markeredgecolor='black', latlon=True, alpha=1)
            basemap.plot(lon_score, lat_score, 'v',  mfc='none',  markeredgecolor='black', latlon=True, alpha=1)
           
            plt.text(10000,10000,'Distance: '+ str(round(distance,1)) + 'km')
            plt.text(10000,80000, 'Threshold: ' + str(self.variance_threshold))
            plt.savefig('img/tweet_' + str(self.variance_threshold) + "_" + str(self.i) + ".png", format='png')
            plt.clf()
        #print distance, ',', var_sum / denumerator

        return (lon_score, lat_score, location[0], location[1], distance)


    def evaluateCorpus(self):
        distance_score = 0
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
                distance_score += distance

                if EvaluationFunctions.evaluateDistance(distance, self.distance_threshold):
                    distance_matches += 1
                else:
                    distance_mismatches += 1

                if EvaluationFunctions.evaluateCluster(lon_calculated, lat_calculated, lon_real, lat_real, self.clusters, real_to_calc_matches):
                    cluster_matches += 1
                else:
                    cluster_mismatches += 1

                valids += 1

        print 'valid: ', valids, 'invalid: ', invalids

        print 'distance_match: ', distance_matches, 'distance_mismatches: ', distance_mismatches
        if distance_matches + distance_mismatches > 0:
            print 'distance_ratio: ', str(float(distance_matches) / (distance_matches + distance_mismatches))

        print 'cluster_matches: ', cluster_matches, 'cluster_mismatches: ', cluster_mismatches
        if cluster_matches + cluster_mismatches > 0:
            print 'cluster_ratio: ', str(float(cluster_matches) / (cluster_matches + cluster_mismatches))

        print "printing real to calc"
       
        print tabulate(real_to_calc_matches, tablefmt="latex",headers=range(n)) 
        
        print tabulate(EvaluationFunctions.transformStatistice(real_to_calc_matches), tablefmt="latex",headers=range(n)) 


        if valids > 0:
            return  distance_score / float(valids)
        else:
            return  float('inf')

