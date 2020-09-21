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
countryList = 'DE, IT, ES, UK, FR, AT, NL'

# just in case we want to use some optionals
numCasesStart = 500
lastN = 40

# create an instance
covidCases = CovidCases(pathToCSV)
# get the dataframe for our countries
#df = covidCases.get_country_data_by_geoid_string_list(countryList, sinceNcases=numCasesStart)
df = covidCases.get_country_data_by_geoid_string_list(countryList, lastNdays=lastN)
#df = covidCases.get_country_data_by_geoid_string_list(countryList)  

# the name of the attribute we want to plot
attribute = 'DailyCases'
# plot
(PlotterBuilder(attribute)
     .set_title(attribute)
     .set_xaxis_index()
     #.set_log()
     .set_grid()
     .set_axis_labels(xlabel='Days since case ' + str(numCasesStart))
     .plot_dataFrame(df))

df = covidCases.add_incidence_7day_per_100Kpopulation(df)
attribute = 'Incidence7DayPer100Kpopulation'
# plot
(PlotterBuilder(attribute)
     .set_title(attribute)
     #.set_xaxis_index()
     #.set_log()
     .set_grid()
     .set_axis_labels(xlabel='Days since case ' + str(numCasesStart))
     .plot_dataFrame(df))

# the name of the attribute we want to plot
attribute = 'DailyCases'
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

# show the plot
plt.show()
