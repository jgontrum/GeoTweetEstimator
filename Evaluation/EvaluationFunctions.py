#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'
from geopy.distance import vincenty
import math

# Move lon2, lat2 closer to the coordinates of lon1 lon2.
def getWeightedPosition(lon1, lat1, lon2, lat2, x):
    distance_lon = lon2 - lon1
    newlon = lon1 + (distance_lon * x)
    distance_lat = lat2 - lat1
    newlat = lat1 + (distance_lat * x)
    return (newlon, newlat)

# calculate the eucleadian distance between two points
def getDistance(lon1, lat1, lon2, lat2):
    return vincenty((lat1, lon1), (lat2, lon2)).meters / 1000

# Checks, if the distance is within range
def evaluateDistance(distance, distance_threshold):
        return distance < distance_threshold

def evaluateCluster(lon1, lat1, lon2, lat2, clusters, statistics=None):
    cluster2 = getCluster(lon1, lat1, clusters)
    cluster1 = getCluster(lon2, lat2, clusters)
    if statistics is not None:
        statistics[cluster1][cluster2+1] += 1
    return cluster1 == cluster2

def transformStatistice(statistics):
    n = len(statistics)
    real_to_calc_matches = [[0 for x in range(n+1)] for x in range(n)] 
    for i in range(n):
        real_to_calc_matches[i][0] = i
        summed = float(sum(statistics[i][1:]))
        for j in range(1,n+1):
            real_to_calc_matches[i][j] = round(statistics[i][j] / summed,2)
    return real_to_calc_matches


# Return a color for a variance value
def getColorForValue(variance):
    t = 8.0
    if variance > t:
        return (1.0, 0 , 25.0/255.0)
    r = (255.0 * float(variance) / t)
    g = (255.0 * (t - float(variance)) / t)
    b = 25.0
    return (r/255.0, g/255.0, b/255.0)

# Return the size of a token for a count value
def getSizeForValue(count):
    t = 1000.0
    max_s = 70
    min_s = 5
    if count > t:
        return max_s
    size = float(count) / t * max_s
    if size < min_s:
        size = min_s
    return size

def convertLatLongToCartesian(lon, lat):
    lat = lat / (180/math.pi)
    lon = lon / (180/math.pi)
    x = math.cos(lat) * math.cos(lon)
    y = math.cos(lat) * math.sin(lon)
    z = math.sin(lat)
    return (x,y,z)

def convertCartesianToLatLong(x,y,z):
    lon = math.atan2(y, x)
    hyp = math.sqrt(x * x + y * y)
    lat = math.atan2(z, hyp)
    return (lon * (180/math.pi), lat * (180/math.pi))

def getWeightedMidpoint(coordinates, weights):
    assert len(coordinates) == len(weights)
    x_sum = 0
    y_sum = 0
    z_sum = 0
    weight_sum = 0
    for i in range(len(coordinates)):
        lon, lat = coordinates[i]
        weight = weights[i]
        x,y,z = convertLatLongToCartesian(lon, lat)
        x_sum = x_sum + (x * weight)
        y_sum = y_sum + (y * weight)
        z_sum = z_sum + (z * weight)
        weight_sum += weight

    ret =  convertCartesianToLatLong(x_sum / weight_sum, y_sum / weight_sum, z_sum / weight_sum)
    return ret


def getCluster(lon, lat, clusters):
    lowest_value = float('inf')
    lowest_cluster = -1

    for i in range(len(clusters)):
        cluster_lon, cluster_lat = clusters[i]
        distance = getDistance(cluster_lon, cluster_lat, lon, lat)
        if distance < lowest_value:
            lowest_value = distance
            lowest_cluster = i

    return lowest_cluster
