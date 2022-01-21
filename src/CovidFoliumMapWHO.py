import pandas as pd
import numpy as np
import math
import os
import geopandas as gpd
import folium
from datetime import date, timedelta
from abc import ABC, abstractmethod
from pathlib import Path
from CovidCases import CovidCases
from CovidCasesWHO import CovidCasesWHO
from CovidCasesOWID import CovidCasesOWID
from CovidFoliumMap import FoliumCovid19Map, ensure_path_exists, this_or_last_weekday

""" This class implements different folium maps based on the data of the WHO using the CovidCases,
    CovidCasesWHO and in case of the World and Asia maps also the CovidCasesOWID class to map the
    Taiwan cases as well.
    The class inherits from the CovidFoliumMap class
"""

class FoliumCovid19MapEurope(FoliumCovid19Map):
    """
    This class will expose an interface to deal with Choropleth maps to display Covid-19 data attributes for German states. 
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
        self.__alias = 'MapEurope'
        # ensure that the data directory exists, meaning to create it if it is not available
        self.__dataDirectory = ensure_path_exists(dataDirectory)
        # check if it really exists
        if self.__dataDirectory != '':
            # get the geo JSON data frame
            self.__dfGeo = self.__get_geo_data()
            # get the covid data for all counties/cities in the geo dataframe
            if not self.get_geo_df is None:
                self.__dfData = self.__get_covid_data()
        # pass the everything to the base class
        super().__init__(self.__dfGeo, self.__dfData, self.__dataDirectory)

    def __get_geo_data(self):
        """ Downloads the JSON file from the RKI server if necessary and opens it to return a geoPandas dataframe. The function throws an
        exception in case of an error

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
            print('Downloading data, that might take some time...')
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

    def __get_covid_data(self):
        """ Downloads the covid-19 data from the RKI servers if necessary, caches them and opens a final csv to return a Pandas dataframe. 
        
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
        # the list of comma separated geoIDs
        countryList = whoData.get_pygal_european_geoid_string_list()
        # get the data for the country list
        df = whoData.get_data_by_geoid_string_list(countryList)
        # add the incidence
        df = whoData.add_incidence_7day_per_100Kpopulation(df)
        # get the data for last friday, on days reporting will not be good
        today = date.today()
        # take care of weekends as the data is often not available on weekends
        if (today.weekday() == 0) or (today.weekday() == 6):
            last_friday = this_or_last_weekday(date.today(), 4)
            self.__generationDate = date(last_friday.year, last_friday.month, last_friday.day)
        else:
            self.__generationDate = today - timedelta(1)
        # get the data for that date
        dfDate = df.loc[df['Date'] == pd.to_datetime(self.__generationDate)]     
        #print(dfDate.head())
        # ...and return df
        return dfDate
    
    def create_default_map(self, 
                           basemap, coloredAttribute = 'Incidence7DayPer100Kpopulation', 
                           coloredAttributeAlias = '7-day incidence per 100.000 population'):
        """ Returns a default folium map

        Args:
            basemap (str): The name of the basemap to be used. Can be one of the nice_basemaps or something different
            coloredAttribute (str, optional): [description]. Defaults to 'Incidence7DayPer100Kpopulation'.
            coloredAttributeAlias (str, optional): [description]. Defaults to '7-day incidence per 100.000 population'.
        """
        # check if we have every<thing that we need
        if (self.__dfGeo is None) or (self.__dfData is None):
            return None
        # merge geo and data dfs. ensure merging to the geoDF to keep the result a geoPandas df
        combined = self.__dfGeo.merge(self.__dfData[[self.get_merge_UID(), 
                                                    'GeoName', 
                                                    'Cases', 
                                                    'Deaths', 
                                                    'PercentDeaths',
                                                    'DailyCases', 
                                                    'DailyDeaths', 
                                                    'Incidence7DayPer100Kpopulation',
                                                    'CasesPerMillionPopulation',
                                                    'DeathsPerMillionPopulation']],
                                                    on=self.get_merge_UID(), 
                                                    how='left')
        # create the map
        map = folium.Map(attr='WHO data. Map generated by CMBT, 2022', location=[51.3, 10.5], tiles=basemap, zoom_start=4)
        # the alias incl. the date
        coloredAttributeAlias = coloredAttributeAlias + ' as of ' + date.today().strftime('%Y-%m-%d')
        # the bins for the colored values
        bins = list(combined[coloredAttribute].quantile([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]))
        # the maximum in the coloredAttribute column
        max = self.__dfData[coloredAttribute].max()
        # fixed bins
        #bins = [0, 150, 300, 450, 600, 750, 900, 1050, 1200, max]
        # build the choropleth
        cp = folium.Choropleth (geo_data=combined,
                                data=combined,
                                #data=df,
                                columns=[self.get_merge_UID(), coloredAttribute],
                                key_on='feature.properties.' + self.get_merge_UID(),
                                fill_color='YlOrRd',
                                fill_opacity=0.4,
                                line_opacity=0.4,
                                nan_fill_color='#f5f5f3',
                                legend_name=coloredAttributeAlias,
                                bins=[float(x) for x in bins],
                                highlight=True,
                                smooth_factor = 0.1)
        # give it a name
        cp.layer_name = "Covid-19 data"  
        # add it to the map
        cp.add_to(map)
        # create a tooltip for hovering
        tt = folium.GeoJsonTooltip(fields= ['GeoName', 
                                            'Cases', 
                                            'Deaths', 
                                            'PercentDeaths',
                                            'DailyCases', 
                                            'DailyDeaths', 
                                            'Incidence7DayPer100Kpopulation',
                                            'CasesPerMillionPopulation',
                                            'DeathsPerMillionPopulation'])
        # add it to the json
        tt.add_to(cp.geojson)
        # numbers and dates in the system local
        tt.localize = True
        # add a layer control to the map
        folium.LayerControl().add_to(map)
        # a legend
        #legend_html = '<div style="position: fixed; bottom: 75px; left: 50%; margin-left: -350px; width: 700px; height: 20px; z-index:9999; font-size:20px;">&nbsp; ' + 'Generated on ' + date.today().strftime('%Y-%m-%d') + '<br></div>'
        #map.get_root().html.add_child(folium.Element(legend_html))
        # return the map
        return map

    def get_merge_UID(self):
        """
        Returns the string holding the name of the unique ID of the data and the geo dataframe that can be used to merge the two

        Returns:
            string: A string holding the name of the unique ID of the data dataframe 
        """
        return 'GeoID'

    def get_map_alias(self):
        """
        Returns the string holding the name of the map that can be used to save it

        Returns:
            string: A string holding the name of the unique ID of the geo dataframe 
        """
        return self.__alias    

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

class FoliumCovid19MapAsia(FoliumCovid19Map):
    """
    This class will expose an interface to deal with Choropleth maps to display Covid-19 data attributes for German states. 
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
        self.__alias = 'MapAsia'
        # ensure that the data directory exists, meaning to create it if it is not available
        self.__dataDirectory = ensure_path_exists(dataDirectory)
        # check if it really exists
        if self.__dataDirectory != '':
            # get the geo JSON data frame
            self.__dfGeo = self.__get_geo_data()
            # get the covid data for all counties/cities in the geo dataframe
            if not self.get_geo_df is None:
                self.__dfData = self.__get_covid_data()
        # pass the everything to the base class
        super().__init__(self.__dfGeo, self.__dfData, self.__dataDirectory)

    def __get_geo_data(self):
        """ Downloads the JSON file from the RKI server if necessary and opens it to return a geoPandas dataframe. The function throws an
        exception in case of an error

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
            print('Downloading data, that might take some time...')
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

    def __get_covid_data(self):
        """ Downloads the covid-19 data from the RKI servers if necessary, caches them and opens a final csv to return a Pandas dataframe. 
        
        Returns:
            covid dataframe: the covid data for the German states or None if it can't load the file
        """
        # init the result
        df = None
        try:
            # get the latests WHO database file as a CSV
            dataFile = CovidCasesWHO.download_CSV_file()
            # get the data for the WHO countryList
            whoData = CovidCasesWHO(dataFile)
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)  
            return df
        # the list of comma separated geoIDs
        countryList = whoData.get_pygal_asian_geoid_string_list()
        # get the data for the country list
        df = whoData.get_data_by_geoid_string_list(countryList)
        # add the incidence
        df = whoData.add_incidence_7day_per_100Kpopulation(df)
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
        # the taiwan data
        dfTW = owidData.get_data_by_geoid_string_list('TW')
        # add the incidence
        dfTW = owidData.add_incidence_7day_per_100Kpopulation(dfTW)  
        # append it
        df = pd.concat([df, dfTW])  
        # get the data for last friday, on days reporting will not be good
        today = date.today()
        # take care of weekends as the data is often not available on weekends
        if (today.weekday() == 0) or (today.weekday() == 6):
            last_friday = this_or_last_weekday(date.today(), 4)
            self.__generationDate = date(last_friday.year, last_friday.month, last_friday.day)
        else:
            self.__generationDate = today - timedelta(1)
        # get the data for that date
        dfDate = df.loc[df['Date'] == pd.to_datetime(self.__generationDate)]      
        #print(dfDate.head())
        # ...and return df
        return dfDate
    
    def create_default_map(self, 
                           basemap, coloredAttribute = 'Incidence7DayPer100Kpopulation', 
                           coloredAttributeAlias = '7-day incidence per 100.000 population'):
        """ Returns a default folium map

        Args:
            basemap (str): The name of the basemap to be used. Can be one of the nice_basemaps or something different
            coloredAttribute (str, optional): [description]. Defaults to 'Incidence7DayPer100Kpopulation'.
            coloredAttributeAlias (str, optional): [description]. Defaults to '7-day incidence per 100.000 population'.
        """
        # check if we have every<thing that we need
        if (self.__dfGeo is None) or (self.__dfData is None):
            return None
        # merge geo and data dfs. ensure merging to the geoDF to keep the result a geoPandas df
        combined = self.__dfGeo.merge(self.__dfData[[self.get_merge_UID(), 
                                                    'GeoName', 
                                                    'Cases', 
                                                    'Deaths', 
                                                    'PercentDeaths',
                                                    'DailyCases', 
                                                    'DailyDeaths', 
                                                    'Incidence7DayPer100Kpopulation',
                                                    'CasesPerMillionPopulation',
                                                    'DeathsPerMillionPopulation']],
                                                    on=self.get_merge_UID(), 
                                                    how='left')
        # create the map
        map = folium.Map(attr='WHO data. Map genrated by CMBT, 2022', location=[23, 92], tiles=basemap, zoom_start=4)
        # the alias incl. the date
        coloredAttributeAlias = coloredAttributeAlias + ' as of ' + date.today().strftime('%Y-%m-%d')
        # the bins for the colored values
        bins = list(combined[coloredAttribute].quantile([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]))
        # the maximum in the coloredAttribute column
        max = self.__dfData[coloredAttribute].max()
        # fixed bins
        #bins = [0, 150, 300, 450, 600, 750, 900, 1050, 1200, max]
        # build the choropleth
        cp = folium.Choropleth (geo_data=combined,
                                data=combined,
                                #data=df,
                                columns=[self.get_merge_UID(), coloredAttribute],
                                key_on='feature.properties.' + self.get_merge_UID(),
                                fill_color='YlOrRd',
                                fill_opacity=0.4,
                                line_opacity=0.4,
                                nan_fill_color='#f5f5f3',
                                legend_name=coloredAttributeAlias,
                                bins=[float(x) for x in bins],
                                highlight=True,
                                smooth_factor = 0.1)
        # give it a name
        cp.layer_name = "Covid-19 data"  
        # add it to the map
        cp.add_to(map)
        # create a tooltip for hovering
        tt = folium.GeoJsonTooltip(fields= ['GeoName', 
                                            'Cases', 
                                            'Deaths', 
                                            'PercentDeaths',
                                            'DailyCases', 
                                            'DailyDeaths', 
                                            'Incidence7DayPer100Kpopulation',
                                            'CasesPerMillionPopulation',
                                            'DeathsPerMillionPopulation'])
        # add it to the json
        tt.add_to(cp.geojson)
        # numbers and dates in the system local
        tt.localize = True
        # add a layer control to the map
        folium.LayerControl().add_to(map)
        # a legend
        #legend_html = '<div style="position: fixed; bottom: 75px; left: 50%; margin-left: -350px; width: 700px; height: 20px; z-index:9999; font-size:20px;">&nbsp; ' + 'Generated on ' + date.today().strftime('%Y-%m-%d') + '<br></div>'
        #map.get_root().html.add_child(folium.Element(legend_html))
        # return the map
        return map

    def get_merge_UID(self):
        """
        Returns the string holding the name of the unique ID of the data and the geo dataframe that can be used to merge the two

        Returns:
            string: A string holding the name of the unique ID of the data dataframe 
        """
        return 'GeoID'

    def get_map_alias(self):
        """
        Returns the string holding the name of the map that can be used to save it

        Returns:
            string: A string holding the name of the unique ID of the geo dataframe 
        """
        return self.__alias  

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

class FoliumCovid19MapAmerica(FoliumCovid19Map):
    """
    This class will expose an interface to deal with Choropleth maps to display Covid-19 data attributes for German states. 
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
        self.__alias = 'MapAmerica'
        # ensure that the data directory exists, meaning to create it if it is not available
        self.__dataDirectory = ensure_path_exists(dataDirectory)
        # check if it really exists
        if self.__dataDirectory != '':
            # get the geo JSON data frame
            self.__dfGeo = self.__get_geo_data()
            # get the covid data for all counties/cities in the geo dataframe
            if not self.get_geo_df is None:
                self.__dfData = self.__get_covid_data()
        # pass the everything to the base class
        super().__init__(self.__dfGeo, self.__dfData, self.__dataDirectory)

    def __get_geo_data(self):
        """ Downloads the JSON file from the RKI server if necessary and opens it to return a geoPandas dataframe. The function throws an
        exception in case of an error

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
            print('Downloading data, that might take some time...')
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

    def __get_covid_data(self):
        """ Downloads the covid-19 data from the RKI servers if necessary, caches them and opens a final csv to return a Pandas dataframe. 
        
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
        # the list of comma separated geoIDs
        countryList = whoData.get_pygal_american_geoid_string_list()
        # get the data for the country list
        df = whoData.get_data_by_geoid_string_list(countryList)
        # add the incidence
        df = whoData.add_incidence_7day_per_100Kpopulation(df)
        # get the data for last friday, on days reporting will not be good
        today = date.today()
        # take care of weekends as the data is often not available on weekends
        if (today.weekday() == 0) or (today.weekday() == 6):
            last_friday = this_or_last_weekday(date.today(), 4)
            self.__generationDate = date(last_friday.year, last_friday.month, last_friday.day)
        else:
            self.__generationDate = today - timedelta(1)
        # get the data for that date
        dfDate = df.loc[df['Date'] == pd.to_datetime(self.__generationDate)]       
        #print(dfDate.head())
        # ...and return df
        return dfDate
    
    def create_default_map(self, 
                           basemap, coloredAttribute = 'Incidence7DayPer100Kpopulation', 
                           coloredAttributeAlias = '7-day incidence per 100.000 population'):
        """ Returns a default folium map

        Args:
            basemap (str): The name of the basemap to be used. Can be one of the nice_basemaps or something different
            coloredAttribute (str, optional): [description]. Defaults to 'Incidence7DayPer100Kpopulation'.
            coloredAttributeAlias (str, optional): [description]. Defaults to '7-day incidence per 100.000 population'.
        """
        # check if we have every<thing that we need
        if (self.__dfGeo is None) or (self.__dfData is None):
            return None
        # merge geo and data dfs. ensure merging to the geoDF to keep the result a geoPandas df
        combined = self.__dfGeo.merge(self.__dfData[[self.get_merge_UID(), 
                                                    'GeoName', 
                                                    'Cases', 
                                                    'Deaths', 
                                                    'PercentDeaths',
                                                    'DailyCases', 
                                                    'DailyDeaths', 
                                                    'Incidence7DayPer100Kpopulation',
                                                    'CasesPerMillionPopulation',
                                                    'DeathsPerMillionPopulation']],
                                                    on=self.get_merge_UID(), 
                                                    how='left')
        # create the map
        map = folium.Map(attr='WHO data. Map generated by CMBT, 2022', location=[16, -86], tiles=basemap, zoom_start=3)
        # the alias incl. the date
        coloredAttributeAlias = coloredAttributeAlias + ' as of ' + date.today().strftime('%Y-%m-%d')
        # the bins for the colored values
        bins = list(combined[coloredAttribute].quantile([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]))
        # the maximum in the coloredAttribute column
        max = self.__dfData[coloredAttribute].max()
        # fixed bins
        #bins = [0, 150, 300, 450, 600, 750, 900, 1050, 1200, max]
        # build the choropleth
        cp = folium.Choropleth (geo_data=combined,
                                data=combined,
                                #data=df,
                                columns=[self.get_merge_UID(), coloredAttribute],
                                key_on='feature.properties.' + self.get_merge_UID(),
                                fill_color='YlOrRd',
                                fill_opacity=0.4,
                                line_opacity=0.4,
                                nan_fill_color='#f5f5f3',
                                legend_name=coloredAttributeAlias,
                                bins=[float(x) for x in bins],
                                highlight=True,
                                smooth_factor = 0.1)
        # give it a name
        cp.layer_name = "Covid-19 data"  
        # add it to the map
        cp.add_to(map)
        # create a tooltip for hovering
        tt = folium.GeoJsonTooltip(fields= ['GeoName', 
                                            'Cases', 
                                            'Deaths', 
                                            'PercentDeaths',
                                            'DailyCases', 
                                            'DailyDeaths', 
                                            'Incidence7DayPer100Kpopulation',
                                            'CasesPerMillionPopulation',
                                            'DeathsPerMillionPopulation'])
        # add it to the json
        tt.add_to(cp.geojson)
        # numbers and dates in the system local
        tt.localize = True
        # add a layer control to the map
        folium.LayerControl().add_to(map)
        # a legend
        #legend_html = '<div style="position: fixed; bottom: 75px; left: 50%; margin-left: -350px; width: 700px; height: 20px; z-index:9999; font-size:20px;">&nbsp; ' + 'Generated on ' + date.today().strftime('%Y-%m-%d') + '<br></div>'
        #map.get_root().html.add_child(folium.Element(legend_html))
        # return the map
        return map

    def get_merge_UID(self):
        """
        Returns the string holding the name of the unique ID of the data and the geo dataframe that can be used to merge the two

        Returns:
            string: A string holding the name of the unique ID of the data dataframe 
        """
        return 'GeoID'

    def get_map_alias(self):
        """
        Returns the string holding the name of the map that can be used to save it

        Returns:
            string: A string holding the name of the unique ID of the geo dataframe 
        """
        return self.__alias  

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

