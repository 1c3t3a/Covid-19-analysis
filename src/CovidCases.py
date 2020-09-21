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

"""
This are the changes in version 3  
  
- renamed 'Cases' to 'DailyCases'
- renamed 'Deaths' to 'DailyDeaths'
- renamed 'CumulativeCases' to 'Cases'
- renames 'CumulativeDeaths' to 'Deaths'
- added method to get a list of available GeoIDs/CountyNames (get_available_GeoID_list)
- added method to get the accumulated 7 day incidence (add_incidence_7day_per_100Kpopulation)

This is version2 of this file. These are the changes:

- instead of the ECDC JSON file we are now using the CSV with the same data
- instead of the JSON data structure we are now using a Pandas data frame
  Both changes allow us to easier add new methods and analytics
- the attribute 'Quotient' has been removed. the attribute was the number
  of cases on the day devided by the number of cases of the
  previous day
- 'Continent' is a new field to analyse the distribution of cases over
  continents
- added a function to lowpass a attribute
  The width of the lowpass is given by the number n. The name of the newly
  created attribute is the given name with a tailing number n. E.g. 'Cases' 
  with n = 7 will add to a newly added attribute named 'Cases7'.
- added a function to save a dataframe to a CSV file
- added a function to caculate an estimation for the reproduction rate R0
"""


