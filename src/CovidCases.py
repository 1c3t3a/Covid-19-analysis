import math
from json import load, dumps


class CovidCases:
    """
    The constructor takes a string containing the full filenname of a JSON
    database you can down load from the WHO website:
    https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide

    The database will be loaded and kept as a private member. To retrieve the
    data for an indvidual country you can use the public methods
    GetCountryDataByGeoID or GetCountryDataByCountryName. Refer to the JSON
    file for a list of available GeoIDs and CountryNames. Both methods will
    return a list of the following fields as a JSON:
    
    Date
    The date of the data Country The name of the country
    
    GeoID
    The GeoID of the country such as FR for France or DE for Germany
    
    Cases
    The number of cases on that day
    
    CumultativeCases
    The accumulated number of cases since the 31.12.2019
    
    Quotient
    The number of cases on the day devided by the number of cases of the
    previous day DoublingTime The number of days in which the number of cases
    will be doubled

    Deaths
    The number of deaths on the date
    
    CumultativeDeaths
    The accumulated number of deaths since the 31.12.2019
    
    PercentDeaths
    The number of deaths in % of the cases

    CasesPerMillionPopulation
    The number of cumulative cases devide by the popolation of the countryy in million 
    
    DeathsPerMillionPopulation
    The number of cumulative deaths devide by the popolation of the countr in million
    """

    def __get_common_attributes(self, record):
        """
        get a subset of attributes
        """
        return {
            "Country": record["countriesAndTerritories"],
            "GeoID": record["geoId"],
            "Population": record["popData2018"],
            "Date": record["dateRep"],
            "Cases": record["cases"],
            "Deaths": record["deaths"]
        }

    def __init__(self, filename):
        """
        constructor
        """
        # open the file and read the 'records'
        with open(filename) as f:
            self.__db = load(f)["records"]
        # map the subset
        # __db = [GetFields (r) for r in db]
        self.__db = list(map(lambda x: self.__get_common_attributes(x), self.__db))
        # dump the database
        # print(dumps(self.__db))
    
    def __get_all_records(self, f):
        """
        get all records
        """
        return lambda y: all([x(y) for x in f])

    def __add_extra_atributes(self, subset):
        """
        add some specific attributs
        """
        # the length of the list
        n = len(subset)
        # add a col to the first element having the number of cases
        subset[0].update({'CumultativeCases': int(subset[0]['Cases'])})
        subset[0].update({'CumultativeDeaths': int(subset[0]['Deaths'])})
        subset[0].update({'PercentDeaths': math.nan})
        subset[0].update({'CasesPerMillionPopulation': 0})
        subset[0].update({'DeathsPerMillionPopulation': 0})
        # loop through the list starting at index 1
        for x in range(1, n - 1):
            # the cumultative ncases of day n-1
            dayNm1Cum = int(subset[x-1]['CumultativeCases'])
            # the cases of day n
            dayN = int(subset[x]['Cases'])
            # the cumultative cases of day n
            dayNCum = dayNm1Cum + dayN
            subset[x].update({'CumultativeCases':  dayNCum})
            # the quuotient of day(n) / day(n-1)
            if dayNm1Cum != 0:
                subset[x].update({'Quotient':  dayNCum / dayNm1Cum})
            else:
                subset[x].update({'Quotient':  math.nan})
            quotient = float(subset[x]['Quotient'])
            # the doubling time in days
            if quotient != 1.0 and quotient != math.nan:
                subset[x].update({'DoublingTime': math.log(2) / math.log(quotient)})
            else:
                subset[x].update({'DoublingTime': math.nan})
            # the cumultative deaths of day n-1
            dayNm1CumDeaths = int(subset[x-1]['CumultativeDeaths'])
            # the deatha of day n
            dayN = int(subset[x]['Deaths'])
            # the cumultative deaths of day n
            dayNCumDeaths = dayNm1CumDeaths + dayN
            subset[x].update({'CumultativeDeaths':  dayNCumDeaths})
            # the number of deaths in percent of the cases
            if dayNCum != 0:
                subset[x].update({'PercentDeaths': dayNCumDeaths * 100 / dayNCum})
            else:
                subset[x].update({'PercentDeaths': math.nan})
            # the population in million
            population = int(subset[x]['Population']) / 1000000
            # cases per million
            casesPerMillion = dayNCum / population
            subset[x].update({'CasesPerMillionPopulation':  casesPerMillion})
            # deaths per million
            deathsPerMillion = dayNCumDeaths / population
            subset[x].update({'DeathsPerMillionPopulation':  deathsPerMillion})
            # print(subset[x])
        return subset

    def get_country_data_by_geoID(self, geoID, lastNdays=0, sinceNcases=0):
        """
        return the list of cases by geoID
        """
        # specify the filter
        filters = []
        filters.append(lambda r: r["GeoID"] == geoID)
        # apply the filter
        subset = list(filter(self.__get_all_records(filters), self.__db))
        # reverse the list (1st date on top of the list)
        subset.reverse()
        subset = self.__add_extra_atributes(subset)
        if lastNdays > 0:
            start_index = len(subset) - lastNdays
            subset = subset[start_index:]
        if sinceNcases > 0:
            # loop through the list
            while len(subset) > 0:
                # the cumultative ncases of x
                numCum = int(subset[0]['CumultativeCases'])
                if numCum < sinceNcases:
                    # delete it
                    subset.pop(0)
                else:
                    # we are done
                    break
            # the length of the list
            n = len(subset)
            # add the index col
            for x in range(0, n - 1):
                subset[x].update({'Index': int(x)})
        return subset

    def get_country_data_by_country_name(self, countryName, lastNdays=0):
        """
        return the list of cases by country name
        """
        # specify the filter
        filters = []
        filters.append(lambda r: r["countriesAndTerritories"] == countryName)
        # apply the filter
        subset = list(filter(self.__get_all_records(filters), self.__db))
        # reverse the list (1st date on top of the list)
        subset.reverse()
        # add additonal fields
        subset = self.__add_extra_atributes(subset)
        if lastNdays > 0:
            start_index = len(subset) - lastNdays
            subset = subset[start_index:]
        return subset
