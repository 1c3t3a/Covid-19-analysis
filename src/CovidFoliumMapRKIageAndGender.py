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
from collections import namedtuple
#!pip install recordclass
from recordclass import recordclass
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

class DownloadAndPreprocessRKIdata():
    def __init__(self, dataDirectory = '../data'):
        """ Constructor

        Args:
            dataDirectory (str, optional): The data directory to be used for cached data. Defaults to '../data'.
        """
        # ensure that the data directory exists, meaning to create it if it is not available
        self.__dataDirectory = ensure_path_exists(dataDirectory)
        # init the result
        self.__df = None
        # a mutable, named tuple to hold columnnames, groupID, alias and a datframe
        Group = recordclass('group', 'column name alias df')
        self.__groups = []
        # build the list
        self.__groups.append(Group('Altersgruppe', 'A00-A04', 'age: 0-4', None))
        self.__groups.append(Group('Altersgruppe', 'A05-A14', 'age: 5-14', None))
        self.__groups.append(Group('Altersgruppe', 'A15-A34', 'age: 15-34', None))
        self.__groups.append(Group('Altersgruppe', 'A35-A59', 'age: 35-59', None))
        self.__groups.append(Group('Altersgruppe', 'A60-A79', 'age: 60-79', None))
        self.__groups.append(Group('Altersgruppe', 'A80+', 'age: 80+', None))
        self.__groups.append(Group('Geschlecht', 'W', 'gender: female', None))
        self.__groups.append(Group('Geschlecht', 'M', 'gender: male', None))

    def __download_RKI_master_file(self):
        """ checks if the RKI master file of today exits already and downloads it if not

        Returns:
            [bool]: True in case the file is available for pre-processing
        """
        # check if we did all that stuff before
        if (self.__df is not None) and (self.__groups is not None):
           return True
        # get the date
        today = date.today()
        # the prefix of the CSV file is Y-m-d
        preFix = today.strftime('%Y-%m-%d') + "-RKI_COVID19"
        # the target filename of the csv to be downloaded
        targetFilename = self.__dataDirectory + '/' + preFix + '-db.csv'
        # check if it exist already
        if os.path.exists(targetFilename):
            print('using existing file: ' + targetFilename)
        else:
            # download the file
            print('Downloading data, that might take some time...')
            endpoint = 'https://www.arcgis.com/sharing/rest/content/items/f10774f1c63e40168479a1feb6c7ca74/data'
            # the manual download link is
            # https://www.arcgis.com/home/item.html?id=dd4580c810204019a7b8eb3e0b329dd6
            # or: https://www.arcgis.com/home/item.html?id=f10774f1c63e40168479a1feb6c7ca74  
            try:
                # try to download the file 
                req = requests.get(endpoint)
                # get the content
                content = req.content
                # open the file
                csv = open(targetFilename, 'wb')
                # write the file
                csv.write(content)
                # close the file
                csv.close()
                print('Download finished...')
            except Exception as e:
                if hasattr(e, 'message'):
                    print(e.message)
                else:
                    print(e)
                return False
        # now the file should exist
        if os.path.exists(targetFilename):
            df = pd.read_csv(targetFilename)
            # drop some columns that we don't need
            df = df.drop(columns=['NeuGenesen', 
                                  'AnzahlGenesen', 
                                  'IstErkrankungsbeginn', 
                                  'Altersgruppe2', 
                                  'Refdatum', 
                                  'NeuerTodesfall', 
                                  'Datenstand'])
        # set index to datetime of 'Meldedatum'
        df = df.set_index('Meldedatum')
        df.index = pd.to_datetime(df.index)
        # keep the dataframe
        self.__df = df
        # filter age groups
        print('Filtering by age/gender groups...')
        for group in self.__groups:
            group.df = df[df[group.column].str.match(group.name)]
        print('Filtering done...')
        return True

    def get_age_and_gender_data_by_county(self):
        """ Pre-processes the RKI master file to generate a csv holding the data per county

        Returns:
            [DataFrame]: The data frame holding the data per county or None in case something went wrong
        """
        # get the date
        today = date.today()
        # the prefix of the CSV file is Y-m-d
        preFix = today.strftime('%Y-%m-%d') + "-RKI_COVID19_age_gender_per_county"
        # the target filename of the csv to be used/created
        targetFilename = self.__dataDirectory + '/' + preFix + '-db.csv'
        if os.path.exists(targetFilename):
            print('using existing file: ' + targetFilename)
            # read the file
            df = pd.read_csv(targetFilename)
            print(df.head())
            # ...and return it
            return df
        else:
            # ensure that we have downloaded the RKI master file
            if self.__df is None:
                if not self.__download_RKI_master_file():
                    return None
        # build the sum of cases
        print('Building groups and sums...')
        dfGroupSum = []
        for group in self.__groups:
            # getting the sum for the group
            tmp = self.__group_and_sum_colum(group.df)
            # change the column name
            tmp.columns = ['Cases by ' + group.alias]
            # append it to the list
            dfGroupSum.append(tmp)
        # concat them horizontally so that the become columns 
        dfSums = pd.concat(dfGroupSum, axis=1)
        # create a data frame and reset its index
        dfAgeAndGender = pd.DataFrame(dfSums.copy()).reset_index()
        # convert NaN to 0
        dfAgeAndGender.fillna(value=0, inplace=True)
        # rename IDLandkreis to RS to match the column name of the geoJSON
        dfAgeAndGender.rename(columns={'IdLandkreis':'RS'}, inplace=True)
        print(dfAgeAndGender.head())
        print('Calculate percentages...')
        # get the county IDs
        IDs = dfAgeAndGender['RS'].unique()
        dfs = []
        for ID in IDs:
            # the county data
            dfSingle = dfAgeAndGender.loc[dfAgeAndGender['RS'] == ID].copy()
            # all cases of all age groups
            overallByAge = sum([dfSingle['Cases by age: 0-4'],
                                dfSingle['Cases by age: 5-14'],
                                dfSingle['Cases by age: 15-34'],
                                dfSingle['Cases by age: 35-59'],
                                dfSingle['Cases by age: 60-79'],
                                dfSingle['Cases by age: 80+']])
            # the percentages of some groups
            percentage = sum([dfSingle['Cases by age: 0-4'], dfSingle['Cases by age: 5-14']]) * 100 / overallByAge
            dfSingle['Percent cases by age: 0-14'] = percentage

            percentage = sum([dfSingle['Cases by age: 15-34'], dfSingle['Cases by age: 35-59'], dfSingle['Cases by age: 60-79']]) * 100 / overallByAge
            dfSingle['Percent cases by age: 15-79'] = percentage
            
            percentage = dfSingle['Cases by age: 80+'] * 100 / overallByAge
            dfSingle['Percent cases by age: 80+'] = percentage
            # put the rows together
            dfs.append(dfSingle)
        # concat them
        df = pd.concat(dfs)
        # write the result to a csv
        df.to_csv(targetFilename)
        return df

    def get_age_and_gender_data_by_state(self):
        """ Pre-processes the RKI master file to generate a csv holding the data per state

        Returns:
            [DataFrame]: The data frame holding the data per state or None in case something went wrong
        """
        # get the date
        today = date.today()
        # the prefix of the CSV file is Y-m-d
        preFix = today.strftime('%Y-%m-%d') + "-RKI_COVID19_age_gender_per_state"
        # the target filename of the csv to be used/created
        targetFilename = self.__dataDirectory + '/' + preFix + '-db.csv'
        if os.path.exists(targetFilename):
            print('using existing file: ' + targetFilename)
            # read the file
            df = pd.read_csv(targetFilename)
            print(df.head())
            # ...and return it
            return df
        else:
            # ensure that we have downloaded the RKI master file
            if self.__df is None:
                if not self.__download_RKI_master_file():
                    return None
        # build the sum of cases
        print('Building groups and sums...')
        dfGroupSum = []
        for group in self.__groups:
            # getting the sum for the group
            tmp = self.__group_and_sum_colum(group.df, groupColumn='IdBundesland')
            # change the column name
            tmp.columns = ['Cases by ' + group.alias]
            # append it to the list
            dfGroupSum.append(tmp)
        # concat them horizontally so that the become columns 
        dfSums = pd.concat(dfGroupSum, axis=1)
        # create a data frame and reset its index
        dfAgeAndGender = pd.DataFrame(dfSums.copy()).reset_index()
        # convert NaN to 0
        dfAgeAndGender.fillna(value=0, inplace=True)
        # rename IdBundesland to AGS_TXT to match the column name of the geoJSON
        dfAgeAndGender.rename(columns={'IdBundesland':'AGS_TXT'}, inplace=True)
        print('Calculate percentages...')
        # get the county IDs
        IDs = dfAgeAndGender['AGS_TXT'].unique()
        dfs = []
        for ID in IDs:
            # the county data
            dfSingle = dfAgeAndGender.loc[dfAgeAndGender['AGS_TXT'] == ID].copy()
            # all cases of all age groups
            overallByAge = sum([dfSingle['Cases by age: 0-4'],
                                dfSingle['Cases by age: 5-14'],
                                dfSingle['Cases by age: 15-34'],
                                dfSingle['Cases by age: 35-59'],
                                dfSingle['Cases by age: 60-79'],
                                dfSingle['Cases by age: 80+']])
            # the percentages of some groups
            percentage = sum([dfSingle['Cases by age: 0-4'], dfSingle['Cases by age: 5-14']]) * 100 / overallByAge
            dfSingle['Percent cases by age: 0-14'] = percentage

            percentage = sum([dfSingle['Cases by age: 15-34'], dfSingle['Cases by age: 35-59'], dfSingle['Cases by age: 60-79']]) * 100 / overallByAge
            dfSingle['Percent cases by age: 15-79'] = percentage
            
            percentage = dfSingle['Cases by age: 80+'] * 100 / overallByAge
            dfSingle['Percent cases by age: 80+'] = percentage
            # put the rows together
            dfs.append(dfSingle)
        # concat them
        df = pd.concat(dfs)
        # write the result to a csv
        df.to_csv(targetFilename)
        return df

    def __group_and_sum_colum(self, df, groupColumn = 'IdLandkreis', sumColumn='AnzahlFall', flagColumn='NeuerFall'):
        """ Groups the data by the groupColumn and builds the sum of the sumColumn. The data in the sumColumn might be 
        invalid depending on a flag in the flagColumn

        Args:
            df (DataFrame): the huge df loaded from the RKI master file
            groupColumn (str, optional): The grouping column. Defaults to 'IdLandkreis', can be 'IdBundesland' as well.
            sumColumn (str, optional): The column to be summed up. Defaults to 'AnzahlFall'.
            flagColumn (str, optional): The column holding the flag if the data is valid or not. -1, 0 or 1 refer to valid 
            data. Defaults to 'NeuerFall'.

        Returns:
            [DataFrame]: A data frame holding the values of the group (e.g. IdLandkreis) vertically and the grouped 
            sums horizontally
        """
        # flag column must be in -1, 0, 1 to indicate valid numbers
        flag = df[flagColumn].isin((-1, 0, 1))
        # group the flagged rows and build the sum
        series = df[flag].groupby([groupColumn])[sumColumn].sum().to_frame(name = sumColumn).reset_index()
        # make an array 
        #series = series[['IdLandkreis', 'AnzahlFall']]
        # the ID is a 5 digit string
        series[groupColumn] = series[groupColumn].astype(str).str.zfill(5)
        # set the index
        series = series.set_index(groupColumn)
        return series

