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

jsonFile = codecs.open(sys.argv[1], 'r', "utf-8")
outFile = sys.argv[2]

extractor = TokenExtractor()
filter = TweetFilter()

c = 0
writer = unicodecsv.writer(open(outFile, 'wb'), delimiter=',', quotechar='"',escapechar='\\', quoting=unicodecsv.QUOTE_ALL, encoding='utf-8')
for line in jsonFile:
    try:
        if len(line) > 1:
            jsonTweet = json.loads(line)
            if jsonTweet[u'geo'] is not None and filter.isValid(jsonTweet):
                tokens = extractor.extractTokens(jsonTweet[u'text'])
                text = " ".join(tokens)

                language = filter.checkLanguage(text)
                if language == None:
                    continue

                country = filter.getCountry(jsonTweet[u'geo'][u'coordinates'][0], jsonTweet[u'geo'][u'coordinates'][1])

                if country not in set(['DE', 'AT', 'CH']):
                    continue

                tokens_low = " ".join([x.lower() for x in tokens])

                writer.writerow([
                    jsonTweet[u'id'],
                    #jsonTweet[u'text'],
                    "",
                    text,
                    tokens_low,
                    jsonTweet[u'geo'][u'coordinates'][0],
                    jsonTweet[u'geo'][u'coordinates'][1],
                    jsonTweet[u'user'][u'id'],
                    language[1],
                    country
                ])
    except:
        print "Error in line:"
        print line
        print ""
        pass