class CovidCases:
    """
    The constructor takes a string containing the full filenname of a CSV
    database you can down load from the WHO website:
    https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide
    The database will be loaded and kept as a private member. To retrieve the
    data for an indvidual country you can use the public methods
    GetCountryDataByGeoID or GetCountryDataByCountryName. Refer to the CSV
    file for a list of available GeoIDs and CountryNames. Both methods will
    return a list of the following fields as a JSON:

    Date
    The date of the data Country The name of the country

    GeoID
    The GeoID of the country such as FR for France or DE for Germany

    Continent
    the continet of the country

    DailyCases
    The number of new cases on a given day

    Incidence7DayPer100Kpopulation
    The accumulated 7 day incidence. That is the sum of daily cases of the last 7 days divided by the popolation in 100000

    Cases
    The accumulated number of cases since the 31.12.2019

    DoublingTime
    The number of days in which the number of cases will be doubled

    DailyDeaths
    The number of new deaths on the given date

    Deaths
    The accumulated number of deaths since the 31.12.2019

    PercentDeaths
    The number of deaths in % of the cases

    CasesPerMillionPopulation
    The number of cumulative cases devide by the popolation of the countryy in million

    DeathsPerMillionPopulation
    The number of cumulative deaths devide by the popolation of the countr in million
    """

    def __init__(self, filename):
        """
        constructor
        """
        # some benchmarking
        start = time.time()
        # open the file
        self.__df = pd.read_csv(filename)
        # remove columns that we don't need
        self.__df = self.__df.drop(columns=['day', 
                                            'month', 
                                            'year', 
                                            'countryterritoryCode', 
                                            'Cumulative_number_for_14_days_of_COVID-19_cases_per_100000'])
        # rename the columns to be more readable
        self.__df.columns = ['Date',
                             'DailyCases',
                             'DailyDeaths',
                             'Country',
                             'GeoID',
                             'Population',
                             'Continent']
        # change the type of the 'date' field to a pandas date
        self.__df['Date'] = pd.to_datetime(self.__df['Date'],
                                           format='%d/%m/%Y')
        # some benchmarking
        end = time.time()
        print('Panda loading the CSV: ' + str(end - start) + 's')

    @staticmethod
    def download_CSV_file():
        """
        automatically downloads the database file if it doesn't exists. need
        to be called in a try-catch block as it may throw FileNotFoundError or
        IOError errors
        """
        # todays date
        today = date.today()
        # the prefix of the CSV file is Y-m-d
        preFix = today.strftime('%Y-%m-%d')
        try:
            # check if it is running in jupyter
            get_ipython
            # the absolut directory of this python file
            absDirectory = os.path.dirname(os.path.abspath(os.path.abspath('')))
            # the target filename
            targetFilename = os.path.join(absDirectory, './data/' + preFix + '-db.csv')
        except:
            # the absolut directory of this python file
            absDirectory = os.path.dirname(os.path.abspath(__file__))
            # the target filename
            targetFilename = os.path.join(absDirectory, '../data/' + preFix + '-db.csv')
        # check if it exist already
        if os.path.exists(targetFilename):
            print('using existing file: ' + targetFilename)
        else:
            # doownload the file from the ecdc server
            url = 'https://opendata.ecdc.europa.eu/covid19/casedistribution/csv/'
            r = requests.get(url, timeout=1.0)
            if r.status_code == requests.codes.ok:
                with open(targetFilename, 'wb') as f:
                    f.write(r.content)
            else:
                raise FileNotFoundError('Error getting CSV file. Error code: ' + str(r.status_code))
        return targetFilename

    @staticmethod
    def __compute_doubling_time(dfSingleCountry):
        """
        Computes the doubling time for everyday day with the formular:
                ln(2) / ln(Conf[n] / Conf[n - 1])
        returns it as a dataframe
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
        """
        Adds additional attributes to a dataframe of a single country.   
        """
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
        # return the manipulated dataframe
        return dfSingleCountry

    def __apply_lowpass_filter(self, dfAttribute, n):
        """
        Returns a dataframe containing the lowpass filtered (with depth n)
        data of the given dataframe.
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
        """
        Adds a atribute to the df of each country that is the lowpass filtered
        data of the given attribute. The width of the lowpass is given by then
        number n. The name of the newly created attribute is the given name
        with a tailing number n. E.g. 'DailyCases' with n = 7 will add to a newly
        added attribute named 'Cases7'.
        If the attribute already exists the function will return the given df.
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
            # add the coiuntry to the result
            dfs.append(dfSingleCountry)
        return pd.concat(dfs)

    def __apply_r0(self, dfCases):
        """
        Returns a dataframe containing an estimation for the reproduction
        number R0 of the dataframe given. The given dataframe has to contain
        'DailyCases'.
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
        """
        Adds a atribute to the df of each country that is an estimation of the
        reproduction number R0. Here the number is called 'R'. The returned
        dataframe should finally lowpassed filtered with a kernel size of 1x7.
        If the attribute already exists the function will return the given df.
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
            # add the coiuntry to the result
            dfs.append(dfSingleCountry)
        return pd.concat(dfs)

    def __apply_incidence_7day_per_100Kpopulation(self, dfAttribute, dfPopulation):
        """
        Returns a dataframe containing the accumulated 7 day incidence
        of the given dataframe containing only< one country.
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
        """
        Adds a atribute to the df of each country that is representing the
        accumulated 7-day incidence. That is the summ of the daily cases of 
        the last 7 days divded by the population in 100000 people.
        If the attribute already exists the function will return the given df.
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
        """
        Saves a df to a CSV file
        """
        df.to_csv(filename)

    def get_country_data_by_geoid_list(self, geoIDs, lastNdays=0, sinceNcases=0):
        """
        Return the dataframe by a list of geoIDs. Optional attributes are:
        lastNdays: returns just the data of the last n days.
        sinceNcases: returns just the data since the nth case.
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

    def get_country_data_by_geoid_string_list(self, geoIDstringList, lastNdays=0, sinceNcases=0):
        """
        Return the dataframe by a comma separated list of geoIDs. Optional
        attributes are:
        lastNdays: returns just the data of the last n days.
        sinceNcases: returns just the data since the nth case.
        """
        # split the string
        geoIDs = re.split(r',\s*', geoIDstringList.upper())
        # return the concatenated dataframe
        return self.get_country_data_by_geoid_list(geoIDs, lastNdays, sinceNcases)

    def get_all_country_data(self, lastNdays=0, sinceNcases=0):
        """
        Return the dataframe of all countries. Optional attributes are:
        lastNdays: returns just the data of the last n days.
        sinceNcases: returns just the data since the nth case.
        """
        # return all countries, but first add the extra columns
        return self.get_country_data_by_geoid_list(self.__df['GeoID'].unique(), lastNdays=lastNdays, sinceNcases=sinceNcases)

    def get_available_GeoID_list(self):
        """
        Returns a dataframe having just two columns for the GeoID and Country name.  
        """
        # the list of GeoIDs in the dataframe
        geoIDs = self.__df['GeoID'].unique()
        # the list of country names in the dataframe
        countries = self.__df['Country'].unique()
        # merge them together
        list_of_tuples = list(zip(geoIDs, countries))
        # create a datafarme out of the list
        dfResult = pd.DataFrame(list_of_tuples, columns=['GeoID', 'Country'])
        return dfResult
