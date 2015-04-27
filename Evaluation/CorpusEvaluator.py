#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import os
from Wrapper import MySQLConnection
from Wrapper import MapFunctions
import matplotlib.pyplot as plt
from Evaluation import EvaluationFunctions

class CorpusEvaluator:
    def __init__(self, corpus='DEV'):
        self.tweets = [] # list of tokenised tweets
        self.location = [] # list of lat, lan tuples
        self.n = 0
        self.data = None
        self.token_to_factor = None
        self.variance_threshold = 0
        self.distance_threshold = 0
        self.draw = False

        database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus=corpus)

        for tokens, lat, lon in database.getRows("`tokenised_low`, `lat`, `long`"):
            self.tweets.append(tokens.split())
            self.location.append((lon, lat))
        self.n = len(self.tweets)
        assert len(self.tweets) == len(self.location)

    def setData(self, data, token_to_factor):
        self.data = data
        self.token_to_factor = token_to_factor

    def setVarianceThreshold(self, threshold):
        self.variance_threshold = threshold

    def setDistanceThreshold(self, threshold):
        self.distance_threshold = threshold

    def evaluateTweet(self, tokens, location):
        coordinate_list = []
        weight_list = []
        failed = 0
        
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

            # Update lon, lat values:
            #lon, lat = EvaluationFunctions.getWeightedPosition()

            if variance < self.variance_threshold:
                if self.draw:
                    plt.text(10000, text_pos, token.decode('utf8', 'ignore') + ' | ' + str(round(variance,1)) + ' | ' + str(count), color='black', fontsize=6)
                    text_pos -= 42000
                    current_color = EvaluationFunctions.getColorForValue(variance)
                    basemap.plot(lon, lat, 'o', latlon=True, markeredgecolor=current_color, color=current_color, markersize=EvaluationFunctions.getSizeForValue(count), alpha=0.7)

                coordinate_list.append(coordinates)
                weight_list.append(weight)

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

        lon_score, lat_score = EvaluationFunctions.getWeightedMidpoint(coordinate_list, weight_list)

        distance = EvaluationFunctions.getDistance(lon_score, lat_score, location[0], location[1])
        
        if self.draw:
            basemap.plot(location[0], location[1], '^', mfc='none' , markeredgecolor='black', latlon=True, alpha=1)
            basemap.plot(lon_score, lat_score, 'v',  mfc='none',  markeredgecolor='black', latlon=True, alpha=1)
           
            plt.text(10000,10000,'Distance: '+ str(round(distance,1)) + 'km')
            plt.text(10000,80000, 'Threshold: ' + str(self.variance_threshold))
            plt.savefig('img/tweet_' + str(self.variance_threshold) + "_" + str(self.i) + ".png", format='png')
            plt.clf()

        return distance


    def evaluateCorpus(self):
        score = 0
        valids = 0
        invalids = 0

        matches = 0
        mismatches = 0

        #self.n = 3
        for self.i in range(0,self.n):
            current_score = self.evaluateTweet(self.tweets[self.i], self.location[self.i])
            if current_score is None:
                invalids += 1
            else:
                score += current_score
                if EvaluationFunctions.evaluateDistance(current_score):
                    matches += 1
                else:
                    mismatches += 1
                valids += 1

        print 'valid: ', valids, 'invalid: ', invalids
        print 'match: ', matches, 'mismatches: ', mismatches
        if matches + mismatches > 0:
            print 'ratio: ', str(float(matches) / (matches + mismatches))

        if valids > 0:
            return score / float(valids)
        else:
            return float('inf')
