import os
from datetime import date
import requests


def get_JSON_filename():
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


try:
    print(get_JSON_filename())
except FileNotFoundError:
    print('Unable to download the database. Try again later.')
except IOError:
    print('Error writing file.')