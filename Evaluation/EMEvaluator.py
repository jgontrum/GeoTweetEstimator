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

    # calculate the distance between two points
    def getDistance(self, lon1, lat1, lon2, lat2):
        return vincenty((lat1, lon1), (lat2, lon2)).meters / 1000

    def getProbability(self, distance):
        return (600.0 - distance) / 600.0

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

            rate = token_to_rate[token] #/ float(summed)

            lat_score += lat * rate
            lon_score += lon * rate

            distance = self.getDistance(lon, lat, real_lon, real_lat)
            token_to_probability[token] = self.getProbability(distance)

        denumerator = float(len(tokens) - failed)
        score = None
        if denumerator > 0.0:
            lat_score = lat_score /  float(len(tokens) - failed)
            lon_score = lon_score / float(len(tokens) - failed)
            score = self.getDistance(lon_score, lat_score, location[0], location[1])

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