class FoliumCovid19MapOceania(FoliumCovid19Map):
    """
    This class will expose an interface to deal with Choropleth maps to display Covid-19 data attributes for German states. 
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
        self.__alias = 'MapOceania'
        # ensure that the data directory exists, meaning to create it if it is not available
        self.__dataDirectory = ensure_path_exists(dataDirectory)
        # check if it really exists
        if self.__dataDirectory != '':
            # get the geo JSON data frame
            self.__dfGeo = self.__get_geo_data()
            # get the covid data for all counties/cities in the geo dataframe
            if not self.get_geo_df is None:
                self.__dfData = self.__get_covid_data()
        # pass the everything to the base class
        super().__init__(self.__dfGeo, self.__dfData, self.__dataDirectory)

    def __get_geo_data(self):
        """ Downloads the JSON file from the RKI server if necessary and opens it to return a geoPandas dataframe. The function throws an
        exception in case of an error

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
            print('Downloading data, that might take some time...')
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

    def __get_covid_data(self):
        """ Downloads the covid-19 data from the RKI servers if necessary, caches them and opens a final csv to return a Pandas dataframe. 
        
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
        # the list of comma separated geoIDs
        countryList = whoData.get_pygal_oceania_geoid_string_list()
        # get the data for the country list
        df = whoData.get_data_by_geoid_string_list(countryList)
        # add the incidence
        df = whoData.add_incidence_7day_per_100Kpopulation(df)
        # get the data for last friday, on days reporting will not be good
        today = date.today()
        # take care of weekends as the data is often not available on weekends
        if (today.weekday() == 0) or (today.weekday() == 6):
            last_friday = this_or_last_weekday(date.today(), 4)
            self.__generationDate = date(last_friday.year, last_friday.month, last_friday.day)
        else:
            self.__generationDate = today - timedelta(1)
        # get the data for that date
        dfDate = df.loc[df['Date'] == pd.to_datetime(self.__generationDate)]       
        #print(dfDate.head())
        # ...and return df
        return dfDate
    
    def create_default_map(self, 
                           basemap, coloredAttribute = 'Incidence7DayPer100Kpopulation', 
                           coloredAttributeAlias = '7-day incidence per 100.000 population'):
        """ Returns a default folium map

        Args:
            basemap (str): The name of the basemap to be used. Can be one of the nice_basemaps or something different
            coloredAttribute (str, optional): [description]. Defaults to 'Incidence7DayPer100Kpopulation'.
            coloredAttributeAlias (str, optional): [description]. Defaults to '7-day incidence per 100.000 population'.
        """
        # check if we have every<thing that we need
        if (self.__dfGeo is None) or (self.__dfData is None):
            return None
        # merge geo and data dfs. ensure merging to the geoDF to keep the result a geoPandas df
        combined = self.__dfGeo.merge(self.__dfData[[self.get_merge_UID(), 
                                                    'GeoName', 
                                                    'Cases', 
                                                    'Deaths', 
                                                    'PercentDeaths',
                                                    'DailyCases', 
                                                    'DailyDeaths', 
                                                    'Incidence7DayPer100Kpopulation',
                                                    'CasesPerMillionPopulation',
                                                    'DeathsPerMillionPopulation']],
                                                    on=self.get_merge_UID(), 
                                                    how='left')
        # create the map
        map = folium.Map(attr='WHO data. Map generated by CMBT, 2022', location=[-26, 147], tiles=basemap, zoom_start=4)
        # the alias incl. the date
        coloredAttributeAlias = coloredAttributeAlias + ' as of ' + date.today().strftime('%Y-%m-%d')
        # the bins for the colored values
        bins = list(combined[coloredAttribute].quantile([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]))
        # the maximum in the coloredAttribute column
        max = self.__dfData[coloredAttribute].max()
        # fixed bins
        #bins = [0, 150, 300, 450, 600, 750, 900, 1050, 1200, max]
        # build the choropleth
        cp = folium.Choropleth (geo_data=combined,
                                data=combined,
                                #data=df,
                                columns=[self.get_merge_UID(), coloredAttribute],
                                key_on='feature.properties.' + self.get_merge_UID(),
                                fill_color='YlOrRd',
                                fill_opacity=0.4,
                                line_opacity=0.4,
                                nan_fill_color='#f5f5f3',
                                legend_name=coloredAttributeAlias,
                                bins=[float(x) for x in bins],
                                highlight=True,
                                smooth_factor = 0.1)
        # give it a name
        cp.layer_name = "Covid-19 data"  
        # add it to the map
        cp.add_to(map)
        # create a tooltip for hovering
        tt = folium.GeoJsonTooltip(fields= ['GeoName', 
                                            'Cases', 
                                            'Deaths', 
                                            'PercentDeaths',
                                            'DailyCases', 
                                            'DailyDeaths', 
                                            'Incidence7DayPer100Kpopulation',
                                            'CasesPerMillionPopulation',
                                            'DeathsPerMillionPopulation'])
        # add it to the json
        tt.add_to(cp.geojson)
        # numbers and dates in the system local
        tt.localize = True
        # add a layer control to the map
        folium.LayerControl().add_to(map)
        # a legend
        #legend_html = '<div style="position: fixed; bottom: 75px; left: 50%; margin-left: -350px; width: 700px; height: 20px; z-index:9999; font-size:20px;">&nbsp; ' + 'Generated on ' + date.today().strftime('%Y-%m-%d') + '<br></div>'
        #map.get_root().html.add_child(folium.Element(legend_html))
        # return the map
        return map

    def get_merge_UID(self):
        """
        Returns the string holding the name of the unique ID of the data and the geo dataframe that can be used to merge the two

        Returns:
            string: A string holding the name of the unique ID of the data dataframe 
        """
        return 'GeoID'

    def get_map_alias(self):
        """
        Returns the string holding the name of the map that can be used to save it

        Returns:
            string: A string holding the name of the unique ID of the geo dataframe 
        """
        return self.__alias  

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

class FoliumCovid19MapAfrica(FoliumCovid19Map):
    """
    This class will expose an interface to deal with Choropleth maps to display Covid-19 data attributes for German states. 
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
        self.__alias = 'MapAfrica'
        # ensure that the data directory exists, meaning to create it if it is not available
        self.__dataDirectory = ensure_path_exists(dataDirectory)
        # check if it really exists
        if self.__dataDirectory != '':
            # get the geo JSON data frame
            self.__dfGeo = self.__get_geo_data()
            # get the covid data for all counties/cities in the geo dataframe
            if not self.get_geo_df is None:
                self.__dfData = self.__get_covid_data()
        # pass the everything to the base class
        super().__init__(self.__dfGeo, self.__dfData, self.__dataDirectory)

    def __get_geo_data(self):
        """ Downloads the JSON file from the RKI server if necessary and opens it to return a geoPandas dataframe. The function throws an
        exception in case of an error

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
            print('Downloading data, that might take some time...')
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

    def __get_covid_data(self):
        """ Downloads the covid-19 data from the RKI servers if necessary, caches them and opens a final csv to return a Pandas dataframe. 
        
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
        # the list of comma separated geoIDs
        countryList = whoData.get_pygal_african_geoid_string_list()
        # get the data for the country list
        df = whoData.get_data_by_geoid_string_list(countryList)
        # add the incidence
        df = whoData.add_incidence_7day_per_100Kpopulation(df)
        # get the data for last friday, on days reporting will not be good
        today = date.today()
        # take care of weekends as the data is often not available on weekends
        if (today.weekday() == 0) or (today.weekday() == 6):
            last_friday = this_or_last_weekday(date.today(), 4)
            self.__generationDate = date(last_friday.year, last_friday.month, last_friday.day)
        else:
            self.__generationDate = today - timedelta(1)
        # get the data for that date
        dfDate = df.loc[df['Date'] == pd.to_datetime(self.__generationDate)]      
        #print(dfDate.head())
        # ...and return df
        return dfDate
    
    def create_default_map(self, 
                           basemap, coloredAttribute = 'Incidence7DayPer100Kpopulation', 
                           coloredAttributeAlias = '7-day incidence per 100.000 population'):
        """ Returns a default folium map

        Args:
            basemap (str): The name of the basemap to be used. Can be one of the nice_basemaps or something different
            coloredAttribute (str, optional): [description]. Defaults to 'Incidence7DayPer100Kpopulation'.
            coloredAttributeAlias (str, optional): [description]. Defaults to '7-day incidence per 100.000 population'.
        """
        # check if we have every<thing that we need
        if (self.__dfGeo is None) or (self.__dfData is None):
            return None
        # merge geo and data dfs. ensure merging to the geoDF to keep the result a geoPandas df
        combined = self.__dfGeo.merge(self.__dfData[[self.get_merge_UID(), 
                                                    'GeoName', 
                                                    'Cases', 
                                                    'Deaths', 
                                                    'PercentDeaths',
                                                    'DailyCases', 
                                                    'DailyDeaths', 
                                                    'Incidence7DayPer100Kpopulation',
                                                    'CasesPerMillionPopulation',
                                                    'DeathsPerMillionPopulation']],
                                                    on=self.get_merge_UID(), 
                                                    how='left')
        # create the map
        map = folium.Map(attr='WHO data. Map generated by CMBT, 2022', location=[5, 19], tiles=basemap, zoom_start=4)
        # the alias incl. the date
        coloredAttributeAlias = coloredAttributeAlias + ' as of ' + date.today().strftime('%Y-%m-%d')
        # the bins for the colored values
        bins = list(combined[coloredAttribute].quantile([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]))
        # the maximum in the coloredAttribute column
        max = self.__dfData[coloredAttribute].max()
        # fixed bins
        #bins = [0, 150, 300, 450, 600, 750, 900, 1050, 1200, max]
        # build the choropleth
        cp = folium.Choropleth (geo_data=combined,
                                data=combined,
                                #data=df,
                                columns=[self.get_merge_UID(), coloredAttribute],
                                key_on='feature.properties.' + self.get_merge_UID(),
                                fill_color='YlOrRd',
                                fill_opacity=0.4,
                                line_opacity=0.4,
                                nan_fill_color='#f5f5f3',
                                legend_name=coloredAttributeAlias,
                                bins=[float(x) for x in bins],
                                highlight=True,
                                smooth_factor = 0.1)
        # give it a name
        cp.layer_name = "Covid-19 data"  
        # add it to the map
        cp.add_to(map)
        # create a tooltip for hovering
        tt = folium.GeoJsonTooltip(fields= ['GeoName', 
                                            'Cases', 
                                            'Deaths', 
                                            'PercentDeaths',
                                            'DailyCases', 
                                            'DailyDeaths', 
                                            'Incidence7DayPer100Kpopulation',
                                            'CasesPerMillionPopulation',
                                            'DeathsPerMillionPopulation'])
        # add it to the json
        tt.add_to(cp.geojson)
        # numbers and dates in the system local
        tt.localize = True
        # add a layer control to the map
        folium.LayerControl().add_to(map)
        # a legend
        #legend_html = '<div style="position: fixed; bottom: 75px; left: 50%; margin-left: -350px; width: 700px; height: 20px; z-index:9999; font-size:20px;">&nbsp; ' + 'Generated on ' + date.today().strftime('%Y-%m-%d') + '<br></div>'
        #map.get_root().html.add_child(folium.Element(legend_html))
        # return the map
        return map

    def get_merge_UID(self):
        """
        Returns the string holding the name of the unique ID of the data and the geo dataframe that can be used to merge the two

        Returns:
            string: A string holding the name of the unique ID of the data dataframe 
        """
        return 'GeoID'

    def get_map_alias(self):
        """
        Returns the string holding the name of the map that can be used to save it

        Returns:
            string: A string holding the name of the unique ID of the geo dataframe 
        """
        return self.__alias  

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

