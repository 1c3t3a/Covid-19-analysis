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

# the countries that what to analyse
text = "DE"
data = []
geoIDs = re.split(r",\s*", text)
# the period, don't forget it doesn't make sense to calculate R for the exponential phase
lastNdays = 60
# collect the data for all country codes
for geoID in geoIDs:
    countryData = covidCases.get_country_data_by_geoID(geoID, lastNdays=lastNdays)
    # we will create 2 blocks and sum the data of each block
    blockSize = 4
    # for the first 2 blocks we don't get a result 
    for i in range(0, 2 * blockSize - 1):
        countryData[i].update({'R0': math.nan})
    for i in range(2 * blockSize - 1, lastNdays):
        # init the sum of each block
        sum0 = 0
        sum1 = 0
        for n in range(0, blockSize):
            # the index of the first block
            index0 = i - n
            # the index of the second block
            index1 = i - n - blockSize
            # the sum of each of the blocks
            sum0 = sum0 + int(countryData[index0]['Cases'])
            sum1 = sum1 + int(countryData[index1]['Cases'])
            #print ("data: " + str(i) + " index0: " + str(index0) + " index1: " + str(index1))
        # R based on the sum of the two blocks
        R = sum0 / sum1
        # add the result to the dataset
        countryData[i].update({'R0': R})
        #print('0-3: ' + str(sum0) + ' 4-7: ' + str(sum1) + " R: " + str(R))
    # the size of a lowpass
    filterSize = 7
    # remember we don't have R for the first two blocks pluse the length of the filter
    offset = filterSize - 1 + 2 * blockSize - 1
    # we don't have a result for the first data
    for i in range(0, offset):
        countryData[i].update({'R0 filtered': math.nan})
    # enumarate the data
    for i in range(offset, lastNdays):
        # init the sum
        sum3 = 0
        # sum it up
        for n in range(0, filterSize):
            sum3 = sum3 + float(countryData[i - n]['R0'])
        # take the average
        sum3 = sum3 / filterSize
        # add it to the dataset
        countryData[i].update({'R0 filtered': sum3})
    data.append(countryData)
# get the data for all countries
dfdata = [pd.DataFrame(country_data) for country_data in data]
# concatinate to one list
df = pd.concat(dfdata)
# ensure the type of the 'Date' field
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
print(df)
# plot filtered R0 cases
(PlotterBuilder('R0 filtered')
     .set_title('Filtered reproduction rate')
     #.set_xaxis_index()
     .set_grid()
     .set_axis_labels(xlabel="Last " + str(lastNdays) + " days")
     .plot_dataFrame(df))
# plot R0
(PlotterBuilder('R0')
     .set_title('Reproduction rate R0')
     #.set_xaxis_index()
     .set_grid()
     .set_axis_labels(xlabel="Last " + str(lastNdays) + " days")
     .plot_dataFrame(df))
plt.show()