import datetime
from datetime import date
import math
import matplotlib as mpl
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
import CovidMap as dfm

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
