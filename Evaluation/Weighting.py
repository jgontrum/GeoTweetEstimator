#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import math

class UnweightedEvaluator():
    def evaluate(self, token_data):
        # token_data = list of tupels (token, variance, count, (lon, lat)) in linear order
        coordinate_list = []
        weight_list = []

        for token, variance, count, coordinates in token_data:
            coordinate_list.append(coordinates)
            weight_list.append(1)

        return (coordinate_list, weight_list)

    def __str__(self):
        print "Unweighted Evaluator"


class InversedVarianceEvaluator():
    def __init__(self, zerovariance = float(math.pow(1,6))):
        self.zerovariance = zerovariance

    def evaluate(self, token_data):
        # token_data = list of tupels (token, variance, count, (lon, lat)) in linear order
        coordinate_list = []
        weight_list = []

        for token, variance, count, coordinates in token_data:
            coordinate_list.append(coordinates)
            if variance == 0:
                weight_list.append(self.zerovariance)
            else:
                weight_list.append(1.0/variance)

        return (coordinate_list, weight_list)

    def __str__(self):
        print "Inversed variance (1/variance) Evaluator with weight for variance==0: " + str(self.zerovariance)


class NegativeVarianceEvaluator():
    def evaluate(self, token_data):
        # token_data = list of tupels (token, variance, count, (lon, lat)) in linear order
        coordinate_list = []
        weight_list = []

        for token, variance, count, coordinates in token_data:
            coordinate_list.append(coordinates)
            weight_list.append(variance * -1)

        return (coordinate_list, weight_list)

    def __str__(self):
        print "Negative variance (var * -1) Evaluator"


class TopTokensEvaluator():
    def __init__(self, evaluator, top = 3):
        self.evaluator = evaluator
        self.top = top

    def evaluate(self, token_data):
        # token_data = list of tupels (token, variance, count, (lon, lat)) in linear order
        coordinate_list = []
        weight_list = []

        all_coordinates, all_weights = self.evaluator.evaluate(token_data)

        counter = 0
        coordinate_list = []
        weight_list = []
        for i in sorted(range(len(all_weights)), key=lambda k: all_weights[k], reverse=True):
            counter += 1
            if counter <= self.top:
                coordinate_list.append(all_coordinates[i])
                weight_list.append(all_weights[i])

        return (coordinate_list, weight_list)

    def __str__(self):
        print "Top-token Evaluator with top = " + str(self.top) + " and second evaluator = " + str(self.evaluator)


class WeightListEvaluator():
    def __init__(self, token_to_weight, note=""):
        self.token_to_weight = token_to_weight
        self.note = note

    def evaluate(self, token_data):
        # token_data = list of tupels (token, variance, count, (lon, lat)) in linear order
        coordinate_list = []
        weight_list = []

        for token, variance, count, coordinates in token_data:
            coordinate_list.append(coordinates)
            weight_list.append(self.token_to_weight[token])

        return (coordinate_list, weight_list)

    def __str__(self):
        print "Weight list Evaluator. Note: " + self.note