class CovidFoliumMapDEageAndGenderCounties(CovidFoliumMap):
    """
    This class will generate Choropleth maps to display Covid-19 data attributes sorted by age and gender for counties and cities in Germany. 
    """
    def __init__(self, dataDirectory = '../data'):
        """ Constructor

        Args:
            dataDirectory (str, optional): The data directory to be used for cached data. Defaults to '../data'.
        """
        # ensure that the data directory exists, meaning to create it if it is not available
        self.__dataDirectory = ensure_path_exists(dataDirectory)
        # init members
        self.__dfGeo = None
        self.__dfData = None
        self.__defaultMapOptions = CovidFoliumMap.mapOptions(mapDate=date.today(),
                                                            mapAlias = 'MapDEageAndGenderCounty',
                                                            mapLocation = [51.3, 10.5],
                                                            mapZoom = 6,
                                                            bins = None,
                                                            mapAttribute = 'Robert Koch-Institut (RKI), dl-de/by-2-0, CMBT 2022',
                                                            tooltipAttributes = ['GeoName',
                                                                                'Cases by age: 0-4', 
                                                                                'Cases by age: 5-14', 
                                                                                'Cases by age: 15-34', 
                                                                                'Cases by age: 35-59', 
                                                                                'Cases by age: 60-79', 
                                                                                'Cases by age: 80+', 
                                                                                'Percent cases by age: 0-14',
                                                                                'Percent cases by age: 15-79',
                                                                                'Percent cases by age: 80+',
                                                                                'Cases by gender: female', 
                                                                                'Cases by gender: male'])
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
        # sort it by RS (LandreisID), there is a mismatch because of the RKI Berlin approach of having separate data for the districts 
        # in one table they are sorted into the table, in the other added at the end
        geoDf = geoDf.sort_values('RS').reset_index()
        return geoDf

    def __get_covid_data(self, dfGeo):
        """ Reads the pre-processed covid-19 data from a csv file generated by the DownloadAndPreprocessRKIdata class. If the file 
        doesn't exist it will ensure that they will be created. Finally it will return a Pandas dataframe. 
        
        Returns:
            covid dataframe: the covid data for the German counties and cities or None if it can't load the file
        """
        # init the result
        df = None
        # get the date
        today = date.today()
        # the prefix of the CSV file is Y-m-d
        preFix = today.strftime('%Y-%m-%d') + "-RKI_COVID19_age_gender_per_county"
        # the target filename of the csv to be used/created
        targetFilename = self.__dataDirectory + '/' + preFix + '-db.csv'
        # check if it exist already
        if os.path.exists(targetFilename):
            print('using existing file: ' + targetFilename)
        else:
            # download and preprocess RKI data for both states and counties
            ps = DownloadAndPreprocessRKIdata(self.__dataDirectory)
            # preprocess by state
            if ps.get_age_and_gender_data_by_state() is None:
                print("Preprocessing by state failed!")
                return df
            # preprocess by county
            if ps.get_age_and_gender_data_by_county() is None:
                print("Preprocessing by county failed!")
                return df
        # now the file should exist, read it
        df = pd.read_csv(targetFilename)
        if df is None:
            return df
        # ensure RS length is 5
        df['RS'] = df['RS'].astype(str).str.zfill(5)
        # sort it by RS (LandkreisID), there is a mismatch because of the RKI Berlin approach of having separate data for the districts 
        # in one table they are sorted into the table, in the other added at the end
        df = df.sort_values('RS').reset_index()
        # the county name is in the dfgeo
        dfTmp = pd.DataFrame(dfGeo['county'])
        dfTmp.columns = ['GeoName']
        combined = pd.concat([df, dfTmp], axis=1)
        # some how it should work with a merge but that fails (maybe because the two tables haven't been sorted) TODO
        # result = df.merge(geoDf['RS', 'county'], on='RS', how='left')
        # ...and return df
        return combined
    
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

