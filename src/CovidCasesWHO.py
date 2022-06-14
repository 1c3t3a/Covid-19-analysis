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
from CovidCases import CovidCases
from GeoInformationWorld import GeoInformationWorld

class CovidCasesWHO(CovidCases):
    """The class will expose data attributes in form of a DataFrame. Its base class also provides methods to process 
    the data which will end up in additional columns in the DataFrame. These are the name sof the columns
    that are generated. Notice: The 'Continent' column is additionally and specific to this sub class.

    ATTENTION: The CovidCasesWHOv1 class is a older version of this class and it will load 50% slower. Both classes
               produce the same results

    Date
    The date of the data 
    
    GeoID
    The GeoID of the country such as FR for France or DE for Germany

    GeoName
    The name of the country

    Continent
    The continent of the country

    Population
    The population of the country

    DailyCases
    The number of new cases on a given day

    DailyDeaths
    The number of new deaths on the given date

    Continent
    The continent of the country as an additional column
    
    Returns:
        CovidCasesWHO: A class to provide access to some data based on the WHO file.
    """

    def __init__(self, filename, cacheLevel = 0):
        """The constructor takes a string containing the full filename of a CSV
        database you can download from the WHO website:
        https://covid19.who.int/WHO-COVID-19-global-data.csv
        The database will be loaded and kept as a private member. If there is a cache
        file containing pre-calculated attributes it will be loaded instead of the 
        downloaded WHO file. If there is no cache file available it may force the base 
        class to build such a cache at the given cache level. A cache file is detected 
        by having and tailing '-cache.csv'.
        To retrieve the data for an individual country you can use the public methods
        GetCountryDataByGeoID or GetCountryDataByCountryName. These functions take 
        ISO 3166 alpha_2 (2 characters long) GeoIDs.

        Args:
            filename (str): The full path and name of the csv file. 
            cacheLevel (int, optional): the amount of data to be calculated for the cache. Defaults to 0.
                refer to CovidCase.__build_cache for more information of the different cache levels
        """
        # some benchmarking
        start = time.time()
        # use a cache if it exists
        filenameCache = os.path.splitext(filename)[0] + '-cache.csv'
        if os.path.exists(filenameCache):
            print('using cache file: ' + filenameCache)
             # open the file
            self.__df = pd.read_csv(filenameCache, keep_default_na=False)
            # change the type of the 'date' field to a pandas date
            self.__df['Date'] = pd.to_datetime(self.__df['Date'],
                                               format='%Y-%m-%d')
            # now ensure the data layout
            dfs = []
            for geoID in self.__df['GeoID'].unique():
                # get the data for a country
                dfSingleCountry = self.__df.loc[self.__df['GeoID'] == geoID].copy()
                # reset the index
                dfSingleCountry.reset_index(inplace=True, drop=True)
                dfSingleCountry.head()
                # re-order it from newest to olders (top-bottom)
                dfSingleCountry = dfSingleCountry.reindex(index=dfSingleCountry.index[::-1])
                # append this dataframe to our result
                dfs.append(dfSingleCountry)
            # keep the concatenated dataframe
            self.__df = pd.concat(dfs)
            # some benchmarking
            end = time.time()
            print('Pandas loading the cached WHO CSV: ' + str(end - start) + 's')
            # pass the dataframe to the base class
            super().__init__(self.__df)
            return
        # open the file
        self.__df = pd.read_csv(filename, keep_default_na=False)
        # drop some columns
        self.__df = self.__df.drop(columns=['WHO_region',
                                            'Cumulative_cases',
                                            'Cumulative_deaths'])
        # rename the columns to be more readable
        self.__df.columns = ['Date',
                             'GeoID',
                             'GeoName',
                             'DailyCases',
                             'DailyDeaths']
        
        # now apply the country names from our internal list
        giw = GeoInformationWorld()
        # get all country info
        dfInfo = giw.get_geo_information_world()
        # our result data frame
        dfs = []
        for geoID in self.__df['GeoID'].unique():
            # 'other' fix
            if geoID == ' ':
                continue
            # 'Saba' fix
            if geoID == 'XC':
                continue
            # Sint Eustatius
            if geoID == 'XB':
                continue
            # American Samoa
            if geoID == 'AS':
                continue
            # Korea, People's Republic
            if geoID == 'KP':
                continue
            # French Guinea
            if geoID == 'GF':
                continue
            # Guadeloupe
            if geoID == 'GP':
                continue
            # Kiribati
            if geoID == 'KI':
                continue
            # Martinique
            if geoID == 'MQ':
                continue
            # Mayotte
            if geoID == 'YT':
                continue
            # Micronesia 
            if geoID == 'FM':
                continue
            # Nauru
            if geoID == 'NR':
                continue
            # Niue
            if geoID == 'NU':
                continue
            # Palau
            if geoID == 'PW':
                continue
            # Pitcairn Islands
            if geoID == 'PN':
                continue
            # Réunion
            if geoID == 'RE':
                continue
            # Saint Barthélemy
            if geoID == 'BL':
                continue
            # Saint Helena
            if geoID == 'SH':
                continue
            # Saint Martin
            if geoID == 'MF':
                continue
            # Saint Pierre and Miquelon
            if geoID == 'PM':
                continue
            # Turkmenistan
            if geoID == 'TM':
                continue
            # Tokelau
            if geoID == 'TK':
                continue
            # Tonga
            if geoID == 'TO':
                continue
            # Tuvalu
            if geoID == 'TV':
                continue

            # get the data for a country and add the additional rows
            dfSingleCountry = self.__df.loc[self.__df['GeoID'] == geoID].copy()
            # reset the index
            dfSingleCountry.reset_index(inplace=True, drop=True)
            dfSingleCountry.head()
            # Bonaire workaround
            if geoID == 'XA':
                geoID = 'BQ'
                dfSingleCountry['GeoID'] = [geoID for _ in range(0, len(dfSingleCountry['GeoID']))]    
            # get the geoName for this geoID from our internal list
            geoName = giw.geo_name_from_geoid(geoID)
            # the current name         
            curName = dfSingleCountry['GeoName'][0]
            # replace it if necessary
            if geoName != curName:
                dfSingleCountry['GeoName'] = [geoName for _ in range(0, len(dfSingleCountry['GeoID']))]
            # get the continent for this geoID from our internal list
            continent = giw.continent_from_geoid(geoID)
            # apply it to this country
            dfSingleCountry['Continent'] = [continent for _ in range(0, len(dfSingleCountry['GeoID']))]
            # get the population for this geoID from our internal list
            population = giw.population_from_geoid(geoID)
            # apply it to this country
            dfSingleCountry['Population'] = [population for _ in range(0, len(dfSingleCountry['GeoID']))]
            # re-order it from newest to olders (top-bottom)
            dfSingleCountry = dfSingleCountry.reindex(index=dfSingleCountry.index[::-1])
            # append this dataframe to our result
            dfs.append(dfSingleCountry)
        # keep the concatenated dataframe
        self.__df = pd.concat(dfs)
        # re-order the columns to be similar for all sub-classes                                   
        self.__df = self.__df[['Date', 
                              'GeoName', 
                              'GeoID', 
                              'Population', 
                              'Continent', 
                              'DailyCases',
                              'DailyDeaths']]
        # change the type of the 'date' field to a pandas date
        self.__df['Date'] = pd.to_datetime(self.__df['Date'],
                                           format='%Y-%m-%d')
        # some benchmarking
        end = time.time()
        print('Pandas loading the WHO CSV: ' + str(end - start) + 's')
        # pass the dataframe to the base class
        if ((filenameCache != '') and (cacheLevel > 0)):
            # force the base class to build and save the cache
            super().__init__(self.__df, filenameCache, cacheLevel)
        else:
            super().__init__(self.__df)
        

    @staticmethod
    def download_CSV_file():
        """automatically downloads the database file if it doesn't exists. Need
        to be called in a try-catch block as it may throw FileNotFoundError or
        IOError errors

        Raises:
            FileNotFoundError: In case it couldn't download the file

        Returns:
            str: The filename of the database wether it has been downloaded or not.
        """
        # todays date
        today = date.today()
        # the prefix of the CSV file is Y-m-d
        preFix = today.strftime('%Y-%m-%d') + "-WHO"
        try:
            # check if it is running in jupyter
            get_ipython
            # the absolute directory of this python file
            absDirectory = os.path.dirname(os.path.abspath(os.path.abspath('')))
            # the target filename
            targetFilename = os.path.join(absDirectory, './data/' + preFix + '-db.csv')
        except:
            # the absolute directory of this python file
            absDirectory = os.path.dirname(os.path.abspath(__file__))
            # the target filename
            targetFilename = os.path.join(absDirectory, '../data/' + preFix + '-db.csv')
        # check if it exist already
        if os.path.exists(targetFilename):
            print('using existing file: ' + targetFilename)
        else:
            # download the file from the ecdc server
            url = 'https://covid19.who.int/WHO-COVID-19-global-data.csv'
            r = requests.get(url, timeout=1.0)
            if r.status_code == requests.codes.ok:
                with open(targetFilename, 'wb') as f:
                    f.write(r.content)
            else:
                raise FileNotFoundError('Error getting CSV file. Error code: ' + str(r.status_code))
        return targetFilename

    def get_available_GeoID_list(self):
        """Returns a dataframe having just two columns for the GeoID and Country name

        Returns:
            Dataframe: A dataframe having two columns: The country name and GeoID
        """ 
        # the list of GeoIDs in the dataframe
        geoIDs = self.__df['GeoID'].unique()
        # the list of country names in the dataframe
        countries = self.__df['GeoName'].unique()
        # merge them together
        list_of_tuples = list(zip(geoIDs, countries))
        # create a dataframe out of the list
        dfResult = pd.DataFrame(list_of_tuples, columns=['GeoID', 'GeoName'])
        return dfResult

    def get_data_source_info(self):
        """
        Returns a list containing information about the data source. The list holds 3 strings:
        InfoFullName: The full name of the data source
        InfoShortName: A shortname for the data source
        InfoLink: The link to get the data

        Returns:
            Dataframe: A dataframe holding the information
        """
        info = ["World Health Organization", 
                "WHO",
                "https://covid19.who.int/WHO-COVID-19-global-data.csv"]
        return info

    def review_geoid_list(self, geoIDs):
        """
        Returns a corrected version of the given geoID list to ensure that cases of mismatches like UK-GB are corrected by the sub-class.  
        geoIDs: The list holding the geoIDs as requested such as ['DE', 'UK']

        Returns:
            list: A corrected list such as ['DE', 'GB'] that translates incorrect country codes to corrected codes 
        """
        # fix the ECDC mistakes and map e.g. UK to GB 
        corrected = []
        for geoID in geoIDs:
            if geoID == 'UK':
                corrected.append('GB')
            elif geoID == 'EL':
                corrected.append('GR')
            elif geoID == 'TW':
                corrected.append('CN')
            else:
                corrected.append(geoID)
        return corrected

    @staticmethod
    def get_pygal_european_geoid_list():
        """Returns a list of GeoIDs of European countries that are available in PayGal and 
        the WHO data. 
        Be aware:
        Not all countries of the WHO are available in PayGal and some names are different 
        (GB in PyGal = UK in WHO, GR in PyGal = EL in WHO). PyGal uses lower case and WHO
        upper case. 

        Returns:
            list: List of strings of GeoID's
        """
        # just the main countries for a map
        geoIDs = re.split(r',\s*', CovidCasesWHO.get_pygal_european_geoid_string_list().upper())
        return geoIDs

    @staticmethod
    def get_pygal_european_geoid_string_list():
        """
        Returns a comma separated list of GeoIDs of European countries that are available in 
        PayGal and the WHO data. 
        Be aware:
        Not all countries of the WHO are available in PayGal and some names are different 
        (GB in PyGal = UK in WHO, GR in PyGal = EL in WHO). PyGal uses lower case and WHO
        upper case. 

        Returns:
            str: A comma separate list of GeoID's
        """
        # just the main european countries for a map, pygal doesn't contain e.g. 
        # Andorra, Kosovo (XK)
        geoIdList = 'AM, AL, AZ, AT, BA, BE, BG, BY, CH, CY, CZ, ' + \
                    'DE, DK, EE, GR, ES, FI, FR, GE, GL, '  + \
                    'HU, HR, IE, IS, IT, LV, LI, LT, ' + \
                    'MD, ME, MK, MT, NL, NO, PL, PT, ' + \
                    'RU, SE, SI, SK, RO, UA, GB, RS'
        return geoIdList

    @staticmethod
    def get_pygal_american_geoid_list():
        """Returns a list of GeoIDs of American countries that are available in PayGal and 
        the WHO data. 
        Be aware:
        Not all countries of the WHO are available in PayGal and some names are different 
        (GB in PyGal = UK in WHO, GR in PyGal = EL in WHO). PyGal uses lower case and WHO
        upper case. 

        Returns:
            list: List of strings of GeoID's
        """
        # just the main countries for a map
        geoIDs = re.split(r',\s*', CovidCasesWHO.get_pygal_american_geoid_string_list().upper())
        return geoIDs
        
    @staticmethod
    def get_pygal_american_geoid_string_list():
        """
        Returns a comma separated list of GeoIDs of American countries that are available in 
        PayGal and the WHO data. 
        Be aware:
        Not all countries of the WHO are available in PayGal and some names are different 
        (GB in PyGal = UK in WHO, GR in PyGal = EL in WHO). PyGal uses lower case and WHO
        upper case. 

        Returns:
            str: A comma separate list of GeoID's
        """
        # just the main american countries for a map, pygal doesn't contain e.g. 
        # Bahamas (BS), Barbados (BB), Bermuda (BM), Falkland Island (FK)
        # 2022-01-22 added BZ
        geoIdList = 'AR, BB, BM, BO, BR, BS, CA, CL, CO, ' + \
                    'CR, CU, DO, EC, SV, GT, GY, HN, HT, ' + \
                    'JM, MX, NI, PA, PE, PR, PY, SR, US, UY, VE, BZ'
        return geoIdList

    @staticmethod
    def get_pygal_asian_geoid_list():
        """Returns a list of GeoIDs of Asian countries that are available in PayGal and 
        the WHO data. 
        Be aware:
        Not all countries of the WHO are available in PayGal and some names are different 
        (GB in PyGal = UK in WHO, GR in PyGal = EL in WHO). PyGal uses lower case and WHO
        upper case. 

        Returns:
            list: List of strings of GeoID's
        """
        # just the main countries for a map
        geoIDs = re.split(r',\s*', CovidCasesWHO.get_pygal_asian_geoid_string_list().upper())
        return geoIDs
        
    @staticmethod
    def get_pygal_asian_geoid_string_list():
        """
        Returns a comma separated list of GeoIDs of Asian countries that are available in 
        PayGal and the WHO data. 
        Be aware:
        Not all countries of the WHO are available in PayGal and some names are different 
        (GB in PyGal = UK in WHO, GR in PyGal = EL in WHO). PyGal uses lower case and WHO
        upper case. 

        Returns:
            str: A comma separate list of GeoID's
        """
        # just the main asian countries for a map, pygal doesn't contain e.g. 
        # Qatar (QA)
        geoIdList = 'AF, BH, BD, BT, BN, KH, CN, IR, IQ, IL, JP, JO, '  + \
                    'KZ, KW, KG, LA, LB, MY, MV, MN, MM, NP, OM, PK, PS, PH, '  + \
                    'QA, SA, SG, KR, LK, SY, TJ, TH, TL, TR, AE, UZ, VN, YE, IN, ID'
        return geoIdList
    
    @staticmethod
    def get_pygal_african_geoid_list():
        """Returns a list of GeoIDs of African countries that are available in PayGal and 
        the WHO data. 
        Be aware:
        Not all countries of the WHO are available in PayGal and some names are different 
        (GB in PyGal = UK in WHO, GR in PyGal = EL in WHO). PyGal uses lower case and WHO
        upper case. 

        Returns:
            list: List of strings of GeoID's
        """
        # just the main countries for a map
        geoIDs = re.split(r',\s*', CovidCasesWHO.get_pygal_african_geoid_string_list().upper())
        return geoIDs
        
    @staticmethod
    def get_pygal_african_geoid_string_list():
        """
        Returns a comma separated list of GeoIDs of African countries that are available in 
        PayGal and the WHO data. 
        Be aware:
        Not all countries of the WHO are available in PayGal and some names are different 
        (GB in PyGal = UK in WHO, GR in PyGal = EL in WHO). PyGal uses lower case and WHO
        upper case. 

        Returns:
            str: A comma separate list of GeoID's
        """
        # just the main african countries for a map, pygal doesn't contain e.g. 
        # Comoros (KM)
        # 2022-01-22 added NA
        geoIdList = 'DZ, AO, BJ, BW, BF, BI, CM, CV, CF, TD, KM, CG, CI, CD, '  + \
                    'DJ, EG, GQ, ER, SZ, ET, GA, GM, GH, GN, GW, KE, LS, LR, '  + \
                    'LY, MG, MW, ML, MR, MU, MA, MZ, NE, NG, RW, ST, SN, SC, '  + \
                    'SL, SO, ZA, SS, SD, TG, TN, UG, TZ, EH, ZM, ZW, NA'
        return geoIdList

    @staticmethod
    def get_pygal_oceania_geoid_list():
        """Returns a list of GeoIDs of Oceanian countries that are available in PayGal and 
        the WHO data. 
        Be aware:
        Not all countries of the WHO are available in PayGal and some names are different 
        (GB in PyGal = UK in WHO, GR in PyGal = EL in WHO). PyGal uses lower case and WHO
        upper case. 

        Returns:
            list: List of strings of GeoID's
        """
        # just the main countries for a map
        geoIDs = re.split(r',\s*', CovidCasesWHO.get_pygal_oceania_geoid_string_list().upper())
        return geoIDs

    @staticmethod
    def get_pygal_oceania_geoid_string_list():
        """
        Returns a comma separated list of GeoIDs of Oceanian countries that are available in 
        PayGal and the WHO data. 
        Be aware:
        Not all countries of the WHO are available in PayGal and some names are different 
        (GB in PyGal = UK in WHO, GR in PyGal = EL in WHO). PyGal uses lower case and WHO
        upper case. 

        Returns:
            str: A comma separate list of GeoID's
        """
        # just the main oceania countries for a map, pygal doesn't contain e.g. 
        # Comoros (KM)
        geoIdList = 'AU, FJ, PF, GU, NC, NZ, MP, PG'
        return geoIdList
