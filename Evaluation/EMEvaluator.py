#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import os
from Wrapper import MySQLConnection
from Evaluation import EvaluationFunctions

class EMEvaluator:
    def __init__(self, corpus='DEV'):
        self.tweets = [] # list of tokenised tweets
        self.location = [] # list of lat, lan tuples
        self.n = 0
        self.token_to_coordinates = None
        self.token_to_coordinates = None
        self.draw = True

        database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus=corpus)

        for tokens, lat, lon in database.getRows("`tokenised_low`, `lat`, `long`"):
            self.tweets.append(tokens.split())
            self.location.append((lon, lat))
        self.n = len(self.tweets)
        assert len(self.tweets) == len(self.location)

    def setData(self, token_to_coordinates, token_to_factor):
        self.token_to_coordinates = token_to_coordinates
        self.token_to_factor = token_to_factor

    def getProbability(self, distance):
        return (500.0 - distance) / 500.0

    def expectation(self, tokens, location):
        real_lon, real_lat = location
        token_to_probability = {}

        lon_score = 0
        lat_score = 0
        failed = 0

        token_to_rate = {}
        for token in tokens:
            if token not in self.token_to_coordinates:
                continue
            token_to_rate[token] = self.token_to_factor[token]

        summed = sum(token_to_rate.values())

        for token in tokens:
            if token not in self.token_to_coordinates:
                failed += 1
                continue

            lon, lat = self.token_to_coordinates[token]

            rate = token_to_rate[token]# / float(summed)

            weighted_lon, weighted_lat  = EvaluationFunctions.getWeightedPosition(real_lon, real_lat, lon, lat, rate)

            lat_score += weighted_lat
            lon_score += weighted_lon
            """
            print "~~~~~~~~~~"
            print "Rate: " + str(rate)
            print "Real: " + str(location)
            print "Tok:  " + str(self.token_to_coordinates[token])
            print "Calculated: " + str((weighted_lon, weighted_lat))
            print ""
            """
            distance = EvaluationFunctions.getDistance(lon, lat, real_lon, real_lat)
            token_to_probability[token] = self.getProbability(distance)
            #print "new prob: " + str(self.getProbability(distance))

        denumerator = float(len(tokens) - failed)
        score = None
        if denumerator > 0.0:
            lat_score = lat_score / denumerator
            lon_score = lon_score / denumerator 
            score = EvaluationFunctions.getDistance(lon_score, lat_score, location[0], location[1])

        return (score, token_to_probability)

    def expectationAll(self):
        invalids = 0
        valids = 0
        score = 0

        #self.n = 3
        token_to_problist = {}

        for self.i in range(0,self.n):
            distance, token_to_probs = self.expectation(self.tweets[self.i], self.location[self.i])
            
            if distance is None:
                invalids += 1
            else:
                valids += 1
                score += distance

            for token, data in token_to_probs.iteritems():
                token_to_problist.setdefault(token, []).append(data)

        if valids > 0:
            return (score / float(valids), token_to_problist)
        else:
            return (float('inf'), token_to_problist)