class FoliumCovid19MapWorld(FoliumCovid19Map):
    """
    This class will expose an interface to deal with Choropleth maps to display Covid-19 data attributes for German states. 
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
        self.__alias = 'MapWorld'
        # ensure that the data directory exists, meaning to create it if it is not available
        self.__dataDirectory = ensure_path_exists(dataDirectory)
        # check if it really exists
        if self.__dataDirectory != '':
            # get the geo JSON data frame
            self.__dfGeo = self.__get_geo_data()
            # get the covid data for all counties/cities in the geo dataframe
            if not self.get_geo_df is None:
                self.__dfData = self.__get_covid_data()
        # pass the everything to the base class
        super().__init__(self.__dfGeo, self.__dfData, self.__dataDirectory)

    def __get_geo_data(self):
        """ Downloads the JSON file from the RKI server if necessary and opens it to return a geoPandas dataframe. The function throws an
        exception in case of an error

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
            print('Downloading data, that might take some time...')
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

    def __get_covid_data(self):
        """ Downloads the covid-19 data from the RKI servers if necessary, caches them and opens a final csv to return a Pandas dataframe. 
        
        Returns:
            covid dataframe: the covid data for the German states or None if it can't load the file
        """
        # init the result
        df = None
        try:
            # get the latests WHO database file as a CSV
            dataFile = CovidCasesWHO.download_CSV_file()
            # get the data for the WHO countryList
            whoData = CovidCasesWHO(dataFile)
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)  
            return df
        # the list of comma separated geoIDs
        countryList = whoData.get_pygal_asian_geoid_string_list()  + ',' + \
                      whoData.get_pygal_european_geoid_string_list()  + ',' + \
                      whoData.get_pygal_american_geoid_string_list()  + ',' + \
                      whoData.get_pygal_african_geoid_string_list()  + ',' + \
                      whoData.get_pygal_oceania_geoid_string_list()
        # get the data for the country list
        df = whoData.get_data_by_geoid_string_list(countryList)
        # add the incidence
        df = whoData.add_incidence_7day_per_100Kpopulation(df)
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
        # the taiwan data
        dfTW = owidData.get_data_by_geoid_string_list('TW')
        # add the incidence
        dfTW = owidData.add_incidence_7day_per_100Kpopulation(dfTW)  
        # append it
        df = pd.concat([df, dfTW])  
        # get the data for last friday, on days reporting will not be good
        today = date.today()
        # take care of weekends as the data is often not available on weekends
        if (today.weekday() == 0) or (today.weekday() == 6):
            last_friday = this_or_last_weekday(date.today(), 4)
            self.__generationDate = date(last_friday.year, last_friday.month, last_friday.day)
        else:
            self.__generationDate = today - timedelta(1)
        # get the data for that date
        dfDate = df.loc[df['Date'] == pd.to_datetime(self.__generationDate)]      
        #print(dfDate.head())
        # ...and return df
        return dfDate
    
    def create_default_map(self, 
                           basemap, coloredAttribute = 'Incidence7DayPer100Kpopulation', 
                           coloredAttributeAlias = '7-day incidence per 100.000 population'):
        """ Returns a default folium map

        Args:
            basemap (str): The name of the basemap to be used. Can be one of the nice_basemaps or something different
            coloredAttribute (str, optional): [description]. Defaults to 'Incidence7DayPer100Kpopulation'.
            coloredAttributeAlias (str, optional): [description]. Defaults to '7-day incidence per 100.000 population'.
        """
        # check if we have every<thing that we need
        if (self.__dfGeo is None) or (self.__dfData is None):
            return None
        # merge geo and data dfs. ensure merging to the geoDF to keep the result a geoPandas df
        combined = self.__dfGeo.merge(self.__dfData[[self.get_merge_UID(), 
                                                    'GeoName', 
                                                    'Cases', 
                                                    'Deaths', 
                                                    'PercentDeaths',
                                                    'DailyCases', 
                                                    'DailyDeaths', 
                                                    'Incidence7DayPer100Kpopulation',
                                                    'CasesPerMillionPopulation',
                                                    'DeathsPerMillionPopulation']],
                                                    on=self.get_merge_UID(), 
                                                    how='left')
        # create the map
        map = folium.Map(attr='WHO data. Map generated by CMBT, 2022', location=[15, 0], tiles=basemap, zoom_start=2)
        # the alias incl. the date
        coloredAttributeAlias = coloredAttributeAlias + ' as of ' + date.today().strftime('%Y-%m-%d')
        # the bins for the colored values
        bins = list(combined[coloredAttribute].quantile([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]))
        # the maximum in the coloredAttribute column
        max = self.__dfData[coloredAttribute].max()
        # fixed bins
        #bins = [0, 150, 300, 450, 600, 750, 900, 1050, 1200, max]
        # build the choropleth
        cp = folium.Choropleth (geo_data=combined,
                                data=combined,
                                #data=df,
                                columns=[self.get_merge_UID(), coloredAttribute],
                                key_on='feature.properties.' + self.get_merge_UID(),
                                fill_color='YlOrRd',
                                fill_opacity=0.4,
                                line_opacity=0.4,
                                nan_fill_color='#f5f5f3',
                                legend_name=coloredAttributeAlias,
                                bins=[float(x) for x in bins],
                                highlight=True,
                                smooth_factor = 0.1)
        # give it a name
        cp.layer_name = "Covid-19 data"  
        # add it to the map
        cp.add_to(map)
        # create a tooltip for hovering
        tt = folium.GeoJsonTooltip(fields= ['GeoName', 
                                            'Cases', 
                                            'Deaths', 
                                            'PercentDeaths',
                                            'DailyCases', 
                                            'DailyDeaths', 
                                            'Incidence7DayPer100Kpopulation',
                                            'CasesPerMillionPopulation',
                                            'DeathsPerMillionPopulation'])
        # add it to the json
        tt.add_to(cp.geojson)
        # numbers and dates in the system local
        tt.localize = True
        # add a layer control to the map
        folium.LayerControl().add_to(map)
        # a legend
        #legend_html = '<div style="position: fixed; bottom: 75px; left: 50%; margin-left: -350px; width: 700px; height: 20px; z-index:9999; font-size:20px;">&nbsp; ' + 'Generated on ' + date.today().strftime('%Y-%m-%d') + '<br></div>'
        #map.get_root().html.add_child(folium.Element(legend_html))
        # return the map
        return map

    def get_merge_UID(self):
        """
        Returns the string holding the name of the unique ID of the data and the geo dataframe that can be used to merge the two

        Returns:
            string: A string holding the name of the unique ID of the data dataframe 
        """
        return 'GeoID'

    def get_map_alias(self):
        """
        Returns the string holding the name of the map that can be used to save it

        Returns:
            string: A string holding the name of the unique ID of the geo dataframe 
        """
        return self.__alias  

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
