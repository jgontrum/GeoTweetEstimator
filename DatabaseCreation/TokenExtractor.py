#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import re

def regex_or(*items):
    return '(?:' + '|'.join(items) + ')'

class TokenExtractor:
    def __init__(self):
        # RegExp that define patterns, that should be REMOVED
        rURL = r'http://.+' # http://www.meh.de
        rURLs = r'https://.+'
        rNumber = r'\d+'
        rUser = r'@(\w|\d|-|_)+' # @motivationsara

        # Create the regex, that deletes unwanted stuff:
        self.deleteRegEx  = re.compile(
            unicode(regex_or(
                rURL,
                rURLs,
                rNumber,
                rUser
            ).decode('utf-8')), re.UNICODE)

        # What a word consists of. (Including @-handles, while the '#' of a hashtag will be removed)
        self.wordRegEx = re.compile(r'\w+', re.U)

    def extractTokens(self, text):
            ret = []
            deleted = self.deleteRegEx.sub("", text) # replace unwanted patterns by ''
            for token in self.wordRegEx.findall(deleted):
                if len(token) > 1: # Remove tokens, that only consist of one character
                    ret.append(unicode(token).encode("utf-8"))
            return ret
