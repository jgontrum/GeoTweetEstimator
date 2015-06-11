#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

from TokenExtractor import regex_or
import re
import langid
import countries

class TweetFilter:
    def __init__(self):
        self.cc = countries.CountryChecker('geo-data/filtered.shp')
        
        """ Filter out the bad ones """
        self.bad_ids = set([203007243, 325160483, 186456725, 345423903, 169523312, 1211153959, 186456725])
        self.bad_tokensRegEx = re.compile(
            unicode(regex_or(
                r'Yelp',
                r'nowplaying',
                r'happy-hours',
                r'NowPlaying',
                r'via',
                r'4sq',
                r'rt',
                r'Goldmünzen',
                r'Nahrungseinheiten',
                r'gameinsight',
                r'androidgames',
                r'RT'
            ).decode('utf-8')), re.UNICODE)

    def getCountry(self, lat, lon):
        country = self.cc.getCountry(countries.Point(lat, lon))
        if not country == None:
            c = country.iso
            return c
        return "XX"

    def isValid(self, jsonTweet):
        return self.checkID(jsonTweet) and self.checkTokens(jsonTweet)

    def isValidCSV(self, user_id, tweet):
        if user_id not in self.bad_ids:
            for badToken in self.bad_tokensRegEx.finditer(tweet):
                return False
            return True
        return False

    def checkID(self, jsonTweet):
        if jsonTweet[u'user'][u'id'] in self.bad_ids:
            return False
        return True

    def checkTokens(self, jsonTweet):
        for badToken in self.bad_tokensRegEx.finditer(jsonTweet[u'text']):
            return False
        return True

    def checkLanguage(self, cleanText):
        l = langid.classify(cleanText)
        if l[0] != 'de':
            return None
        return l

    def checkGeo(self, lat, long):
        country = self.getCountry(lat, long)
        print country
        if country == "DE" or country == "AT" or country == "CH":
            return True
        return False
