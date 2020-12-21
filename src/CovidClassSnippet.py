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

def test_all_data(obj, strGeoIDs):
    df = obj.get_data_by_geoid_string_list(strGeoIDs) 
    # the name of the attribute we want to plot
    attribute = 'DailyCases'
    # plot
    (PlotterBuilder(attribute)
        .set_title(attribute)
        #.set_log()
        .set_grid()
        .plot_dataFrame(df))

    # lowpass the attribute
    width = 7
    df = obj.add_lowpass_filter_for_attribute(df, attribute, width)
    # the name of the attribute we want to plot
    attribute = attribute + str(width)
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
    
    # show the plot
    plt.show()

def test_since_data(obj, strGeoIDs, sinceN=500):
    df = obj.get_data_by_geoid_string_list(strGeoIDs, sinceNcases=sinceN) 
    # the name of the attribute we want to plot
    attribute = 'DailyCases'
    # plot
    (PlotterBuilder(attribute)
        .set_title(attribute)
        .set_xaxis_index()
        #.set_log()
        .set_grid()
        .set_axis_labels(xlabel='Days since case ' + str(sinceN))
        .plot_dataFrame(df))

    # lowpass the attribute
    width = 7
    df = obj.add_lowpass_filter_for_attribute(df, attribute, width)
    # the name of the attribute we want to plot
    attribute = attribute + str(width)
    # plot
    (PlotterBuilder(attribute)
        .set_title(attribute)
        .set_xaxis_index()
        #.set_log()
        .set_grid()
        .set_axis_labels(xlabel='Days since case ' + str(sinceN))
        .plot_dataFrame(df))

    # the name of the attribute we want to plot
    attribute = 'Cases'
    # plot
    (PlotterBuilder(attribute)
        .set_title(attribute)
        .set_xaxis_index()
        #.set_log()
        .set_grid()
        .set_axis_labels(xlabel='Days since case ' + str(sinceN))
        .plot_dataFrame(df))
    
    # show the plot
    plt.show()

# the list of comma separated geoIDs
countryList_owid = 'DEU, ITA'
countryList_ecdc = 'DE, IT'

# just in case we want to use some optionals
numCasesStart = 10000
lastN = 40

# create an instance
covidCases_owid = CovidCasesOWID(pathToCSV_owid)
covidCases_ecdc = CovidCasesECDC(pathToCSV_ecdc)

#test_all_data(countryList)
test_since_data(covidCases_ecdc, countryList_ecdc, 5000)
test_since_data(covidCases_owid, countryList_owid, 5000)
# get the dataframe for our countries
#df = covidCases.get_data_by_geoid_string_list(countryList, sinceNcases=numCasesStart)
#df = covidCases.get_data_by_geoid_string_list(countryList, lastNdays=lastN)
#df = covidCases.get_data_by_geoid_string_list(countryList)  




