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

# terms and their description from the OWID website:
#total_vaccinations	
# National government reports	
# Total number of COVID-19 vaccination doses administered

#people_vaccinated	
# National government reports	
# Total number of people who received at least one vaccine dose

#people_fully_vaccinated	
# National government reports	
# Total number of people who received all doses prescribed by the vaccination protocol

#new_vaccinations	
# National government reports	
# New COVID-19 vaccination doses administered (only calculated for consecutive days)

#new_vaccinations_smoothed	
# National government reports	
# New COVID-19 vaccination doses administered (7-day smoothed). For countries that don't report vaccination data on a daily basis, we assume that vaccination changed equally on a daily basis over any periods in which no data was reported. This produces a complete series of daily figures, which is then averaged over a rolling 7-day window

#total_vaccinations_per_hundred	
# National government reports	
# Total number of COVID-19 vaccination doses administered per 100 people in the total population

#people_vaccinated_per_hundred	
# National government reports	
# Total number of people who received at least one vaccine dose per 100 people in the total population

#people_fully_vaccinated_per_hundred	
# National government reports	
# Total number of people who received all doses prescribed by the vaccination protocol per 100 people in the total population

#new_vaccinations_smoothed_per_million	
# National government reports	
# New COVID-19 vaccination doses administered (7-day smoothed) per 1,000,000 people in the total population

