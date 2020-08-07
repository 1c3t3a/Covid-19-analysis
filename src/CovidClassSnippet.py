import datetime
from datetime import date
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from CovidCases import CovidCases
from PlotterBuilder import PlotterBuilder


# get the latests database file as a CSV
try:
    pathToCSV = CovidCases.download_CSV_file()
except FileNotFoundError:
    pathToCSV = "data/db.csv"
    print('Unable to download the database. Try again later.')
except IOError:
    pathToCSV = "data/db.csv"
    print('Error writing file.')

# the list of comma separated geoIDs
countryList = 'DE, IT, SE, BR, US'

# just in case we want to use some optionals
numCasesStart = 500
lastN = 120

# create an instance
covidCases = CovidCases(pathToCSV)
# get the dataframe for our countries
df = covidCases.get_country_data_by_geoid_string_list(countryList, sinceNcases=numCasesStart)
# the name of the attribute we want to plot
attribute = 'Cases'
# plot
(PlotterBuilder(attribute)
     .set_title(attribute)
     .set_xaxis_index()
     #.set_log()
     .set_grid()
     .set_axis_labels(xlabel='Days since case ' + str(numCasesStart))
     .plot_dataFrame(df))

# lowpass the attribute
width = 7
df = covidCases.add_lowpass_filter_for_attribute(df, attribute, width)
# the name of the attribute we want to plot
attribute = attribute + str(width)
# plot
(PlotterBuilder(attribute)
     .set_title(attribute)
     .set_xaxis_index()
     #.set_log()
     .set_grid()
     .set_axis_labels(xlabel='Days since case ' + str(numCasesStart))
     .plot_dataFrame(df))

# the name of the attribute we want to plot
df = covidCases.add_r0(df)
attribute = 'R'
# plot
(PlotterBuilder(attribute)
     .set_title(attribute)
     #.set_xaxis_index()
     #.set_log()
     .set_grid()
     .set_axis_labels(xlabel='Days since case ' + str(numCasesStart))
     .plot_dataFrame(df))

df = covidCases.add_lowpass_filter_for_attribute(df, attribute, width)
# the name of the attribute we want to plot
attribute = attribute + str(width)
# plot
(PlotterBuilder(attribute)
     .set_title(attribute)
     #.set_xaxis_index()
     #.set_log()
     .set_grid()
     .set_axis_labels(xlabel='Days since case ' + str(numCasesStart))
     .plot_dataFrame(df))

# show the plot
plt.show()
