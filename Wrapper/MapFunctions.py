#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Johannes Gontrum <gontrum@uni-potsdam.de>'

from mpl_toolkits.basemap import Basemap

"""
This wrapper maintains all functions about the Basemap package, that allows you to draw graphs
directly on a map.
The prepareMap() function returns a Basemap-object, that is centered on Germany, Austria and Switzerland.
"""

# Returns a map with default setting
def prepareMap():
    map = Basemap(projection='merc',
    resolution='l',
                  area_thresh=200,
                  lat_0=51.16,  # center
                  lon_0=10.44,  # center
                  llcrnrlon=5.3,  # longitude of lower left hand corner of the desired map domain (degrees).
                  llcrnrlat=45,  # latitude of lower left hand corner of the desired map domain (degrees).
                  urcrnrlon=18,  # longitude of upper right hand corner of the desired map domain (degrees).
                  urcrnrlat=56  # latitude of upper right hand corner of the desired map domain (degrees).
    )

    # draw coastlines, state and country boundaries, edge of map.
    map.drawcoastlines(linewidth=0.25)
    map.drawcountries(linewidth=0.25)
    map.fillcontinents(color='snow', lake_color='lightcyan')
    # draw the edge of the map projection region (the projection limb)
    map.drawmapboundary(fill_color='lightblue')

    return map