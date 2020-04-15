import json
import datetime
import math
from pprint import pprint
from json import load, dumps
import pandas as pd
from pandas.io.json import json_normalize


# a class
class CovidCases:
    # get a subset of fields
    def __GetFields (self, record):
        return {
            "Country": record["countriesAndTerritories"],
            "GeoID": record["geoId"],
            "Date": record["dateRep"],
            "Cases": record["cases"],
            "Deaths": record["deaths"]
        }

    # constructor
    def __init__(self, filename):
        # the database can be downloaded as a JSON from https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide
        # open the file and read the 'records'  
        with open(filename) as f:
            self.__db = load(f)["records"]
        # map the subset
        #__db = [GetFields (r) for r in db]
        self.__db = list (map(lambda x : self.__GetFields(x), self.__db))
        # dump the database
        #print(dumps(self.__db))

    # get all records 
    def __GetAllRecords(self, f):
        return lambda y: all([x(y) for x in f])

    # add some specific  fields
    def __AddExtraFields(self, subset):
        # the length of the list
        n = len(subset)
        # add a col to the first element having the number of cases
        subset[0].update({'Cumultative': int(subset[0]['Cases'])})
        # loop through the list starting at index 1
        for x in range (1, n - 1):
            # the cumultative ncases of day n-1
            dayNm1Cum = int(subset[x-1]['Cumultative'])
            # the cases of day n
            dayN = int(subset[x]['Cases'])
            # the cumultative cases of day n
            dayNCum = dayNm1Cum + dayN
            subset[x].update({'Cumultative':  dayNCum})
            # the quuotient of day(n) / day(n-1)
            if dayNm1Cum != 0:
                subset[x].update({'Quotient':  dayNCum / dayNm1Cum})
            else:
                subset[x].update({'Quotient':  math.nan})
            quotient = float(subset[x]['Quotient'])
            # the doubling time in days
            if quotient != 1.0 and quotient != math.nan:
                subset[x].update({'DoublingTime':  math.log(2) / math.log(quotient)})
            else:
                subset[x].update({'DoublingTime':  math.nan})
            #print(subset[x])
        return subset

    # return the list of cases by geoID
    def GetCountryDataByGeoID (self, geoID):
        # specify the filter
        filters = []
        filters.append(lambda r: r["GeoID"] == geoID)
        # apply the filter
        subset = list(filter( self.__GetAllRecords(filters), self.__db)) 
        # reverse the list (1st date on top of the list)
        subset.reverse()
        subset = self.__AddExtraFields(subset)
        return subset

    # return the list of cases by country name
    def GetCountryDataByCountryName (self, countryName):
        # specify the filter
        filters = []
        filters.append(lambda r: r["countriesAndTerritories"] == countryName)
        # apply the filter
        subset = list(filter( self.__GetAllRecords(filters), self.__db)) 
        # reverse the list (1st date on top of the list)
        subset.reverse()
        subset = self.__AddExtraFields(subset)
        return subset

# create an instance
covidCases = CovidCases('../../data/db.json')

# modify the country code if required
countryCode = "DE"

# get cases
res = covidCases.GetCountryDataByGeoID(countryCode)

# convert it to a panda dataframe
df = pd.DataFrame(res) 
print(df) 
# print(df)