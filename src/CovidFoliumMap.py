import pandas as pd
import numpy as np
import os
import geopandas as gpd
import requests
import json
import datetime
from abc import ABC, abstractmethod
from pathlib import Path

""" This abstract class acts as a base class for other classes that implement different folium maps based on different data 
    sources. Here are some usefull links:

    - Geodata visualization 
        folium: https://python-visualization.github.io/folium/
        Different basemaps are available on https://leaflet-extras.github.io/leaflet-providers/preview/
"""


def ensure_path_exists(thePath):
    """ The function checks of the given relative or absolute path exists and if not it will try to create it. If that fails
    the function will throw an exception

    Args:
        thePath (string): the given relative or absolute path

    Returns:
        string: The absolute path that will exists or an empty string if it failed to create it
    """
    # if the data directory is given as an absolute path it's all fine
    if Path(thePath).is_absolute():
        result = thePath
    else:
        # get path to the directory of this file
        try:
            # check if it is running in jupyter, it will throw if not running in jupyter
            get_ipython
            # the absolute directory of this python file
            currentDirectory = os.path.dirname(os.path.abspath(os.path.abspath('')))
        except:
            # the absolute directory of this python file
            currentDirectory = os.path.dirname(os.path.abspath(__file__))
        # the directory is not given as an absolute path so add it to the current directory
        result = currentDirectory + '/' + thePath
    if not os.path.exists(result):
        try:
            os.makedirs(result)
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)  
            return ''
    return result
    
def download_JSON_file(endpoint, filename):
    """ The function downloads a JSON file from the given endpoint and stores it in a file 
    of the given filename. If the directory doesn't exist it will be created. The function 
    throws an exception in case of an error

    Args:
        endpoint (string): the full endpoint that is referring to a JSON file
        filename (string): the full filename of the file to be created

    Raises:
        IOError: In case it can't save the data
    """
    # contact the server
    res = requests.get(endpoint)
    # check if there was a response
    if res.ok:
        # get the json
        res = res.json()
    else:
        # raise an exception
        res.raise_for_status()
    try:
        # create the directory if it doesn't exist 
        path = os.path.dirname(filename)
        if not os.path.exists(path):
            os.makedirs(filename)
        # write it to the file
        with open (filename, 'w', encoding='utf-8') as f:
            # use dumps as we don't care about formatting
            f.write(json.dumps(res) + "\n")
    except:
        msg = 'Error writing file ' + filename
        raise IOError(msg)      

def this_or_last_weekday(the_date, the_weekday):
    """ Retruns the given date of the last weekday or the given date if that has the right weekday.
        Example: the_date = 2022.01.19 that was a Wednesday (weekday=2), 
                 if being called with the_weekday=4 (Friday) the function will return 2022.01.14
                 if being called with the_weekday=2 (Wednesday) the function will return 2022.01.19

    Args:
        the_date (Date): the date to be checked
        the_weekday (int): the day of the week to get the date for ranging from 0 (Monday) to 6 (Sunday)

    Returns:
        DateTime: The date of the weekday a week ago or at the given date if it is already the proper weekday
    """
    # maybe it is the_date that is the right weekday
    if the_date.weekday() == the_weekday:
        return the_date
    # 9:00 on that date
    the_time = datetime.datetime(the_date.year, the_date.month, the_date.day, 9, 0)
    # get the same day one week ago at 9:00
    last_weekday = (the_time.date() -
                    datetime.timedelta(days=the_time.weekday()) +
                    datetime.timedelta(days=the_weekday, weeks=-1))
    last_weekday_at_9 = datetime.datetime.combine(last_weekday, datetime.time(9))

    # if today is also the_weekday but after 9:00 change to the current date
    one_week = datetime.timedelta(weeks=1)
    if the_time - last_weekday_at_9 >= one_week:
        last_weekday_at_9 += one_week
    return last_weekday_at_9
      
class FoliumCovid19Map(ABC):
    """
    This abstract base class will expose an interface to deal with Choropleth maps to display Covid-19 data attributes. It does this  
    by providing access to a pandas geoJSON dataframe and a data dataframe. It also also provides methods to generate a default map.
    """
    def __init__(self, dfGeo, dfData, dataDirectory):
        """
        The constructor takes two dataframes. One containing geoJSON information and a second containing CoVid-19 data. 

        Args:
            dfGeo (dataframe): The geoPandas dataframe containing geometry information of the countries and regions of the world.  
            dfData (dataframe): The 'regular' Pandas dataframe containing Covid-19 data to be shown on the map
        """
        # keep the data frames
        self.__dfGeo = dfGeo
        self.__dfData = dfData,
        self.__dataDirectory = dataDirectory

    def get_geo_df(self):
        """Returns the geoPandas data frame
        
        Args:
            -

        Returns:
            DataFrame: The geoPandas data frame containing geoJSON geometries
        """
        return self.__dfGeo
    
    def get_data_df(self):
        """Returns the geoPandas data frame
        
        Args:
            -

        Returns:
            DataFrame: The Pandas data frame containing Covid-19 data
        """
        return self.__dfData

    def get_data_directory(self):
        """Returns the data directory as a string
        
        Args:
            -

        Returns:
            DataDirectory: A string pointing to the absolute data directory path
        """
        return self.__dataDirectory

    @abstractmethod
    def create_default_map(self, 
                           basemap, coloredAttribute = 'Incidence7DayPer100Kpopulation', 
                           coloredAttributeAlias = '7-day incidence per 100.000 population'):
        """ Returns a default folium map

        Args:
            basemap (str): The name of the basemap to be used. Can be one of the nice_basemaps or something different
            coloredAttribute (str, optional): [description]. Defaults to 'Incidence7DayPer100Kpopulation'.
            coloredAttributeAlias (str, optional): [description]. Defaults to '7-day incidence per 100.000 population'.
        """
        pass 

    @abstractmethod
    def get_merge_UID(self):
        """
        Returns the string holding the name of the unique ID of the data and the geo dataframe that can be used to merge the two

        Returns:
            string: A string holding the name of the unique ID of the data dataframe 
        """
        pass 

    @abstractmethod
    def get_map_alias(self):
        """
        Returns the string holding the name of the map that can be used to save it 

        Returns:
            string: A string holding the name of the unique ID of the geo dataframe 
        """
        pass 

    @abstractmethod
    def get_nice_basemaps(self):
        """
        Returns an array of strings referring to nice basemaps for the specific region. At least one basemaps should be given and 
        the preferred basemap should be basemap[0]

        Returns:
            string: A array of strings referring to nice basemaps 
        """
        pass 
