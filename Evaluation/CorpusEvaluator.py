#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import os
import math
from Wrapper import MySQLConnection

class CorpusEvaluator:
    def __init__(self, corpus='DEV'):
        self.tweets = [] # list of tokenised tweets
        self.location = [] # list of lat, lan tuples
        self.n = 0
        self.data = None
        self.variance_threshold = 0

        database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus=corpus)

        for tokens, lat, lon in database.getRows("`tokenised`, `lat`, `long`"):
            self.tweets.append(tokens.split())
            self.location.append((lat, lon))
        self.n = len(self.tweets)
        assert len(self.tweets) == len(self.location)

    def setData(self, data):
        self.data = data

    # calculate the eucleadian distance between two points
    def getDistance(self, lon1, lat1, lon2, lat2):
        return math.sqrt(math.pow(lon1-lon2,2) + math.pow(lat1-lat2,2))

    def setVarianceThreshold(self, threshold):
        self.variance_threshold = threshold

    def evaluateTweet(self, tokens, location):
        lat_score = 0
        lon_score = 0
        failed = 0

        for token in tokens:
            #print token
            if token not in self.data:
                failed += 1
                #print 'not found', token
                continue
            coordinates, variance, count = self.data[token]

            if variance < self.variance_threshold:
                lat, lon = coordinates
                lat_score += lat
                lon_score += lon
            else:
                #print 'threshold failed ' + str(variance)
                failed += 1
        
        denumerator = float(len(tokens) - failed)
        
        #print "failed: ", failed , ' / ', len(tokens)

        if denumerator == 0.0:
            lon_score = 0
            lat_score = 0
        else:
            lat_score /= float(len(tokens) - failed)
            lon_score /= float(len(tokens) - failed)

        return self.getDistance(lon_score, lat_score, location[1], location[0])

    def evaluateCorpus(self):
        score = 0
        for i in range(1,self.n):
            #print i
            current_score = self.evaluateTweet(self.tweets[i], self.location[i])
            score += current_score
            #print '==='
            #raw_input('...')
        return score / float(self.n)
