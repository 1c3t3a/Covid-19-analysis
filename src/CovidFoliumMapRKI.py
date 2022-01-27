import pandas as pd
import numpy as np
import math
import os
import geopandas as gpd
import folium
import requests
import json
import datetime
from datetime import date, timedelta
from abc import ABC, abstractmethod
from pathlib import Path
from CovidFoliumMap import CovidFoliumMap, ensure_path_exists, download_JSON_file

""" This classes generate different folium maps based on the data of the RKI using access to the 
    RKI Covid-19 API.
    The class inherits from the CovidFoliumMap class. Here are some usefull links:

    - Geodata sources for Germany
      From the Bundesamt für Kartographie und Geodäsie:
        License plates (wfs_kfz250): https://gdz.bkg.bund.de/index.php/default/open-data/wfs-kfz-kennzeichen-1-250-000-wfs-kfz250.html
        Counties & population (wfs_vg250-ew): https://gdz.bkg.bund.de/index.php/default/open-data/wfs-verwaltungsgebiete-1-250-000-mit-einwohnerzahlen-stand-31-12-wfs-vg250-ew.html
      From OpenDataLab
        Good county, city, village maps with optional other meta information
        Portal: http://opendatalab.de/projects/geojson-utilities/
        a download from there creates 'landkreise_simplify0.geojson'. The 0 refers to highest resolution (1:250000)
        GitHub: https://github.com/opendatalab-de/simple-geodata-selector

    - RKI Covid-19 API
        Great REST API to retrieve the Covid-19 data of the RKI
        https://api.corona-zahlen.org/docs/endpoints/districts.html#districts-history-recovered
        BUT:
        The RKI divides Berlin in districts and that doesn't match regular geoJSON files. Therefore you should use the RKI geoJSON for 
        German counties/cities: https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/917fc37a709542548cc3be077a786c17_0/explore to
        download 'RKI_Corona_Landkreise.geojson'
"""

class CovidFoliumMapDEcounties(CovidFoliumMap):
    """
    This class will expose an interface to deal with Choropleth maps to display Covid-19 data attributes for counties and cities in Germany. 
    """
    def __init__(self, dataDirectory = '../data'):
        """ Constructor

        Args:
            dataDirectory (str, optional): The data directory to be used for cached data. Defaults to '../data'.
        """
        # init members
        self.__dataDirectory = dataDirectory + '/'
        self.__dfGeo = None
        self.__dfData = None
        self.__defaultMapOptions = CovidFoliumMap.mapOptions(mapDate=date.today(),
                                                            mapAlias = 'MapDEcounty',
                                                            mapLocation = [51.3, 10.5],
                                                            mapZoom = 6,
                                                            bins = [5, 25, 50, 100, 200, 400, 800, 1200, 1600, 2600],
                                                            mapAttribute = 'Robert Koch-Institut (RKI), dl-de/by-2-0, CMBT 2022',
                                                            tooltipAttributes = ['GeoName', 
                                                                                'Cases', 
                                                                                'Deaths', 
                                                                                'WeeklyCases', 
                                                                                'WeeklyDeaths', 
                                                                                'DailyCases', 
                                                                                'DailyDeaths', 
                                                                                'DailyRecovered', 
                                                                                'Incidence7DayPer100Kpopulation'])
        # ensure that the data directory exists, meaning to create it if it is not available
        self.__dataDirectory = ensure_path_exists(dataDirectory)
        # check if it really exists
        if self.__dataDirectory != '':
            # get the geo JSON data frame
            self.__dfGeo = self.__get_geo_data()
            # get the covid data for all counties/cities in the geo dataframe
            if not self.get_geo_df is None:
                self.__dfData = self.__get_covid_data(self.__dfGeo)
        # init base class
        super().__init__(self.__dataDirectory)

    def __get_geo_data(self):
        """ Downloads the JSON file from the RKI server if necessary and opens it to return a geoPandas dataframe. The function throws an
        exception in case of an error

        Returns:
            geo dataframe: the geo dataframe of the German counties and cities or None if it can't load the file
        """
        # init return
        geoDf = None
        # the filename of the geoJSON that is used
        targetFilename = self.__dataDirectory + '/' + 'RKI_Corona_Landkreise.geojson'
        # check if it exist already
        if not os.path.exists(targetFilename):
            # download the file
            print('Downloading data, that might take some time...')
            endpoint = 'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json'
            # the manual download link is
            # 'https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/917fc37a709542548cc3be077a786c17_0/explore?location=51.282342%2C10.714458%2C6.71'
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
            #print(geoDf.head())
        # finally return the geo df
        return geoDf

    def __get_covid_data(self, geoDf):
        """ Downloads the covid-19 data from the RKI servers if necessary, caches them and opens a final csv to return a Pandas dataframe. 
        
        Returns:
            covid dataframe: the covid data for the German counties and cities or None if it can't load the file
        """
        # init the result
        df = None
        # get the date
        today = date.today()
        # the prefix of the CSV file is Y-m-d
        preFix = today.strftime('%Y-%m-%d') + "-RKIcounty"
        # the target filename of the csv to be downloaded
        targetFilename = self.__dataDirectory + '/' + preFix + '-db.csv'
        # check if it exist already
        if os.path.exists(targetFilename):
            print('using existing file: ' + targetFilename)
            # read the file
            df = pd.read_csv(targetFilename)
        else:
            print('Downloading data, that might take some time...')
            # build a result df
            dfs = []
            for id in geoDf['RS']:
                try:
                    # get the data for the county
                    df = self.__get_county_data_from_web(id)
                    # add it to the list
                    dfs.append(df)
                except:
                    msg = 'Error getting the data for ' + id + '!'
                    print(msg) 
            # finally concatenate all dfs together
            df = pd.concat(dfs)  
            # save it to file
            df.to_csv(targetFilename)
            print('Download finished.')
        # ensure RS length is 5
        if not df is None:
            df['RS'] = df['RS'].astype(str).str.zfill(5)
        # ...and return df
        return df
    
    def __get_county_data_from_web(self, county_ID):
        """ Downloads the covid-19 data for the given county-ID

        Args:
            county_ID string: the county-ID for which we want the data

        Raises:
            ValueError: In case the data is empty

        Returns:
            dataframe: A dataframe of the county data
        """
        # the endpoint of the request
        endpoint = 'https://api.corona-zahlen.org/districts/' + county_ID
        # contact the server
        res = requests.get(endpoint)
        # check if there was a response
        if res.ok:
            # get the json
            res = res.json()
        else:
            # raise an exception
            res.raise_for_status()
        # check if the data is not empty
        if not bool(res['data']):
            raise ValueError("Empty response! County ID might be invalid.")
        df = pd.json_normalize(res['data'])
        df.columns = ['RS', 
                    'GeoName', 
                    'GeoID', 
                    'State', 
                    'Population', 
                    'Cases',
                    'Deaths',
                    'WeeklyCases',
                    'WeeklyDeaths',
                    'StateID',
                    'Recovered',
                    'Incidence7DayPer100Kpopulation', 
                    'CasesPer100kPopulation', 
                    'DailyCases', 
                    'DailyDeaths', 
                    'DailyRecovered']
        return df

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
        return 'RS'

    def get_nice_basemaps(self):
        """
        Returns an array of strings referring to nice basemaps for the specific region. At least one basemaps should be given and 
        the preferred basemap should be basemap[0]

        Returns:
            string: A array of strings referring to nice basemaps 
        """
        mapArray = ['cartodbpositron',
                    'https://server.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
                    'Stamen Terrain']
        return mapArray

