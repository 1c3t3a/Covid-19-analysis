import pandas as pd
import numpy as np
import math
import os
import datetime
from datetime import date, timedelta
from CovidFoliumMapWHO import FoliumCovid19MapWorld
from CovidFoliumMapWHO import FoliumCovid19MapAfrica
from CovidFoliumMapWHO import FoliumCovid19MapOceania
from CovidFoliumMapWHO import FoliumCovid19MapAmerica
from CovidFoliumMapWHO import FoliumCovid19MapAsia
from CovidFoliumMapWHO import FoliumCovid19MapEurope
from CovidFoliumMapRKI import FoliumCovid19MapDEstates
from CovidFoliumMapRKI import FoliumCovid19MapDEcounties

def main():
    # an array of instances
    mapObjects = []
    #"""
    # world
    mapObjects.append(FoliumCovid19MapWorld())
    # africa
    mapObjects.append(FoliumCovid19MapAfrica())
    # oceania
    mapObjects.append(FoliumCovid19MapOceania())
    # america
    mapObjects.append(FoliumCovid19MapAmerica())
    # asia
    mapObjects.append(FoliumCovid19MapAsia())
    # europe
    mapObjects.append(FoliumCovid19MapEurope())
    #"""
    #"""
    # de states
    mapObjects.append(FoliumCovid19MapDEstates())
    # de counties
    mapObjects.append(FoliumCovid19MapDEcounties())
    #"""
    
    # process the maps
    for mapObject in mapObjects:
        if mapObject.get_geo_df() is None:
            return
        # get the data directory
        dir = mapObject.get_data_directory()
        # select a basemap
        basemap = mapObject.get_nice_basemaps()[0]
        # build the default map
        map = mapObject.create_default_map(basemap)
        # save the map
        map.save(dir + '/' + mapObject.get_map_alias() + '.html')  
        if mapObject.get_map_alias().find('World') > 0:
            # build another map of the world
            map = mapObject.create_default_map(basemap, 'PercentDeaths', 'Case Fatality Rate (CFR)')
            # save that as well
            map.save(dir + '/' + mapObject.get_map_alias() + 'CFR.html')  
            # build another map of the world
            map = mapObject.create_default_map(basemap, 'CasesPerMillionPopulation', 'Cases per million population')
            # save that as well
            map.save(dir + '/' + mapObject.get_map_alias() + 'CasesPerMillionPopulation.html')   
    return

if __name__ == "__main__":
    main()
