import datetime
from datetime import date
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from CovidCases import CovidCases
from CovidCasesECDC import CovidCasesECDC
from CovidCasesOWID import CovidCasesOWID
from PlotterBuilder import PlotterBuilder
import pycountry

# get the latests database file as a CSV
try:
    pathToCSV_owid = CovidCasesOWID.download_CSV_file()
    pathToCSV_ecdc = CovidCasesECDC.download_CSV_file()
except FileNotFoundError:
    pathToCSV = "data/db.csv"
    print('Unable to download the database. Try again later.')
except IOError:
    pathToCSV = "data/db.csv"
    print('Error writing file.')

# the list of comma separated geoIDs
countryList_owid = 'DEU, ITA, FRA, GBR'
countryList_ecdc = 'DE, IT, FR, UK'

# create instances
covidCases_owid = CovidCasesOWID(pathToCSV_owid)
covidCases_ecdc = CovidCasesECDC(pathToCSV_ecdc)

# we are now using this class
covidCases = covidCases_owid

#df = covidCases_ecdc.get_data_by_geoid_string_list('US, DE')
#df = covidCases_owid.get_data_by_geoid_string_list('USA, DEU')
#print(df)

#df.reset_index(inplace=True, drop=False)
#df['GeoName'] = df.apply(covidCases._replace_country_name, axis = 1)
#print(df)

# get the list of available geoids
lst = covidCases.get_available_GeoID_list()
# get the list of ISO 3166 alpha 2 codes
lst_alpha_2 = [i.alpha_2 for i in list(pycountry.countries)]
# get the list of ISO 3166 alpha 3 codes
lst_alpha_3 = [i.alpha_3 for i in list(pycountry.countries)]    

def add_country_name(df):
    # check if the GeoID string exist
    if pd.isnull(df['GeoID']):
        return 'Invalid GeoID'
    # the geoid
    geoID = df['GeoID']
    # return the name
    if (len(geoID) == 2 and geoID in lst_alpha_2):
        return pycountry.countries.get(alpha_2 = geoID).name
    elif (len(geoID) == 3 and geoID in lst_alpha_3):
        return pycountry.countries.get(alpha_3 = geoID).name
    else:
        return 'Invalid GeoID'

def add_country_alpha2(df):
    # check if the GeoID string exist
    if pd.isnull(df['GeoID']):
        return 'Invalid GeoID'
    # the geoid
    geoID = df['GeoID']
    # return the alpha_2
    if (len(geoID) == 2 and geoID in lst_alpha_2):
        return pycountry.countries.get(alpha_2 = geoID).alpha_2
    elif (len(geoID) == 3 and geoID in lst_alpha_3):
        return pycountry.countries.get(alpha_3 = geoID).alpha_2
    else:
        return 'Invalid GeoID'

def add_country_alpha3(df):
    # check if the GeoID string exist
    if pd.isnull(df['GeoID']):
        return 'Invalid GeoID'
    # the geoid
    geoID = df['GeoID']
    # return the alpha_3
    if (len(geoID) == 2 and geoID in lst_alpha_2):
        return pycountry.countries.get(alpha_2 = geoID).alpha_3
    elif (len(geoID) == 3 and geoID in lst_alpha_3):
        return pycountry.countries.get(alpha_3 = geoID).alpha_3
    else:
        return 'Invalid GeoID'

print(lst)

# add the name (to generate a csv the commas should be deleted afterwards)
lst['Name'] = lst.apply(add_country_name, axis = 1)
# add the alpha_2 values
lst['ISO-3166-alpha_2'] = lst.apply(add_country_alpha2, axis = 1)
# add the alpha_3 values
lst['ISO-3166-alpha_3'] = lst.apply(add_country_alpha3, axis = 1)

print(lst)
lst.to_csv('~/tmp.csv')

# afterwards 
# - remove the GeoName column from the file,  
# - rename the 'Name' column to 'GeoName'
# - remove the commas and everythin behind them from the GeoNames

# before you start edit CovidCasesECDC.get_available_GeoID_list and return the 'Population' instead of the 'GeoName'
