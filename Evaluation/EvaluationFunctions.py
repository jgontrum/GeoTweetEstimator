#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'
#from geopy.distance import vincenty
import math

# Move lon2, lat2 closer to the coordinates of lon1 lon2.
def getWeightedPosition(self, lon1, lat1, lon2, lat2, x):
    distance_lon = lon2 - lon1
    newlon = lon1 + (distance_lon * x)
    distance_lat = lat2 - lat1
    newlat = lat1 + (distance_lat * x)
    return (newlon, newlat)

# calculate the eucleadian distance between two points
#def getDistance(self, lon1, lat1, lon2, lat2):
#    return vincenty((lat1, lon1), (lat2, lon2)).meters / 1000

# Checks, if the distance is within range
def evaluateDistance(self, distance, distance_threshold):
        return distance < distance_threshold

# Return a color for a variance value
def getColorForValue(self, variance):
    t = 8.0
    if variance > t:
        return (1.0, 0 , 25.0/255.0)
    r = (255.0 * float(variance) / t)
    g = (255.0 * (t - float(variance)) / t)
    b = 25.0
    return (r/255.0, g/255.0, b/255.0)

# Return the size of a token for a count value
def getSizeForValue(self, count):
    t = 1000.0
    max_s = 70
    min_s = 5
    if count > t:
        return max_s
    size = float(count) / t * max_s
    if size < min_s:
        size = min_s
    return size

def __convertLatLongToCartesian(long, lat):
    lat = lat / (180/math.pi)
    long = long / (180/math.pi)
    x = math.cos(lat) * math.cos(long)
    y = math.cos(lat) * math.sin(long)
    z = math.sin(lat)
    return (x,y,z)

def __convertCartesianToLatLong(x,y,z):
    long = math.atan2(y, x)
    hyp = math.sqrt(x * x + y * y)
    lat = math.atan2(z, hyp)
    return (long * (180/math.pi), lat * (180/math.pi))

def getWeightedMidpoint(coordinates, weights):
    assert len(coordinates) == len(weights)
    x_sum = 0
    y_sum = 0
    z_sum = 0
    weight_sum = 0
    for i in range(len(coordinates)):
        lon, lat = coordinates[i]
        weight = weights[i]
        x,y,z = __convertLatLongToCartesian(lat, lon)
        x_sum = x_sum + (x * weight)
        y_sum = y_sum + (y * weight)
        z_sum = z_sum + (z * weight)
        weight_sum += weight

    return __convertCartesianToLatLong(x_sum / weight_sum, y_sum / weight_sum, z_sum / weight_sum)

