import pandas as pd
import numpy as np
import math
import os
import datetime
from datetime import datetime, date, timedelta
from CovidFoliumMapWHO import CovidFoliumMapWHO, Continents
from CovidFoliumMapRKI import CovidFoliumMapDEstates, CovidFoliumMapDEcounties
from CovidFoliumMapRKIageAndGender import CovidFoliumMapDEageAndGenderCounties, CovidFoliumMapDEageAndGenderStates

def main():
    # the directory for temp. data as well as for the output
    # check if this code is running in jupyter, either local or in colab
    try:
        # this will generate an exception if not executed in jupyter
        if 'google.colab' in str(get_ipython()):    
            outputDir = '/content/data/'
            print('Running on google colab. Using ' + outputDir + ' as the data directory')
        else:
            # the absolute directory of this python file
            absDirectory = os.path.dirname(os.path.abspath(os.path.abspath('')))
            # the target filename
            outputDir = os.path.join(absDirectory, './data/')
            print('Running on local jupyter server. Using ' + outputDir + ' as the data directory')
    except:
        # we are running not in jupyter
        outputDir = '../data'
        print('Running locally. Using ' + outputDir + ' as the data directory')

    # print the start time
    now = datetime.now()
    currentTime = now.strftime("%H:%M:%S")
    print("Starting at: ", currentTime)

    # an array of instances
    mapObjects = []
    
    # world
    mapObjects.append(CovidFoliumMapWHO(Continents.World, outputDir))
    # africa
    mapObjects.append(CovidFoliumMapWHO(Continents.Africa, outputDir))
    # oceania
    mapObjects.append(CovidFoliumMapWHO(Continents.Oceania, outputDir))
    # america
    mapObjects.append(CovidFoliumMapWHO(Continents.America, outputDir))
    # asia
    mapObjects.append(CovidFoliumMapWHO(Continents.Asia, outputDir))
    # europe
    mapObjects.append(CovidFoliumMapWHO(Continents.Europe, outputDir))
    
    # de states
    mapObjects.append(CovidFoliumMapDEstates(outputDir))
    # de counties
    mapObjects.append(CovidFoliumMapDEcounties(outputDir))
    # de states per age
    mapObjects.append(CovidFoliumMapDEageAndGenderStates(outputDir))
    # de counties per age
    mapObjects.append(CovidFoliumMapDEageAndGenderCounties(outputDir))
    
    # process the maps
    for mapObject in mapObjects:
        # check if it is initialized
        if mapObject.get_geo_df() is None:
            return
        # get the data directory
        dir = mapObject.get_data_directory()
        # select a basemap
        basemap = mapObject.get_nice_basemaps()[0]
        # build the default map
        if mapObject.get_default_map_options().mapAlias.find('age') > 0:
            # the maps contaning age based information
            map = mapObject.create_default_map(basemap, 
                                               coloredAttribute = 'Percent cases by age: 0-14', 
                                               coloredAttributeAlias = 'Percent cases age 0-14')
        else:
            # standard incidence based maps 
            map = mapObject.create_default_map(basemap)
        # the filename
        filename = mapObject.get_default_map_options().mapAlias
        # save the map
        if map is not None:
            map.save(dir + '/' + filename + '.html')  
        if mapObject.get_default_map_options().mapAlias.find('World') > 0:
            # the filename
            filename = mapObject.get_default_map_options().mapAlias

            # reset the bins as we want to generate them again automatically
            mapObject.get_default_map_options().bins = None
            # build another map of the world
            map = mapObject.create_default_map(basemap, 'PercentDeaths', 'Case Fatality Rate (CFR)')
            # save that as well
            if map is not None:
                map.save(dir + '/' + filename + 'CFR.html')  

            # reset the bins as we want to generate them again automatically
            mapObject.get_default_map_options().bins = None
            # build another map of the world 
            map = mapObject.create_default_map(basemap, 'CasesPerMillionPopulation', 'Cases per million population')
            # save that as well
            if map is not None:
                map.save(dir + '/' + filename + 'CasesPerMillionPopulation.html')   
    # print finished time
    now = datetime.now()
    currentTime = now.strftime("%H:%M:%S")
    print("Finished at: ", currentTime)
    return

if __name__ == "__main__":
    main()