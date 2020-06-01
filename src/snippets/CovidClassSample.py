import datetime
from datetime import date
import math
import requests
import json
import os
from json import load, dumps
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from pandas.io.json import json_normalize
import re
import matplotlib.ticker as ticker
from CovidCases import CovidCases
from PlotterBuilder import PlotterBuilder


def get_JSON_filename():
    """
    automatically downloads the database file if it doesn't exists
    """
    # todays date
    today = date.today()
    # the prefix of the JSON file is Y-m-d
    preFix = today.strftime("%Y-%m-%d")
    # the absolut directory of this python file
    absDirectory = os.path.dirname(os.path.abspath(__file__))
    # the target filename
    targetFilename = os.path.join(absDirectory, "../data/" + preFix + "-db.json")
    print('target file: ', targetFilename)
    # check if it exist already
    if os.path.exists(targetFilename):
        print('using existing file: ' + targetFilename)
    else:
        # doownload the file from the ecdc server
        url = "https://opendata.ecdc.europa.eu/covid19/casedistribution/json/"
        r = requests.get(url)
        if r.status_code == 200:
            with open(targetFilename, 'wb') as f:
                f.write(r.content)
        else:
            raise FileNotFoundError('Error getting JSON file. Error code: ' + str(r.status_code))
    return targetFilename

# get the latests database file
try:
    pathToJson = get_JSON_filename()
except FileNotFoundError:
    print('Unable to download the database. Try again later.')
except IOError:
    print('Error writing file.')

# create an instance
covidCases = CovidCases(pathToJson)

# add the text input widget and display it
text = "DE, FR, ES, UK, JP, IT, SG"
data = []
geoIDs = re.split(r",\s*", text)
numCasesStart = 500
# collect the data for all country codes
for geoID in geoIDs:
    countryData = covidCases.get_country_data_by_geoID(geoID, sinceNcases=numCasesStart)
    data.append(countryData)
# get the data
dfdata = [pd.DataFrame(country_data) for country_data in data]
# concatinate to one list
df = pd.concat(dfdata)
# ensure the type of the 'Date' field
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

# plot cumulated cases
(PlotterBuilder('CumulativeCases')
     .set_title('Cumulated cases')
     .set_xaxis_index()
     .set_grid()
     .set_axis_labels(xlabel="Days since case " + str(numCasesStart))
     .plot_dataFrame(df))

# plot cumulated cases
(PlotterBuilder('CumulativeCases')
     .set_title('Logarithmic cumulated cases')
     .set_xaxis_index()
     .set_grid()
     .set_log()
     .set_axis_labels(xlabel="Days since case " + str(numCasesStart))
     .plot_dataFrame(df))

plt.show()