class CovidCasesOWID(CovidCases):
    """The class will expose data attributes in form of a DataFrame. Its base class also provides methods to process 
    the data which will end up in additional columns in the DataFrame. These are the name sof the columns
    that are generated. Notice: The 'Continent' column is additionally and specific to this sub class

    Date
    The date of the data 
    
    GeoID
    The GeoID of the country such as FR for France or DE for Germany

    GeoName
    The name of the country

    Population
    The population of the country

    Continent
    The continent of the country

    DailyCases
    The number of new cases on a given day

    DailyDeaths
    The number of new deaths on the given date

    DailyVaccineDosesAdministered7DayAverage
    New COVID-19 vaccination doses administered (7-day smoothed). For countries that 
    don't report vaccination data on a daily basis, we assume that vaccination 
    changed equally on a daily basis over any periods in which no data was reported. 
    This produces a complete series of daily figures, which is then averaged over a 
    rolling 7-day window. 
    In OWID words this is the new_vaccinations_smoothed value.
                              
    PeopleReceivedFirstDose
    Total number of people who received at least one vaccine dose.
    In OWID words this is the people_vaccinated value.

    PeopleReceivedAllDoses
    Total number of people who received all doses prescribed by the vaccination protocol.
    In OWID words this is the people_fully_vaccinated value.

    VaccineDosesAdministered
    Total number of COVID-19 vaccination doses administered. It's the sum of 
    PeopleReceivedFirstDose and PeopleReceivedAllDoses.
    In OWID words this is the total_vaccinations value.

    Continent
    The continent of the country as an additional column.
    
    Returns:
        CovidCasesOWID: A class to provide access to some data based on the OWID file.
    """

    def __init__(self, filename):
        """The constructor takes a string containing the full filename of a CSV
        database you can download from the OWID website:
        https://covid.ourworldindata.org/data/owid-covid-data.csv
        The database will be loaded and kept as a private member. To retrieve the
        data for an individual country you can use the public methods
        GetCountryDataByGeoID or GetCountryDataByCountryName. These functions take 
        ISO 3166 alpha_2 (2 characters long) GeoIDs.

        Args:
            filename (str): The full path and name of the csv file. 
        """
        # some benchmarking
        start = time.time()
        # open the file
        self.__df = pd.read_csv(filename)
        # remove columns that we don't need
        self.__df = self.__df.drop(columns=['total_cases', 
                                            'new_cases_smoothed', 
                                            'total_deaths', 
                                            'new_deaths_smoothed', 
                                            'total_cases_per_million',
                                            'new_cases_per_million',
                                            'new_cases_smoothed_per_million',
                                            'total_deaths_per_million',
                                            'new_deaths_per_million',
                                            'new_deaths_smoothed_per_million',
                                            'reproduction_rate',
                                            'icu_patients',
                                            'icu_patients_per_million',
                                            'hosp_patients',
                                            'hosp_patients_per_million',
                                            'weekly_icu_admissions',
                                            'weekly_icu_admissions_per_million',
                                            'weekly_hosp_admissions',
                                            'weekly_hosp_admissions_per_million',
                                            'new_tests',
                                            'total_tests',
                                            'total_tests_per_thousand',
                                            'new_tests_per_thousand',
                                            'new_tests_smoothed',
                                            'new_tests_smoothed_per_thousand',
                                            'positive_rate',
                                            'tests_per_case',
                                            'tests_units',
                                            #'total_vaccinations',
                                            'total_vaccinations_per_hundred',
                                            'stringency_index',
                                            'population_density',
                                            'median_age',
                                            'aged_65_older',
                                            'aged_70_older',
                                            'gdp_per_capita',
                                            'extreme_poverty',
                                            'cardiovasc_death_rate',
                                            'diabetes_prevalence',
                                            'female_smokers',
                                            'male_smokers',
                                            'handwashing_facilities',
                                            'hospital_beds_per_thousand',
                                            'life_expectancy',
                                            'human_development_index',
                                            # three more columns have been introduced
                                            'new_vaccinations',
                                            #'new_vaccinations_smoothed',
                                            'new_vaccinations_smoothed_per_million',
                                            #'people_fully_vaccinated',
                                            'people_fully_vaccinated_per_hundred',
                                            #'people_vaccinated',
                                            'people_vaccinated_per_hundred',
                                            # again a new field
                                            'excess_mortality',
                                            # and of course some new fields
                                            'total_boosters',
                                            'total_boosters_per_hundred',
                                            # some more
                                            'excess_mortality_cumulative_absolute',
                                            'excess_mortality_cumulative',
                                            'excess_mortality_cumulative_per_million',
                                            'excess_mortality',
                                            'new_people_vaccinated_smoothed',
                                            'new_people_vaccinated_smoothed_per_hundred'])
        if self.__df.columns.size != 11:
            # oops, there are some new columns in the csv
            print('Detecting new cols in OWID CSV: ' + self.__df.columns)
            # add the new cols to a list
            cols = [self.__df.columns[col] for col in range (11, self.__df.columns.size)]
            # ...and drop them
            self.__df = self.__df.drop(columns=cols)
            print('Accepting cols in OWID CSV: ' + self.__df.columns)
        # rename the columns to be more readable
        self.__df.columns = ['GeoID',
                             'Continent',
                             'GeoName',
                             'Date',
                             'DailyCases',
                             'DailyDeaths',
                             'VaccineDosesAdministered',
                             'PeopleReceivedFirstDose',
                             'PeopleReceivedAllDoses',
                             'DailyVaccineDosesAdministered7DayAverage',
                             'Population']
        #print(self.__df.columns)
        # change the type of the 'date' field to a pandas date
        self.__df['Date'] = pd.to_datetime(self.__df['Date'],
                                           format='%Y/%m/%d')
        # re-order the columns to be similar for all sub-classes                                   
        self.__df = self.__df[['Date', 
                              'GeoName', 
                              'GeoID', 
                              'Population', 
                              'Continent', 
                              'DailyCases',
                              'DailyDeaths',
                              'DailyVaccineDosesAdministered7DayAverage',
                              'PeopleReceivedFirstDose',
                              'PeopleReceivedAllDoses',
                              'VaccineDosesAdministered']]
        #print(self.__df)
        df = self.__df
        # to apply the country names from our internal list
        giw = GeoInformationWorld()
        # get all country info
        dfInfo = giw.get_geo_information_world()
        # we need the newest date being on top, get all GeoIDs in the df
        geoIDs = df['GeoID'].unique()
        # our result data frame
        dfs = []
        for geoID in geoIDs:
            # 'nan' workaround
            if str(geoID) == 'nan':
                # nothing else worked to detect this nan (it's the 'international' line in the file that doesn't have any GeoIds)
                continue
            # get the country dataframe
            dfSingleCountry = df.loc[df['GeoID'] == geoID].copy()
            # reset the index to start from index = 0
            dfSingleCountry.reset_index(inplace=True, drop=True)
            dfSingleCountry = dfSingleCountry.reindex(index=dfSingleCountry.index[::-1])  
            # 'Kosovo' workaround
            if geoID == 'OWID_KOS':
                geoID = 'KOS'
            # 'OWID World' workaround
            if geoID == 'OWID_WRL':
                continue
            # get the geoName for this geoID from our internal list
            geoName = giw.geo_name_from_ISO3166_alpha_3(geoID)
            # get the alpha-2 geoID from the alpha-3 geoID
            geoID2 = giw.geoID_from_ISO3166_alpha_3(geoID)
            # the current name         
            curName = dfSingleCountry['GeoName'][0]
            # replace it if necessary
            if geoName != curName:
                dfSingleCountry['GeoName'] = [geoName for _ in range(0, len(dfSingleCountry['GeoID']))]
            # now overwrite the alpha-3 geoID with the alpha-2 geoID so all sublasses can use the same geoIDs
            dfSingleCountry['GeoID'] = [geoID2 for _ in range(0, len(dfSingleCountry['GeoID']))]    
            # add the country to the result
            dfs.append(dfSingleCountry)
        # done, keep the list
        self.__df = pd.concat(dfs)
        # some benchmarking
        end = time.time()
        print('Pandas loading the OWID CSV: ' + str(end - start) + 's')
        # pass the dataframe to the base class
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
        preFix = today.strftime('%Y-%m-%d') + "-OWID"
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
            url = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
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
        info = ["Our World In Data", 
                "OWID",
                "https://covid.ourworldindata.org/data/owid-covid-data.csv"]
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
        geoIDs = re.split(r',\s*', CovidCasesOWID.get_pygal_european_geoid_string_list().upper())
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
        geoIDs = re.split(r',\s*', CovidCasesOWID.get_pygal_american_geoid_string_list().upper())
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
        geoIdList = 'AR, BB, BM, BO, BR, BS, CA, CL, CO, ' + \
                    'CR, CU, DO, EC, SV, GT, GY, HN, HT, ' + \
                    'JM, MX, NI, PA, PE, PR, PY, SR, US, UY, VE'
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
        geoIDs = re.split(r',\s*', CovidCasesOWID.get_pygal_asian_geoid_string_list().upper())
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
                    'QA, SA, SG, KR, LK, SY, TW, TJ, TH, TL, TR, AE, UZ, VN, YE, IN, ID'
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
        geoIDs = re.split(r',\s*', CovidCasesOWID.get_pygal_african_geoid_string_list().upper())
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
        # 2022-01-20 added NA
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
        geoIDs = re.split(r',\s*', CovidCasesOWID.get_pygal_oceania_geoid_string_list().upper())
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
