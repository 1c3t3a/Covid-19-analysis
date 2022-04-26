import pandas as pd
import numpy as np
import os
import geopandas as gpd
import requests
import json
import datetime
from abc import ABC, abstractmethod
from pathlib import Path
import folium
from typing import List
from dataclasses import dataclass, field
from datetime import date, timedelta

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
       
class CovidFoliumMap(ABC):
    """
    This abstract base class will expose an interface to deal with Choropleth maps to display Covid-19 data attributes. It does this  
    by providing access to a pandas geoJSON dataframe and a data dataframe. It also  provides methods to generate a default map.
    """
    def __init__(self, dataDirectory):
        """
        The constructor takes two dataframes. One containing geoJSON information and a second containing CoVid-19 data. 

        Args:
            dataDirectory (str): The path to a directory to store temporary data
        """
        # keep the data directory
        self.__dataDirectory = dataDirectory

    @dataclass
    class mapOptions:
        """ Somehow a struct holding information about the map such as location of the alias, date, center, etc.
        """
        mapAlias: str = field(default_factory=lambda : '')
        """ An alias name of the map that can be used as a filename to save the map
        """
        #ingredients: List = field(default_factory=lambda: ['dow', 'tomatoes'])
        tooltipAttributes: List = field(default_factory=lambda : [])
        """ A list of data attributes of the data df that should appear in the tooltip when moving the mouse over the map
        """
        mapAttribute: str = field(default_factory=lambda : '')
        """ The string that should appear in the leaflet of the map
        """
        mapLocation: List = field(default_factory=lambda : [])
        """ The initial center of the map 
        """
        mapZoom: int = 4
        """ The initial zoom level of the map
        """
        mapDate: date = date.today
        """ The date of the data shown in the map
        """
        bins: List[float] = field(default_factory=lambda : [])
        """ A list of values representing the colour bins (Folium supports up to 10 bins), or none to calculate default bins

        Returns:
            mapOptions: The struct of options
        """

    def create_default_map(self, 
                           basemap, 
                           coloredAttribute = 'Incidence7DayPer100Kpopulation', 
                           coloredAttributeAlias = '7-day incidence per 100.000 population'):
        """ Returns a default folium map

        Args:
            basemap (str): The name of the basemap to be used. Can be one of the nice_basemaps or something different
            coloredAttribute (str, optional): [description]. Defaults to 'Incidence7DayPer100Kpopulation'.
            coloredAttributeAlias (str, optional): [description]. Defaults to '7-day incidence per 100.000 population'.
        """
        # get the map options
        dfGeo = self.get_geo_df()
        dfData = self.get_data_df()
        mapOptions = self.get_default_map_options()
        # check if we have every<thing that we need
        if (dfGeo is None) or (dfData is None):
            return None
        # merge geo and data dfs. ensure merging to the geoDF to keep the result a geoPandas df
        combined = dfGeo.merge(dfData[[self.get_merge_UID()] + mapOptions.tooltipAttributes], 
                               on=self.get_merge_UID(), 
                               how='left')
        # create the map
        map = folium.Map(attr=mapOptions.mapAttribute, location=mapOptions.mapLocation, tiles=basemap, zoom_start=mapOptions.mapZoom)
        # the alias incl. the date
        coloredAttributeAlias = coloredAttributeAlias + ' as of ' + mapOptions.mapDate.strftime('%Y-%m-%d')
        # the bins for the colored values
        if (mapOptions.bins is None):
            mapOptions.bins = list(combined[coloredAttribute].quantile([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]))
        else:      
            # the minimum/maximum in the coloredAttribute column
            maximum = dfData[coloredAttribute].max()
            minimum = dfData[coloredAttribute].min()
            # ensure min/max value will fit in the bins
            mapOptions.bins[mapOptions.bins.count(0)-1] = max(maximum, mapOptions.bins[mapOptions.bins.count(0)-1])
            mapOptions.bins[0] = min(minimum, mapOptions.bins[0])
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
                                bins=[float(x) for x in mapOptions.bins],
                                highlight=True,
                                smooth_factor = 0.1)
        # give it a name
        cp.layer_name = "Covid-19 data"  
        # add it to the map
        cp.add_to(map)
        # create a tooltip for hovering
        tt = folium.GeoJsonTooltip(fields= mapOptions.tooltipAttributes)
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

    def get_data_directory(self):
        """Returns the data directory as a string
        
        Args:
            -

        Returns:
            DataDirectory: A string pointing to the absolute data directory path
        """
        return self.__dataDirectory
    
    @abstractmethod
    def get_data_df(self):
        """ Returns the pandas data df
        """
        pass

    @abstractmethod
    def get_geo_df(self):
        """ Returns the geoPandas df containing geometry information
        """
        pass
    
    @abstractmethod
    def get_default_map_options(self):
        """ returns the options of the default map
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
    def get_nice_basemaps(self):
        """
        Returns an array of strings referring to nice basemaps for the specific region. At least one basemaps should be given and 
        the preferred basemap should be basemap[0]

        Returns:
            string: A array of strings referring to nice basemaps 
        """
        pass 
