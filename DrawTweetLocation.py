#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

import os
from Wrapper import MySQLConnection
from Wrapper import MapFunctions
import matplotlib.pyplot as plt

# Make connection
database = MySQLConnection.MySQLConnectionWrapper(basedir=os.getcwd(), corpus="DEV")

# Prepare map
basemap = MapFunctions.prepareMap()

# Iterate over database
counter = 0
for lat, lon in database.getRows("lat, long"):
    basemap.plot(lon, lat, 'r,', latlon=True)

plt.savefig('map.png', format='png')