#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import os
from Wrapper import MySQLConnection
from geopy.distance import vincenty

class EMEvaluator:
    def __init__(self, corpus='DEV'):
        self.tweets = [] # list of tokenised tweets
        self.location = [] # list of lat, lan tuples
        self.n = 0
        self.token_to_coordinates = None
        self.draw = True

        database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd() + "/", corpus=corpus)

        for tokens, lat, lon in database.getRows("`tokenised_low`, `lat`, `long`"):
            self.tweets.append(tokens.split())
            self.location.append((lon, lat))
        self.n = len(self.tweets)
        assert len(self.tweets) == len(self.location)

    def setData(self, data):
        self.token_to_coordinates = data

    # calculate the distance between two points
    def getDistance(self, lon1, lat1, lon2, lat2):
        return vincenty((lat1, lon1), (lat2, lon2)).meters / 1000

    def getProbability(self, distance):
        return (600.0 - distance) / 600.0

    def expectation(self, tokens, location):
        real_lon, real_lat = location
        token_to_probability = {}

        for token in tokens:
            if token not in self.token_to_coordinates:
                continue

            lon, lat = self.token_to_coordinates[token]

            distance = self.getDistance(lon, lat, real_lon, real_lat)
            token_to_probability[token] = self.getProbability(distance)

        return token_to_probability

    def expectationAll(self):
        #self.n = 3
        token_to_problist = {}

        for self.i in range(0,self.n):
            token_to_probs = self.expectation(self.tweets[self.i], self.location[self.i])
            for token, prob in token_to_probs.iteritems():
                token_to_problist.setdefault(token, []).append(prob)

        return prob
