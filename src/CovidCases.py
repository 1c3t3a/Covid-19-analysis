import pandas as pd
import numpy as np
import math
import re
import time
import datetime
import os
import requests
import re
from datetime import date
from abc import ABC, abstractmethod

class CovidCases(ABC):
    """This abstract base class will expose data attributes in form of a DataFrame. It also provides methods to process 
    the data which will end up in additional columns in the DataFrame.  
    These are the names of six columns that have to be generated by ALL subclasses.

    Date
    The date of the data 
    
    GeoID
    The ISO-3166-alpha_3 GeoID of the area such as 'FR' for France or 'DE' for Germany

    GeoName
    The name of the area such as 'England' or 'Italy'

    Population
    The population of the country

    Continent
    E.g. The continent of the country. But it also may be grouping value for e.g. the states of a federal republic such as Bavaria
    
    DailyCases
    The number of new cases on a given day

    DailyDeaths
    The number of new deaths on the given date

    Beside these fields a subclass might also define additional columns such as 'Continent'
    Based on the six mandatory columns the class will generate the following additional columns (attributes):
    
    Cases
    The accumulated number of cases since the 31.12.2019

    Deaths
    The accumulated number of deaths since the 31.12.2019

    CasesPerMillionPopulation
    The number of cumulative cases divided by the population of the country in million

    DeathsPerMillionPopulation
    The number of cumulative deaths divided by the population of the country in million

    PercentDeaths
    The number of deaths in % of the cases. This is the Case Fatality Rate (CFR), an approximation for the
    Infection Fatality Rate (IFR) that includes also 'hidden' cases.

    Incidence7DayPer100Kpopulation
    The accumulated 7 day incidence. That is the sum of daily cases of the last 7 days divided by the 
    population in 100000

    DoublingTime
    The number of days in which the number of cases will be doubled

    R0
    This is an estimation of the reproduction number R0. As the calculation takes some time it is 
    generated on demand by calling add_r0 method.

    Returns:
        You can't create an instance of this class. Instead create an instance of a subclass
    """

    def __init__(self, df):
        """The constructor takes a dataframe loaded by any sub-class containing the data published by the
        website that is handled in the sub-classes individually.  
        To retrieve the data for an individual country you can use the public methods
        GetCountryDataByGeoID or GetCountryDataByCountryName. These functions take ISO 3166 alpha_2 
        (2 characters long) GeoIDs.

        Args:
            df (dataframe): The dataframe containing information about individual countries such as
                            GeoID, CountryName, Cases and Deaths. 
        """
        # keep the data frame
        self.__df = df
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
 
    @staticmethod
    def __compute_doubling_time(dfSingleCountry):
        """Computes the doubling time for everyday day with the formula:
                ln(2) / ln(Conf[n] / Conf[n - 1])
        
        Args:
            dfSingleCountry (DataFrame): A dataframe holding only one country

        Returns:
            DataFrame: A data frame holding only one column to be appended to another data frame
        """
        result = []
        quotient = []
        for index, value in dfSingleCountry['Cases'].iteritems():
            #  calculating the quotient conf[n] / conf[n-1]
            if index > 0 and index - 1 != 0:
                quotient.append(value / dfSingleCountry['Cases'][index - 1])
            else:
                quotient.append(math.nan)
            # calculates the doubling time (can't be calculated when there's 
            # no change from one day to the other)
            if quotient[index] != 1 and quotient[index] != math.nan:
                result.append(math.log(2) / math.log(quotient[index]))
            else:
                result.append(math.nan)
        # return the dataframe
        return pd.DataFrame(np.asarray(result))

    def __add_additional_attributes(self, dfSingleCountry):
        """Adds additional attributes to a dataframe of a single country.  

        Args:
            dfSingleCountry (DataFrame): A dataframe holding only one country

        Returns:
            DataFrame: The modified data frame of the country
        """
        if dfSingleCountry.empty == True:
            return
        # reset the index on the dataframe (if the argument is just a slice)
        dfSingleCountry.reset_index(inplace=True, drop=True)

        # the cumlative cases
        dfSingleCountry['Cases'] = dfSingleCountry['DailyCases'].cumsum()
        # the cumlative cases
        dfSingleCountry['Deaths'] = dfSingleCountry['DailyDeaths'].cumsum()
        # the percentage of deaths of the cumulative cases
        dfSingleCountry['PercentDeaths'] = pd.DataFrame({'PercentDeaths': dfSingleCountry['Deaths'] * 100 / dfSingleCountry['Cases']})
        # the percentage of cumulative cases of the 1 million population
        dfSingleCountry['CasesPerMillionPopulation'] = pd.DataFrame({'CasesPerMillionPopulation': dfSingleCountry['Cases'].div(dfSingleCountry['Population'].iloc[0] / 1000000)})
        # the percantage of cumulative deaths of 1 million population
        dfSingleCountry['DeathsPerMillionPopulation'] = pd.DataFrame({'DeathsPerMillionPopulation': dfSingleCountry['Deaths'].div(dfSingleCountry['Population'].iloc[0] / 1000000)})
        # adds the extra attributes
        dfSingleCountry['DoublingTime'] = self.__compute_doubling_time(dfSingleCountry)
        # now apply the country names from our internal list
        dfInfo = self.__dfGeoInformationWorld
        # return the manipulated dataframe
        return dfSingleCountry

    def __apply_lowpass_filter(self, dfAttribute, n):
        """Returns a dataframe containing the lowpass filtered (with depth n)
        data of the given dataframe.

        Args:
            dfAttribute (DataFrame): The data frame to be filtered
            n (int): Width of the lowpass filter

        Returns:
            DataFrame: A data frame holding only one column to be appended to another data frame
        """
        result = []
        # iterate the attribute
        for index, value in dfAttribute.iteritems():
            # if the dataframe contains NaN, leave it untouched
            if math.isnan(value):
                result.append(math.nan)
                continue
            if index == 0:
                result.append(value)
            # for all rows below the nth row, calculate the lowpass filter up to this point
            elif index < n:
                result.append(sum(dfAttribute[0:index + 1]) / (index + 1))
            else:
                start = index - n + 1
                result.append(sum(dfAttribute[start:start + n]) / n)
        # return the calculated data as an array
        return pd.DataFrame(np.asarray(result))

    def add_lowpass_filter_for_attribute(self, df, attribute, n):
        """Adds a attribute to the df of each country that is the lowpass filtered
        data of the given attribute. The width of the lowpass is given by then
        number n. The name of the newly created attribute is the given name
        with a tailing number n. E.g. 'DailyCases' with n = 7 will add to a newly
        added attribute named 'Cases7'.
        If the attribute already exists the function will return the given df.

        Args:
            df (DataFrame): The data frame holding all countries and all columns
            attribute (str): The name of the column to be processed
            n (int): The width of the lowpass filter

        Returns:
            DataFrame: A data frame that includes the newly generated column
        """ 
        # check if the attribute already exists
        requestedAttribute = attribute + str(n)
        for col in df.columns:
            if col == requestedAttribute:
                return df
        # get all GeoIDs in the df
        geoIDs = df['GeoID'].unique()
        # our result data frame
        dfs = []
        for geoID in geoIDs:
            # get the country dataframe
            dfSingleCountry = df.loc[df['GeoID'] == geoID].copy()
            # reset the index to start from index = 0
            dfSingleCountry.reset_index(inplace=True, drop=True)
            # add the lowpass filtered attribute
            dfSingleCountry[requestedAttribute] = self.__apply_lowpass_filter(dfSingleCountry[attribute], 7)
            # add the country to the result
            dfs.append(dfSingleCountry)
        return pd.concat(dfs)

    def __apply_r0(self, dfCases):
        """Returns a dataframe containing an estimation for the reproduction
        number R0 of the dataframe given. The given dataframe has to contain
        'DailyCases'.

        Args:
            dfCases (DataFrame): The data frame to be processed
            
        Returns:
            DataFrame: A data frame holding only one column to be appended to another data frame
        """
        # add the r0 attribute
        result = []
        # we will create 2 blocks and sum the data of each block
        blockSize = 4
        # iterate the cases
        for index, value in dfCases.iteritems():
            if index < 2 * blockSize - 1:
                result.append(math.nan)
            else:
                # the sum of block 0
                start = index - (2 * blockSize - 1)
                sum0 = sum(dfCases[start: start + blockSize])
                # the sum of block 1
                start = index - (blockSize - 1)
                sum1 = sum(dfCases[start: start + blockSize])
                # and R
                if sum0 == 0:
                    R = math.nan
                else:
                    R = sum1 / sum0
                result.append(R)
        # return the calculated data as an array
        return pd.DataFrame(np.asarray(result))

    def add_r0(self, df):
        """Adds a attribute to the df of each country that is an estimation of the
        reproduction number R0. Here the number is called 'R'. The returned
        dataframe should finally lowpassed filtered with a kernel size of 1x7.
        If the attribute already exists the function will return the given df.
        
        Args:
            df (DataFrame): The data frame holding all countries and all columns

        Returns:
            DataFrame: A data frame that includes the newly generated column
        """ 
        # check if the attribute already exists
        requestedAttribute = 'R'
        for col in df.columns:
            if col == requestedAttribute:
                return df
        # get all GeoIDs in the df
        geoIDs = df['GeoID'].unique()
        # our result data frame
        dfs = []
        for geoID in geoIDs:
            # get the country dataframe
            dfSingleCountry = df.loc[df['GeoID'] == geoID].copy()
            # reset the index to start from index = 0
            dfSingleCountry.reset_index(inplace=True, drop=True)
            # add the lowpass filtered attribute
            dfSingleCountry[requestedAttribute] = self.__apply_r0(dfSingleCountry['DailyCases'])
            # add the country to the result
            dfs.append(dfSingleCountry)
        return pd.concat(dfs)

    def __apply_incidence_7day_per_100Kpopulation(self, dfAttribute, dfPopulation):
        """Returns a dataframe containing the accumulated 7 day incidence
        of the given dataframe containing only one country.
        
        Args:
            dfAttribute (DataFrame): The data frame holding the daily ne cases
            dfPopulation (DataFrame): A data frame holding the population
            
        Returns:
            DataFrame: A data frame holding only one column to be appended to another data frame
        """
        result = []
        # iterate the attribute
        for index, value in dfAttribute.iteritems():
            # for all rows below the nth row, calculate the lowpass filter up to this point
            if index < 7:
                daysSum7 = sum(dfAttribute[0:index + 1]) * 7 / (index + 1)
                result.append(daysSum7  / (dfPopulation[index] / 100000))
            else:
                start = index - 7 + 1
                daysSum7 = sum(dfAttribute[start:start + 7])
                result.append(daysSum7 / (dfPopulation[index] / 100000))
        # return the calculated data as an array
        return pd.DataFrame(np.asarray(result))

    def add_incidence_7day_per_100Kpopulation(self, df):
        """Adds a attribute to the df of each country that is representing the
        accumulated 7-day incidence. That is the sum of the daily cases of 
        the last 7 days divided by the population in 100000 people.
        If the attribute already exists the function will return the given df.
        
        Args:
            df (DataFrame): The data frame holding all countries and all columns

        Returns:
            DataFrame: A data frame that includes the newly generated column
        """ 
        # check if the attribute exists
        requestedAttribute = 'Incidence7DayPer100Kpopulation'
        for col in df.columns:
            if col == requestedAttribute:
                return df
        # get all GeoIDs in the df
        geoIDs = df['GeoID'].unique()
        # our result data frame
        dfs = []
        for geoID in geoIDs:
            # get the country dataframe
            dfSingleCountry = df.loc[df['GeoID'] == geoID].copy()
            # reset the index to start from index = 0
            dfSingleCountry.reset_index(inplace=True, drop=True)
            # add the lowpass filtered attribute
            dfSingleCountry[requestedAttribute] = self.__apply_incidence_7day_per_100Kpopulation(dfSingleCountry['DailyCases'], dfSingleCountry['Population'])
            # add the coiuntry to the result
            dfs.append(dfSingleCountry)
        return pd.concat(dfs)

    def save_df_to_csv(self, df, filename):
        """Saves a df to a CSV file

        Args:
            df (DataFrame): The data frame holding all countries and all columns
            filename (str): The name of the output file
        """       
        df.to_csv(filename)

    def get_data_by_geoid_list(self, geoIDs, lastNdays=0, sinceNcases=0):
        """Return the dataframe by a list of geoIDs. Refer to the CSV
        file for a list of available GeoIDs and CountryNames.

        Args:
            geoIDs (list): A list of strings holding the GeoIds
            lastNdays (int, optional): Get the data only for the last N days. Defaults to 0.
            sinceNcases (int, optional): Get the data since the Nth. case has been exceeded. Defaults to 0.

        Raises:
            ValueError: In case that both optional arguments have been used (>0) 

        Returns:
            DataFrame: A data frame holding the information of the selected countries
        """
        # check if only one optional parameter is used
        if lastNdays > 0 and sinceNcases > 0:
            raise ValueError("Only one optional parameter allowed!")
        # our result data frame
        dfs = []
        # get data for each country
        for geoID in geoIDs:
            # get the data for a country and add the additional rows
            df = self.__df.loc[self.__df['GeoID'] == geoID].copy()
            # reverse the data frame to the newest date in the bottom
            df = df.reindex(index=df.index[::-1])
            df.head()
            df = self.__add_additional_attributes(df)
            # if lastNdays is specified just return these last n days
            if lastNdays > 0:
                df = df.tail(lastNdays)
            # if sinceNcases is specified calculate the start index
            if sinceNcases > 0:
                start = -1
                for index, val in df['Cases'].iteritems():
                    if val >= sinceNcases:
                        start = index
                        break
                # an illegal input will cause an exception
                if start == -1:
                    raise ValueError("Number of cases wasn't that high!")
                # copy the data
                df = df.iloc[start:].copy()
                # reset the index on the remaining data points so that they
                # start at zero
                df.reset_index(inplace=True, drop=True)
            # append this dataframe to our result
            dfs.append(df)
        # return the concatenated dataframe
        return pd.concat(dfs)

    def get_data_by_geoid_string_list(self, geoIDstringList, lastNdays=0, sinceNcases=0):
        """Return the dataframe by a comma separated list of geoIDs. Refer to the CSV
        file for a list of available GeoIDs and CountryNames.

        Args:
            geoIDs (str): A string of comma separated GeoIds
            lastNdays (int, optional): Get the data only for the last N days. Defaults to 0.
            sinceNcases (int, optional): Get the data since the Nth. case has been exceeded. Defaults to 0.

        Raises:
            ValueError: In case that both optional arguments have been used (>0) 

        Returns:
            DataFrame: A data frame holding the information of the selected countries
        """
        # split the string
        geoIDs = re.split(r',\s*', geoIDstringList.upper())
        # return the concatenated dataframe
        return self.get_data_by_geoid_list(geoIDs, lastNdays, sinceNcases)

    def get_all_data(self):
        """Return the dataframe of all countries in the database.
        
        Returns:
            DataFrame: A data frame holding the information of all countries in the file
        """
        # return all countries, but first add the extra columns
        return self.get_data_by_geoid_list(self.__df['GeoID'].unique(), lastNdays=lastNdays, sinceNcases=sinceNcases)

    @abstractmethod
    def get_available_GeoID_list(self):
        """
        Returns a dataframe having just two columns for the GeoID and region/country or whatever name.  
        Needs to be implemented by all sub-classes derived from this.

        Returns:
            Dataframe: A dataframe having two columns: The country name and GeoID
        """
        pass 

    @abstractmethod
    def get_data_source_info(self):
        """
        Returns a dataframe containing information about the data source. The dataframe holds 3 columns:
        InfoFullName: The full name of the data source
        InfoShortName: A shortname for the data source
        InfoLink: The link to get the data

        Returns:
            Dataframe: A dataframe holding the information
        """
        pass 