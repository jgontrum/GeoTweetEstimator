#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import random
import cPickle as pickle
from TweetValidator import TweetFilter

filter = TweetFilter()
countries = set(['DE', 'AT', 'CH'])
count = 0
ret = []

while count < 10000:
    lat = random.uniform(5.0, 18.0)
    lon = random.uniform(45.7, 55.5)
    if filter.getCountry(lon, lat) in countries:
        count += 1
        ret.append((lat, lon))

pickle.dump(ret, open('randompos.pickle', 'wb'))