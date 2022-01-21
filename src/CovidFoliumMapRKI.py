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
from CovidFoliumMap import FoliumCovid19Map, ensure_path_exists, download_JSON_file

""" This class implements different folium maps based on the data of the RKI using access to the 
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

    - RKI API
        Great REST API to retrieve the Covid-19 data of the RKI
        https://api.corona-zahlen.org/docs/endpoints/districts.html#districts-history-recovered
        BUT:
    The RKI divides Berlin in districts and that doesn't match regular geoJSON files. Therefore you should use the RKI geoJSON for 
    German counties/cities: https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/917fc37a709542548cc3be077a786c17_0/explore to
    download 'RKI_Corona_Landkreise.geojson'
"""

class FoliumCovid19MapDEcounties(FoliumCovid19Map):
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
        self.__alias = 'MapDEcounty'
        # ensure that the data directory exists, meaning to create it if it is not available
        self.__dataDirectory = ensure_path_exists(dataDirectory)
        # check if it really exists
        if self.__dataDirectory != '':
            # get the geo JSON data frame
            self.__dfGeo = self.__get_geo_data()
            # get the covid data for all counties/cities in the geo dataframe
            if not self.get_geo_df is None:
                self.__dfData = self.__get_covid_data(self.__dfGeo)
        # pass the everything to the base class
        super().__init__(self.__dfGeo, self.__dfData, self.__dataDirectory)

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
                                                    'GeoID', 
                                                    'Cases', 
                                                    'Deaths', 
                                                    'WeeklyCases', 
                                                    'WeeklyDeaths', 
                                                    'DailyCases', 
                                                    'DailyDeaths', 
                                                    'DailyRecovered', 
                                                    'Incidence7DayPer100Kpopulation']], 
                                                    on=self.get_merge_UID(), 
                                                    how='left')
        # create the map
        map = folium.Map(attr='Robert Koch-Institut (RKI), dl-de/by-2-0, CMBT 2022', location=[51.3, 10.5], tiles=basemap, zoom_start=6)
        # the alias incl. the date
        coloredAttributeAlias = coloredAttributeAlias + ' as of ' + date.today().strftime('%Y-%m-%d')
        # the bins for the colored values
        #bins = list(combined[coloredAttribute].quantile([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]))
        # the maximum in the coloredAttribute column
        max = self.__dfData[coloredAttribute].max()
        # fixed bins
        bins = [0, 150, 300, 450, 600, 750, 900, 1050, 1200, max]
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
        tt = folium.GeoJsonTooltip(fields= ['GeoID', 
                                            'Cases', 
                                            'Deaths', 
                                            'WeeklyCases', 
                                            'WeeklyDeaths', 
                                            'DailyCases', 
                                            'DailyDeaths', 
                                            'DailyRecovered', 
                                            'Incidence7DayPer100Kpopulation'])
        # add it to the json
        tt.add_to(cp.geojson)
        # numbers and dates in the system local
        tt.localize = True
        # add a layer control to the map
        folium.LayerControl().add_to(map)
        # return the map
        return map

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

    def get_merge_UID(self):
        """
        Returns the string holding the name of the unique ID of the data and the geo dataframe that can be used to merge the two

        Returns:
            string: A string holding the name of the unique ID of the data dataframe 
        """
        return 'RS'

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
        mapArray = ['cartodbpositron',
                    'https://server.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
                    'Stamen Terrain']
        return mapArray

class FoliumCovid19MapDEstates(FoliumCovid19Map):
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
        self.__alias = 'MapDEstate'
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
                                                    'WeeklyCases', 
                                                    'WeeklyDeaths', 
                                                    'DailyCases', 
                                                    'DailyDeaths', 
                                                    'DailyRecovered', 
                                                    'Incidence7DayPer100Kpopulation',
                                                    'HospitalizationCases7']], 
                                                    on=self.get_merge_UID(), 
                                                    how='left')
        # create the map
        map = folium.Map(attr='Robert Koch-Institut (RKI), dl-de/by-2-0, CMBT 2022', location=[51.3, 10.5], tiles=basemap, zoom_start=6)
        # the alias incl. the date
        coloredAttributeAlias = coloredAttributeAlias + ' as of ' + date.today().strftime('%Y-%m-%d')
        # the bins for the colored values
        #bins = list(combined[coloredAttribute].quantile([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]))
        # the maximum in the coloredAttribute column
        max = self.__dfData[coloredAttribute].max()
        # fixed bins
        bins = [0, 150, 300, 450, 600, 750, 900, 1050, 1200, max]
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
                                            'WeeklyCases', 
                                            'WeeklyDeaths', 
                                            'DailyCases', 
                                            'DailyDeaths', 
                                            'DailyRecovered', 
                                            'Incidence7DayPer100Kpopulation',
                                            'HospitalizationCases7'])
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

    def get_merge_UID(self):
        """
        Returns the string holding the name of the unique ID of the data and the geo dataframe that can be used to merge the two

        Returns:
            string: A string holding the name of the unique ID of the data dataframe 
        """
        return 'AGS_TXT'

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
        mapArray = ['cartodbpositron',
                    'https://server.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
                    'Stamen Terrain']
        return mapArray
