import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os
import time
from datetime import timedelta, date
from CovidCases import CovidCases
from CovidCasesECDC import CovidCasesECDC
from CovidCasesOWID import CovidCasesOWID
from CovidCasesWHOv1 import CovidCasesWHOv1
from CovidCasesWHO import CovidCasesWHO
from PlotterBuilder import PlotterBuilder
import CovidMap as dfm
from IPython.display import SVG, display

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
    attribute = 'R7'
    # plot
    (PlotterBuilder(attribute)
        .set_title(attribute)
        #.set_log()
        .set_grid()
        .set_yaxis_formatter(mpl.ticker.StrMethodFormatter('{x:,.2f}'))
        .plot_dataFrame(df))

    # the name of the attribute we want to plot
    attribute = 'VaccineDosesAdministered'
    # plot
    (PlotterBuilder(attribute)
        .set_title(attribute)
        .set_log()
        .set_grid()
        .plot_dataFrame(df))

    # the name of the attribute we want to plot
    attribute = 'PercentPeopleReceivedFirstDose'
    # plot
    (PlotterBuilder(attribute)
        .set_title(attribute)
        #.set_log()
        .set_grid()
        .set_yaxis_formatter(mpl.ticker.PercentFormatter())
        .plot_dataFrame(df))

    # the name of the attribute we want to plot
    attribute = 'PercentPeopleReceivedAllDoses'
    # plot
    (PlotterBuilder(attribute)
        .set_title(attribute)
        #.set_log()
        .set_grid()
        .set_yaxis_formatter(mpl.ticker.PercentFormatter())
        .plot_dataFrame(df))

    # the name of the attribute we want to plot
    attribute = 'DailyVaccineDosesAdministered7DayAverage'
    # plot
    (PlotterBuilder(attribute)
        .set_title(attribute)
        #.set_log()
        .set_grid()
        .plot_dataFrame(df))

def plot_map(theClass):
    # the root of the output directory
    outputDirectory = str(os.path.expanduser('~/Desktop')) 
    # the list of comma separated geoIDs for the major European countries
    countryListAll = theClass.get_pygal_american_geoid_string_list() + ',' + \
                     theClass.get_pygal_european_geoid_string_list() + ',' + \
                     theClass.get_pygal_african_geoid_string_list() + ',' + \
                     theClass.get_pygal_oceania_geoid_string_list() + ',' + \
                     theClass.get_pygal_asian_geoid_string_list()  
    # get the dataframe for these countries
    dfAll = theClass.get_data_by_geoid_string_list(countryListAll)
    # create a map for the dataframe
    map = dfm.CovidMap(dfAll)
    # a list of requested maps
    gis = []
    # append maps to be generated
    gis.append(dfm.mapInfo("Cases", 'Accumulated confirmed cases', outputDirectory))
    # select a date
    theDay = date.today() - timedelta(days=4)
    for gi in gis:
        # generate the map
        result = map.create_map_for_date(gi, theDay)

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
lastN = 90

# the list of comma separated geoIDs
countryList = 'DE, GB, FR, ES, IT, CH, AT, EL'

# create instances
#covidCases_ecdc = CovidCasesECDC(pathToCSV_ecdc)
covidCases_owid = CovidCasesOWID(pathToCSV_owid)
#covidCases_whov1 = CovidCasesWHOv1(pathToCSV_whov1)
covidCases_who = CovidCasesWHO(pathToCSV_who)

# create tuples of instances and country codes
#objList = [covidCases_owid]
objList = [covidCases_owid, covidCases_who]

# get the combined dataframe
df = CovidCases.create_combined_dataframe_by_geoid_string_list(objList, countryList, lastNdays=lastN)

width = 7
for obj in objList:
    # add lowpass filtered DailyCases
    df = obj.add_lowpass_filter_for_attribute(df, 'DailyCases', width)
    # add r0
    df = obj.add_r0(df)
    # add lowpass filtered R
    df = obj.add_lowpass_filter_for_attribute(df, "R", 7)

# plot it
plot_the_data (df)
# show the plot
plt.show()
