#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import unicodecsv
import json
import sys
import codecs
from TokenExtractor import TokenExtractor
from TweetValidator import TweetFilter

if len(sys.argv) != 3:
    print "1. Tweetfile, 2. CSV Output"
    sys.exit(1)

inputFile = codecs.open(sys.argv[1], 'rU')
outFile = sys.argv[2]

extractor = TokenExtractor()
filter = TweetFilter()

c = 0
m = 0
writer = unicodecsv.writer(open(outFile, 'wb'), delimiter=',', quotechar='"',escapechar='\\', quoting=unicodecsv.QUOTE_ALL, encoding='utf-8')
reader = unicodecsv.reader(inputFile, delimiter="|", quoting=unicodecsv.QUOTE_NONE)
for row in reader:
    c+=1
    if c % 10000 == 0:
        print c , m
    if len(row) > 6:
        try:
            timestamp = unicode(row[0].strip())
            user_id = long(row[1].strip())
            tweet_id = long(row[2].strip())
            try:
                reply_id = long(row[3].strip())
            except:
                reply_id = None
            try:
                lat = float(row[4].strip())
                lon = float(row[5].strip())
            except:
                lon = None
                lat = None

            tweet = unicode(" ".join(row[6:]).strip())
            #print tweet
            #print filter.isValidCSV(user_id, tweet)
            if lon is not None and filter.isValidCSV(user_id, tweet):
                tokens = extractor.extractTokens(tweet)
                text = " ".join(tokens)

                language = filter.checkLanguage(text)
                if language == None:
                    continue

                country = filter.getCountry(lat,lon)


                if country not in set(['DE', 'AT', 'CH']):
                    continue

                tokens_low = " ".join([x.lower() for x in tokens])
                m += 1
                writer.writerow([
                    tweet_id,
                    #jsonTweet[u'text'],
                    "",
                    text,
                    tokens_low,
                    lat,
                    lon,
                    user_id,
                    language[1],
                    country
                ])
        except Exception, e:
            print "Error in line:"
            print row
            print e
            pass