class CovidFoliumMapDEstates(CovidFoliumMap):
    """
    This class will generate Choropleth maps to display Covid-19 data attributes for German states. 
    """
    def __init__(self, dataDirectory = '../data'):
        """ Constructor

        Args:
            dataDirectory (str, optional): The data directory to be used for cached data. Defaults to '../data'.
        """
        # init members
        self.__dataDirectory = dataDirectory + '/'
        self.__dfGeo = None
        self.__dfData = None
        self.__defaultMapOptions = CovidFoliumMap.mapOptions(mapDate=date.today(),
                                                            mapAlias = 'MapDEstate',
                                                            mapLocation = [51.3, 10.5],
                                                            mapZoom = 6,
                                                            bins = [5, 25, 50, 100, 200, 400, 800, 1200, 1600, 2600],
                                                            mapAttribute = 'Robert Koch-Institut (RKI), dl-de/by-2-0, CMBT 2022',
                                                            tooltipAttributes = ['GeoName', 
                                                                                'Cases', 
                                                                                'Deaths', 
                                                                                'WeeklyCases', 
                                                                                'WeeklyDeaths', 
                                                                                'DailyCases', 
                                                                                'DailyDeaths', 
                                                                                'DailyRecovered', 
                                                                                'Incidence7DayPer100Kpopulation',
                                                                                'HospitalizationCases7'])
        # a list of German states
        self.__statelist = [['Schleswig-Holstein', 'SH'],
                            ['Hamburg', 'HH'],
                            ['Niedersachsen', 'NI'],
                            ['Bremen', 'HB'],
                            ['Nordrhein-Westfalen', 'NW'],
                            ['Hessen', 'HE'],
                            ['Rheinland-Pfalz', 'RP'],
                            ['Baden-Württemberg', 'BW'],
                            ['Bayern', 'BY'],
                            ['Saarland', 'SL'],
                            ['Berlin', 'BE'],
                            ['Brandenburg', 'BB'],
                            ['Mecklenburg-Vorpommern', 'MV'],
                            ['Sachsen', 'SN'],
                            ['Sachsen-Anhalt', 'ST'],
                            ['Thüringen', 'TH']]
        # ensure that the data directory exists, meaning to create it if it is not available
        self.__dataDirectory = ensure_path_exists(dataDirectory)
        # check if it really exists
        if self.__dataDirectory != '':
            # get the geo JSON data frame
            self.__dfGeo = self.__get_geo_data()
            # get the covid data for all counties/cities in the geo dataframe
            if not self.get_geo_df is None:
                self.__dfData = self.__get_covid_data()
        # init the base class
        super().__init__(self.__dataDirectory)

    def __get_geo_data(self):
        """ Downloads the JSON file from the RKI server if necessary and opens it to return a geoPandas dataframe. The function throws an
        exception in case of an error

        Returns:
            geo dataframe: the geo dataframe of the German states or None if it can't load the file
        """
        # init return
        geoDf = None
        # the filename of the geoJSON that is used
        targetFilename = self.__dataDirectory + '/' + 'RKI_Corona_Bundeslaender.geojson'
        # check if it exist already
        if not os.path.exists(targetFilename):
            # download the file
            print('Downloading data, that might take some time...')
            endpoint = 'https://opendata.arcgis.com/api/v3/datasets/ef4b445a53c1406892257fe63129a8ea_0/downloads/data?format=geojson&spatialRefId=4326'
            # the manual download link is
            # 'https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/ef4b445a53c1406892257fe63129a8ea_0/explore'
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
        # finally return the geo df
        return geoDf

    def __get_covid_data(self):
        """ Downloads the covid-19 data from the RKI servers if necessary, caches them and opens a final csv to return a Pandas dataframe. 
        
        Returns:
            covid dataframe: the covid data for the German states or None if it can't load the file
        """
        # init the result
        df = None
        # get the date
        today = date.today()
        # the prefix of the CSV file is Y-m-d
        preFix = today.strftime('%Y-%m-%d') + "-RKIstates"
        # the target filename of the csv to be downloaded
        targetFilename = self.__dataDirectory + '/' + preFix + '-db.csv'
        # check if it exist already
        if os.path.exists(targetFilename):
            print('using existing file: ' + targetFilename)
            # read the file
            df = pd.read_csv(targetFilename)
        else:
            print('Downloading data, that might take some time...')
            # build a result df
            dfs = []
            for id in self.__statelist:
                try:
                    # get the data for the county
                    df = self.__get_state_data_from_web(id[1])
                    # add it to the list
                    dfs.append(df)
                except:
                    msg = 'Error getting the data for ' + id + '!'
                    print(msg) 
            # finally concatenate all dfs together
            df = pd.concat(dfs)  
            # save it to file
            df.to_csv(targetFilename)
            print('Download finished.')
            #print(df.head())
        # ensure AGS length is 2
        if not df is None:
            df['AGS_TXT'] = df['AGS_TXT'].astype(str).str.zfill(2)
        # ...and return df
        return df
    
    def __get_state_data_from_web(self, state_ID):
        """ Downloads the covid-19 data for the given county-ID

        Args:
            county_ID string: the county-ID for which we want the data

        Raises:
            ValueError: In case the data is empty

        Returns:
            dataframe: A dataframe of the county data
        """
        # the endpoint of the request
        endpoint = 'https://api.corona-zahlen.org/states/' + state_ID
        # contact the server
        res = requests.get(endpoint)
        # check if there was a response
        if res.ok:
            # get the json
            res = res.json()
        else:
            # raise an exception
            res.raise_for_status()
        # check if the data is not empty
        if not bool(res['data']):
            raise ValueError("Empty response! County ID might be invalid.")
        df = pd.json_normalize(res['data'])
        # adjust column names
        df.columns = ['AGS_TXT', 
                    'GeoName', 
                    'Population', 
                    'Cases',
                    'Deaths',
                    'WeeklyCases',
                    'WeeklyDeaths',
                    'Recovered',
                    'GeoID',
                    'Incidence7DayPer100Kpopulation', 
                    'CasesPer100kPopulation', 
                    'DailyCases', 
                    'DailyDeaths', 
                    'DailyRecovered',
                    'HospitalizationCases7',
                    'HospitalizationIncidence7',
                    'HospitalizationDate',
                    'HospitalizationUpdate']
        return df

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
        return 'AGS_TXT'

    def get_nice_basemaps(self):
        """
        Returns an array of strings referring to nice basemaps for the specific region. At least one basemaps should be given and 
        the preferred basemap should be basemap[0]

        Returns:
            string: A array of strings referring to nice basemaps 
        """
        mapArray = ['cartodbpositron',
                    'https://server.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
                    'Stamen Terrain']
        return mapArray
