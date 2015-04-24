#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import os
import math
from Wrapper import MySQLConnection
from geopy.distance import vincenty
from Wrapper import MapFunctions
import matplotlib.pyplot as plt

class CorpusEvaluator:
    def __init__(self, corpus='DEV'):
        self.tweets = [] # list of tokenised tweets
        self.location = [] # list of lat, lan tuples
        self.n = 0
        self.data = None
        self.variance_threshold = 0
        self.distance_threshold = 0
        self.draw = False

        database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus=corpus)

        for tokens, lat, lon in database.getRows("`tokenised_low`, `lat`, `long`"):
            self.tweets.append(tokens.split())
            self.location.append((lon, lat))
        self.n = len(self.tweets)
        assert len(self.tweets) == len(self.location)

    def setData(self, data):
        self.data = data

    # calculate the eucleadian distance between two points
    def getDistance(self, lon1, lat1, lon2, lat2):
        return vincenty((lat1, lon1), (lat2, lon2)).meters / 1000

    def setVarianceThreshold(self, threshold):
        self.variance_threshold = threshold

    def setDistanceThreshold(self, threshold):
        self.distance_threshold = threshold

    def evaluateTweet(self, tokens, location):
        lon_score = 0
        lat_score = 0
        failed = 0
        
        if self.draw:
            basemap = MapFunctions.prepareMap()

        for token in tokens:
            if token not in self.data:
                failed += 1
                continue

            coordinates, variance, count = self.data[token]
            
            lon, lat = coordinates

            if variance < self.variance_threshold:
                if self.draw:
                    basemap.plot(lon, lat, 'o', latlon=True, color=self.getColorForValue(variance), alpha=1)
                    lonx, laty = basemap(lon, lat)
                    # plt.text(lonx + 10000, laty + 10000, str(round(variance,1)) + '|' + str(count), fontsize=8)
                lat_score += lat
                lon_score += lon

            else:
                failed += 1
                if self.draw:
                    basemap.plot(lon, lat, 'o', latlon=True, color=self.getColorForValue(variance), alpha=0.3)
                    lonx, laty = basemap(lon, lat)
                    # plt.text(lonx + 10000, laty + 10000, str(round(variance,1)) + '|' + str(count),color='silver', fontsize=8)
        denumerator = float(len(tokens) - failed)

        if denumerator == 0.0:
            plt.clf()
            return None
        else:
            lat_score = lat_score /  float(len(tokens) - failed)
            lon_score = lon_score / float(len(tokens) - failed)
        
        
        distance = self.getDistance(lon_score, lat_score, location[0], location[1])
        
        if self.draw:
            basemap.plot(location[0], location[1], 'rx', latlon=True)
            basemap.plot(lon_score, lat_score, 'gx', latlon=True)
           
            plt.text(10000,10000,'Distance: '+ str(round(distance,1)) + 'km') 

            plt.savefig('img/tweet_' + str(self.variance_threshold) + "_" + str(self.i) + ".png", format='png')
            plt.clf()

        return distance

    def evaluateDistance(self, distance):
        return distance < self.distance_threshold

    def getColorForValue(self, variance):
        t = 5.0
        if variance > t:
            return (1.0, 0 , 25.0/255.0)
        r = (255.0 * float(variance) / t)
        g = (255.0 * (t - float(variance)) / t)
        b = 25.0
        return (r/255.0, g/255.0, b/255.0)


    def evaluateCorpus(self):
        score = 0
        valids = 0
        invalids = 0

        matches = 0
        mismatches = 0

        self.n = 3
        for self.i in range(0,self.n):
            current_score = self.evaluateTweet(self.tweets[self.i], self.location[self.i])
            if current_score is None:
                invalids += 1
            else:
                score += current_score
                if self.evaluateDistance(current_score):
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
