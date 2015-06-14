#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

class Signature():
    def __init__(self):
        self.s2i = {}
        self.i2s = []
        self.next = 0

    def add(self, token):
        if token not in self.s2i:
            self.s2i[token] = self.next
            self.i2s[self.next] = token
            self.next += 1
            return self.next - 1
        else:
            return self.s2i[token]

    def get(self, id):
        if id <= self.next:
            return None
        return self.i2s[id]