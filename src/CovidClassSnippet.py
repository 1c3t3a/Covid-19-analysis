import datetime
from datetime import date
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import time
import datetime
from CovidCases import CovidCases
from CovidCasesECDC import CovidCasesECDC
from CovidCasesOWID import CovidCasesOWID
from CovidCasesWHOv1 import CovidCasesWHOv1
from CovidCasesWHO import CovidCasesWHO
from PlotterBuilder import PlotterBuilder

def create_combined_dataframe(objList, countryList, lastNdays=0, sinceNcases=0):  
    # a final array of dataframes containing all three data
    dfs = []
    # loop through all classes / geoIDs
    for obj in objList:
        # get the data frame
        df = obj.get_data_by_geoid_string_list(countryList, lastNdays, sinceNcases)
        # rename the country and add the source info to the name
        for name in df['GeoName'].unique():
            df.replace(name, name + '-' + obj.get_data_source_info()[1], inplace=True)
        # lowpass the DailyCases attribute
        width = 7
        df = obj.add_lowpass_filter_for_attribute(df, 'DailyCases', width)
        # add it to the list
        dfs.append(df)  
    # finally concatenate all dfs together
    df = pd.concat(dfs)  
    # ...and return it
    return df

def plot_the_data (df):
    # the name of the attribute we want to plot
    attribute = 'DailyCases'
    # plot
    (PlotterBuilder(attribute)
        .set_title(attribute)
        #.set_log()
        .set_grid()
        .plot_dataFrame(df))

    # the name of the attribute we want to plot
    attribute = "DailyCases7"
    # plot
    (PlotterBuilder(attribute)
        .set_title(attribute)
        #.set_log()
        .set_grid()
        .plot_dataFrame(df))

    # the name of the attribute we want to plot
    attribute = 'Cases'
    # plot
    (PlotterBuilder(attribute)
        .set_title(attribute)
        #.set_log()
        .set_grid()
        .plot_dataFrame(df))
    
# get the latests database file as a CSV
try:
    pathToCSV_owid = CovidCasesOWID.download_CSV_file()
    pathToCSV_ecdc = CovidCasesECDC.download_CSV_file()
    pathToCSV_whov1 = CovidCasesWHOv1.download_CSV_file()
    pathToCSV_who = CovidCasesWHO.download_CSV_file()
except FileNotFoundError:
    pathToCSV = "data/db.csv"
    print('Unable to download the database. Try again later.')
except IOError:
    pathToCSV = "data/db.csv"
    print('Error writing file.')

# just in case we want to use some optionals
numCasesince = 10000
lastN = 100

# the list of comma separated geoIDs
countryList = 'DE, GB, FR, ES, IT, CH, AT, EL'

# create instances
covidCases_ecdc = CovidCasesECDC(pathToCSV_ecdc)
covidCases_owid = CovidCasesOWID(pathToCSV_owid)
#covidCases_whov1 = CovidCasesWHOv1(pathToCSV_whov1)
covidCases_who = CovidCasesWHO(pathToCSV_who)

# create tuples of instances and country codes
objList = [covidCases_owid, covidCases_who, covidCases_ecdc]

# get the combined dataframe
df = create_combined_dataframe(objList, countryList)

# plot it
plot_the_data (df)
# show the plot
plt.show()
