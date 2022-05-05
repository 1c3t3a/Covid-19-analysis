import pandas as pd
import numpy as np
import math
import os
import geopandas as gpd
import folium
import datetime
from datetime import date, timedelta
from abc import ABC, abstractmethod
from pathlib import Path
from CovidCases import CovidCases
from CovidCasesWHO import CovidCasesWHO
from CovidCasesOWID import CovidCasesOWID
from CovidFoliumMap import CovidFoliumMap, ensure_path_exists, this_or_last_weekday, download_JSON_file
from enum import Enum

class Continents(Enum):
    """ an enum for the continents

    Args:
        Enum (int): an enum for the continents
    """
    # 
    World = 0
    Europe = 1
    Africa = 2
    Asia = 3
    Oceania = 4
    America = 5
    
class CovidFoliumMapWHO(CovidFoliumMap):
    """
    This class implements different folium maps based on the data of the WHO using the CovidCases and
    CovidCasesWHO classes. In case of the World and Asia maps it also uses the CovidCasesOWID class 
    to map the Taiwan cases as well.
    The class inherits from the CovidFoliumMap class 
    """
    def __init__(self, continent, dataDirectory = '../data', delay = 0):
        """ Constructor

        Args:
            continent (Continent): The continent to create the map for
            dataDirectory (str, optional): The data directory to be used for cached data. Defaults to '../data'.
        """
        # init members
        self.__dataDirectory = dataDirectory + '/'
        self.__dfGeo = None
        self.__dfData = None
        self.__defaultMapOptions = CovidFoliumMapWHO.get_map_options_by_continent(continent)
        # ensure that the data directory exists, meaning to create it if it is not available
        self.__dataDirectory = ensure_path_exists(dataDirectory)
        # check if it really exists
        if self.__dataDirectory != '':
            # get the geoJSON data frame
            self.__dfGeo = self.__get_geo_data()
            # get the covid data for all countries in the continent
            if not self.__dfGeo is None:
                self.__dfData = self.__get_covid_data(continent, delay)
        # init the base class
        super().__init__(self.__dataDirectory)

    def __get_geo_data(self):
        """ Downloads the geoJSON file from the server if necessary and opens it to return a geoPandas dataframe. 
        The function throws an exception in case of an error

        Returns:
            geo dataframe: the geo dataframe of the German states or None if it can't load the file
        """
        # init return
        geoDf = None
        # the filename of the geoJSON that is used
        targetFilename = self.__dataDirectory + '/' + 'WorldCountries.geojson'
        # check if it exist already
        if not os.path.exists(targetFilename):
            # download the file
            print('Downloading data (WorldCountries.geojson), that might take some time...')
            endpoint = 'https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson'
            # the manual download link is
            # 'https://github.com/datasets/geo-countries/blob/master/data/countries.geojson'
            try:
                # try to download the file 
                download_JSON_file(endpoint, targetFilename)
                print('Download finished.')
            except Exception as e:
                if hasattr(e, 'message'):
                    print(e.message)
                else:
                    print(e)    
        # now the file should exist
        if os.path.exists(targetFilename):
            # load the file
            geoDf = gpd.read_file(targetFilename)
        # adjust column names
        geoDf.columns = ['Name', 'ISO-3166-alpha_3', 'GeoID', 'geometry']
        # finally return the geo df
        return geoDf

    def __get_covid_data(self, continent, delay = 0):
        """ Downloads the covid-19 data from the RKI servers if necessary, caches them and opens a final csv to return a Pandas dataframe. 
        
        Args:
            continent (Continent): The continent to create the map for
            delay (int): A delay in days to the current date. especially during holidays the reporting is delayed

        Returns:
            covid dataframe: the covid data for the German states or None if it can't load the file
        """
        # init the result
        df = None
        try:
            # get the latests database file as a CSV
            dataFile = CovidCasesWHO.download_CSV_file()
            # get the data for the countryList
            whoData = CovidCasesWHO(dataFile)
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)  
            return df
        # g# the list of comma separated geoIDs for the continent
        if continent == Continents.World:
            countryList = whoData.get_pygal_asian_geoid_list()  + \
                          whoData.get_pygal_european_geoid_list()  +  \
                          whoData.get_pygal_american_geoid_list()  +  \
                          whoData.get_pygal_african_geoid_list()  +  \
                          whoData.get_pygal_oceania_geoid_list()
        elif continent == Continents.Europe:
            countryList = whoData.get_pygal_european_geoid_list()
        elif continent == Continents.Africa:
            countryList = whoData.get_pygal_african_geoid_list()
        elif continent == Continents.Asia:
            countryList = whoData.get_pygal_asian_geoid_list()
        elif continent == Continents.Oceania:
            countryList = whoData.get_pygal_oceania_geoid_list()
        elif continent == Continents.America:
            countryList = whoData.get_pygal_american_geoid_list()
        # since Omicron the WHO data for China seem to be incomplete
        if 'CN' in countryList:
            # remove china from the WHO list
            countryList.remove('CN')
        # get the data for the country list
        df = whoData.get_data_by_geoid_list(countryList)
        # add the incidence
        df = whoData.add_incidence_7day_per_100Kpopulation(df)
        if continent == Continents.Asia or continent == Continents.World:
            try:
                # get the OWID database as well
                dataFile = CovidCasesOWID.download_CSV_file()
                # get the OWID data
                owidData = CovidCasesOWID(dataFile)
            except Exception as e:
                if hasattr(e, 'message'):
                    print(e.message)
                else:
                    print(e)  
                return df
            # the taiwan, hongkong and china data
            dfTW = owidData.get_data_by_geoid_string_list('TW, HK, CN')
            # add the incidence
            dfTW = owidData.add_incidence_7day_per_100Kpopulation(dfTW)  
            # append it
            df = pd.concat([df, dfTW])  
        # get the data for last friday, on days reporting will not be good
        today = date.today() - datetime.timedelta(days=delay)
        # take care of weekends as the data is often not available on weekends
        if (today.weekday() == 0) or (today.weekday() == 6):
            last_friday = this_or_last_weekday(date.today(), 4)
            self.__defaultMapOptions.mapDate = date(last_friday.year, last_friday.month, last_friday.day)
        else:
            self.__defaultMapOptions.mapDate = today - timedelta(1)
        # get the data for that date
        dfDate = df.loc[df['Date'] == pd.to_datetime(self.__defaultMapOptions.mapDate)]     
        # ...and return df
        return dfDate

    def get_data_df(self):
        """ Returns the covid19 dataframe

        Returns:
            [Dataframe]: The pandas data frame with all data for the countries
        """
        return self.__dfData

    def get_geo_df(self):
        """ Returns the geoJSON dataframe

        Returns:
            [Dataframe]: The geoPandas data frame with all data for the countries
        """
        return self.__dfGeo

    def get_default_map_options(self):
        """ Returns the options for the default map

        Returns:
            [mapOptions]: The map options such as the default location and zoom
        """
        return self.__defaultMapOptions

    def get_merge_UID(self):
        """
        Returns the string holding the name of the unique ID of the data and the geo dataframe that can be used to merge the two

        Returns:
            string: A string holding the name of the unique ID of the data dataframe 
        """
        return 'GeoID'

    def get_nice_basemaps(self):
        """
        Returns an array of strings referring to nice basemaps for the specific region. At least one basemaps should be given and 
        the preferred basemap should be basemap[0]

        Returns:
            string: A array of strings referring to nice basemaps 
        """
        mapArray = ['https://server.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
                    'cartodbpositron',
                    'Stamen Terrain']
        return mapArray

    @staticmethod
    def get_map_options_by_continent(continent):
        """ The function generates default options for the WHO maps for the different continents

        Args:
            continent (Continents): the continent to generate the data for
        
        Returns:
            [mapOptions]: The options for the default map
        """
        mo = CovidFoliumMap.mapOptions()
        # init everything that is somehow constant for WHO maps
        mo.mapDate = date.today()
        # this will use automatically generated bins
        mo.bins = None
        # the leaflet
        mo.mapAttribute = 'WHO data. Map generated by CMBT, 2022'
        # all WHO dataframes will include these attributes
        mo.tooltipAttributes = ['GeoName', 
                                'Cases',
                                'Deaths', 
                                'PercentDeaths',
                                'DailyCases', 
                                'DailyDeaths', 
                                'Incidence7DayPer100Kpopulation',
                                'CasesPerMillionPopulation',
                                'DeathsPerMillionPopulation']
        if continent == Continents.World:
            # defaults for the world map
            mo.mapAlias = 'MapWorld' 
            mo.mapLocation = [15, 0]
            mo.mapZoom = 2
        elif continent == Continents.Europe:
            # defaults for the europe map
            mo.mapAlias = 'MapEurope' 
            mo.mapLocation = [51.3, 10.5]
            mo.mapZoom = 4
        elif continent == Continents.Africa:
            # defaults for the africa map
            mo.mapAlias = 'MapAfrica' 
            mo.mapLocation=[5, 19]
            mo.mapZoom = 4
        elif continent == Continents.Asia:
            # defaults for the asia map
            mo.mapAlias = 'MapAsia' 
            mo.mapLocation=[23, 92]
            mo.mapZoom = 4
        elif continent == Continents.Oceania:
            # defaults for the oceania map
            mo.mapAlias = 'MapOceania' 
            mo.mapLocation=[-26, 147]
            mo.mapZoom = 4
        elif continent == Continents.America:
            # defaults for the america map
            mo.mapAlias = 'MapAmerica' 
            mo.mapLocation=[16, -86]
            mo.mapZoom = 3
        # return the options
        return mo