class CovidFoliumMapDEageAndGenderStates(CovidFoliumMap):
    """
    This class will generate Choropleth maps to display Covid-19 data attributes sorted by age and gender for German states.  
    """
    def __init__(self, dataDirectory = '../data'):
        """ Constructor

        Args:
            dataDirectory (str, optional): The data directory to be used for cached data. Defaults to '../data'.
        """
        # ensure that the data directory exists, meaning to create it if it is not available
        self.__dataDirectory = ensure_path_exists(dataDirectory)
        # init members
        self.__dfGeo = None
        self.__dfData = None
        self.__defaultMapOptions = CovidFoliumMap.mapOptions(mapDate=date.today(),
                                                            mapAlias = 'MapDEageAndGenderState',
                                                            mapLocation = [51.3, 10.5],
                                                            mapZoom = 6,
                                                            bins = None,
                                                            mapAttribute = 'Robert Koch-Institut (RKI), dl-de/by-2-0, CMBT 2022',
                                                            tooltipAttributes = ['GeoName',
                                                                                'Cases by age: 0-4', 
                                                                                'Cases by age: 5-14', 
                                                                                'Cases by age: 15-34', 
                                                                                'Cases by age: 35-59', 
                                                                                'Cases by age: 60-79', 
                                                                                'Cases by age: 80+', 
                                                                                'Percent cases by age: 0-14',
                                                                                'Percent cases by age: 15-79',
                                                                                'Percent cases by age: 80+',
                                                                                'Cases by gender: female', 
                                                                                'Cases by gender: male'])
        
        # check if it really exists
        if self.__dataDirectory != '':
            # get the geo JSON data frame
            self.__dfGeo = self.__get_geo_data()
            # get the covid data for all counties/cities in the geo dataframe
            if not self.get_geo_df is None:
                self.__dfData = self.__get_covid_data(self.__dfGeo)
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

    def __get_covid_data(self, dfGeo):
        """ Reads the pre-processed covid-19 data from a csv file generated by the DownloadAndPreprocessRKIdata class. If the file 
        doesn't exist it will ensure that they will be created. Finally it will return a Pandas dataframe. 
        
        Returns:
            covid dataframe: the covid data for the German counties and cities or None if it can't load the file
        """
        # init the result
        df = None
        # get the date
        today = date.today()
        # the prefix of the CSV file is Y-m-d
        preFix = today.strftime('%Y-%m-%d') + "-RKI_COVID19_age_gender_per_state"
        # the target filename of the csv to be used/created
        targetFilename = self.__dataDirectory + '/' + preFix + '-db.csv'
        # check if it exist already
        if os.path.exists(targetFilename):
            print('using existing file: ' + targetFilename)
        else:
            # download and preprocess RKI data for both states and counties
            ps = DownloadAndPreprocessRKIdata(self.__dataDirectory)
            # preprocess by state
            if ps.get_age_and_gender_data_by_state() is None:
                print("Preprocessing by state failed!")
                return df
            # preprocess by county
            if ps.get_age_and_gender_data_by_county() is None:
                print("Preprocessing by county failed!")
                return df
        # now the file should exist, read it
        df = pd.read_csv(targetFilename)
        if df is None:
            return df
        # ensure AGS length is 2
        df['AGS_TXT'] = df['AGS_TXT'].astype(str).str.zfill(2)
        
        # get the state names from the dfGeo
        dfTmp = pd.DataFrame(dfGeo['LAN_ew_GEN'])
        # rename them to fit our wording 
        dfTmp.columns = ['GeoName']
        # put them together
        combined = pd.concat([df, dfTmp], axis=1)
        # ...and return them
        return combined
   
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
