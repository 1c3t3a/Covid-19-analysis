import datetime
from datetime import date
import math
import pandas as pd
import os

class GeoInformationWorld():
    
    def __init__(self):
        """The constructor loads a CSV with the geo information of the countries of the world.  
            ATTENTION: The GeoID and alpha-2 of Nambia would be 'NA' but panadas csv reader makes a NaN out of it.

        Raises:
            FileNotFoundError: In case it couldn't download the file

        """
        # load the geo information for the world
        try:
            # check if it is running in jupyter
            get_ipython
            # the absolute directory of this python file
            absDirectory = os.path.dirname(os.path.abspath(os.path.abspath('')))
            # the target filename
            targetFilename = os.path.join(absDirectory, './data/GeoInformationWorld.csv')
        except:
            # the absolute directory of this python file
            absDirectory = os.path.dirname(os.path.abspath(__file__))
            # the target filename
            targetFilename = os.path.join(absDirectory, '../data/GeoInformationWorld.csv')
        # check if it exist already
        if os.path.exists(targetFilename):
            self.__dfGeoInformationWorld = pd.read_csv(targetFilename)
        else:
            raise FileNotFoundError("Error loading " + targetFilename)

    def get_geo_information_world(self):
        """Return the dataframe of information of all countries such as country name, continent, population etc..
        
        Returns:
            DataFrame: A data frame holding the information of all countries
        """
        return self.__dfGeoInformationWorld

    def geo_name_from_geoid (self, geoID):
        """Return the name of a country of the internal geo information from a given ISO-3166-alpha_2 geoid.
        
        Args:
            geoID (str):  a string of a ISO-3166-alpha_2 geoid

        Returns:
            str: the country name
        """
        # get the world info
        dfInfo = self.get_geo_information_world()
        # ISO-3166-alpha_3
        # find the row in our internal listin the GeoID column
        dfTheOne = dfInfo.loc[dfInfo['GeoID'] == geoID]
        # the name used in our internal list
        return dfTheOne['GeoName'].values[0]
        
    def geo_name_from_ISO3166_alpha_3 (self, geoID):
        """Return the name of a country of the internal geo information from a given ISO-3166-alpha_3 geoid.

        Args:
            geoID (str):  a string of a ISO-3166-alpha_3 geoid

        Returns:
            str: the country name
        """
        # get the world info
        dfInfo = self.get_geo_information_world()
        # find the row in our internal listin the GeoID column
        dfTheOne = dfInfo.loc[dfInfo['ISO-3166-alpha_3'] == geoID]
        # the name used in our internal list
        return dfTheOne['GeoName'].values[0]

    def geoID_from_ISO3166_alpha_3 (self, geoID):
        """Return the name of a country of the internal geo information from a given ISO-3166-alpha_3 geoid.

        Args:
            geoID (str):  a string of a ISO-3166-alpha_3 geoid

        Returns:
            str: ISO-3166-alpha_2 geoid
        """
        # get the world info
        dfInfo = self.get_geo_information_world()
        # find the row in our internal listin the GeoID column
        dfTheOne = dfInfo.loc[dfInfo['ISO-3166-alpha_3'] == geoID]
        # the name used in our internal list
        return dfTheOne['GeoID'].values[0]

    def ISO3166_alpha_3_from_geoID (self, geoID):
        """Return the name of a country of the internal geo information from a given ISO-3166-alpha_2 geoid.

        Args:
            geoID (str):  a string of a ISO-3166-alpha_2 geoid

        Returns:
            str: the ISO-3166-alpha_3 geoid
        """
        # get the world info
        dfInfo = self.get_geo_information_world()
        # find the row in our internal list in the GeoID column
        dfTheOne = dfInfo.loc[dfInfo['GeoID'] == geoID]
        # the name used in our internal list
        return dfTheOne['ISO-3166-alpha_3'].values[0]

    def population_from_geoid(self, geoID):
        """Return the population of a country of the internal geo information from a given geoName.

        Args:
            geoID (str):  a string with the country name such as 'Germany'

        Returns:
            int: the population of the country
        """
        # get the world info
        dfInfo = self.get_geo_information_world()
         # find the row in our internal list in the GeoID column
        dfTheOne = dfInfo.loc[dfInfo['GeoID'] == geoID]
        # the name used in our internal list
        pop = int(dfTheOne['Population2019'].values[0])
        return pop

    def continent_from_geoid(self, geoID):
        """Return the continent of a country of the internal geo information from a given geoName.

        Args:
            geoID (str):  a string with the country name such as 'Germany'

        Returns:
            str: the continent of the country
        """
        # get the world info
        dfInfo = self.get_geo_information_world()
         # find the row in our internal list in the GeoID column
        dfTheOne = dfInfo.loc[dfInfo['GeoID'] == geoID]
        # the name used in our internal list
        return dfTheOne['Continent'].values[0]
