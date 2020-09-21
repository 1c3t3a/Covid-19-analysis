from typing import Optional
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import io
import requests
from datetime import date
import os
import sys
from starlette.responses import StreamingResponse
from fastapi import FastAPI, HTTPException
from enum import Enum
# append the src directory to the sys path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from CovidCases import CovidCases
from PlotterBuilder import PlotterBuilder


class Attributes(Enum):
    """
    Enumeration of all available plotable attributes.
    """
    DailyCases = 'DailyCases'
    DailyCases7 = 'DailyCases7'
    Incidence7DayPer100Kpopulation = 'Incidence7DayPer100Kpopulation'
    Cases = 'Cases'
    CasesPerMillionPopulation = 'CasesPerMillionPopulation'
    DailyDeaths = 'DailyDeaths'
    DailyDeaths7 = 'DailyDeaths7'
    Deaths = 'Deaths'
    PercentDeaths = 'PercentDeaths'
    DeathsPerMillionPopulation = 'DeathsPerMillionPopulation'
    DoublingTime = 'DoublingTime'
    DoublingTime7 = 'DoublingTime7'
    R = 'R'
    R7 = 'R7'

class AttributeTitles(Enum):
    """
    Enumeration of the documentation of all available plotable attributes.
    """
    DailyCases = 'Daily confirmed cases'
    DailyCases7 = 'Daily confirmed cases: 7-day rolling average'
    Incidence7DayPer100Kpopulation = '7-day incidence per 100.000 population'
    Cases = 'Accumulated cases'
    CasesPerMillionPopulation = 'Accumulated cases per million population'
    DailyDeaths = 'Daily deaths'
    DailyDeaths7 = 'Daily deaths: 7-day rolling average'
    Deaths = 'Accumulated deaths'
    PercentDeaths = 'Percent deaths of the accumulated cases'
    DeathsPerMillionPopulation = 'Deaths per million population'
    DoublingTime = 'Doubling time'
    DoublingTime7 = 'Doubling time: 7-day rolling average'
    R = 'Reproduction rate'
    R7 = 'Reproduction rate: 7-day rolling average'

class Rest_API:

    def generate_plot(self, geo_ids, wanted_attrib, log=False, last_n=-1, since_n=-1, bar=False):
        """
        Generates a plot for given GeoIds and returns it in form of a byteIO stream
        Parameters:
            geo_ids: [String] -> countries that should be plotted
            wanted_attrib: String -> the field you want to plot, e.g. Cases
            log: bool -> should the plot be logarithmic
            last_n: int -> plot the last n days, if not further specified all available data is plotted
            since_n: int -> plot since the nth case, if not further specified all available data is plotted
        """
        # load the cases
        csv_file = CovidCases.download_CSV_file()
        self.covid_cases = CovidCases(csv_file)

        # try to collect the data for given geoIds, if a wrong geoId is passed, the operation will abort with a 400
        # bad request error
        try:
            df = self.covid_cases.get_country_data_by_geoid_list(
                geo_ids, lastNdays=last_n, sinceNcases=since_n)
        except IndexError:
            raise HTTPException(
                status_code=400, detail="Couldn't load data")

        # if the wanted attribute is one that need to be calculated, calculate it
        if wanted_attrib == Attributes.R or Attributes.R7:
            df = self.covid_cases.add_r0(df)
        if wanted_attrib == Attributes.R7:
            df = self.covid_cases.add_lowpass_filter_for_attribute(df, 'R', 7)
        if wanted_attrib == Attributes.DailyCases7:
            df = self.covid_cases.add_lowpass_filter_for_attribute(
                df, 'DailyCases', 7)
        if wanted_attrib == Attributes.DailyDeaths7:
            df = self.covid_cases.add_lowpass_filter_for_attribute(
                df, 'DailyDeaths', 7)
        if wanted_attrib == Attributes.DoublingTime7:
            df = self.covid_cases.add_lowpass_filter_for_attribute(
                df, 'DoublingTime', 7)
        if wanted_attrib == Attributes.Incidence7DayPer100Kpopulation:
            df = self.covid_cases.add_incidence_7day_per_100Kpopulation(
                df)

        # concat to one DataFrame and set date
        df[['Date']] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
        # create pivot table with all needed values, if the x-axis shows a timedelta with days since the nth case the index
        # has to change
        pldf = df.pivot_table(values=wanted_attrib.name, index='Date', columns='Country') if since_n == -1 \
            else df.pivot_table(values=wanted_attrib.name, index=df.index, columns='Country')


        # use the PlotterBuilder to set up the plot
        builder = (PlotterBuilder(wanted_attrib)
                   #.set_title(re.sub(r"([a-z])([A-Z])", r"\g<1> \g<2>", wanted_attrib.name))
                   .set_title(AttributeTitles[wanted_attrib.value].value)
                   .set_grid())
        if log:
            builder.set_log()
        if since_n != -1:
            # if the plot has a timedelta on the x-axis, the label has to be reset
            builder.set_axis_labels(
                xlabel="Days since case " + str(since_n))
            builder.set_xaxis_index()
        # generate plot
        fig, ax = builder.build()
        if bar:
            pldf.plot(ax=ax, kind='bar')
        else:
            pldf.plot(ax=ax)
            ax.grid()
        # write image to io stream
        byte_io = io.BytesIO()
        plt.savefig(byte_io, dpi=fig.dpi)
        byte_io.seek(0)

        return byte_io

    def setup_routes(self, app: FastAPI):
        """
        Setup of the route. The url has to be in the form:
        /api/data/<country codes comma separated>/<attribute to be plotted>
            ?log=(True or False)[&lastN=X if you want to plot lastNdays][&sinceN=X if you want to plot since the Nth case]
        """

        # setting up routes and implement methods
        @app.get('/api/data/{countries}/{wanted_attrib}')
        def get_data(countries: str, wanted_attrib: Attributes, sinceN: Optional[int] = None, lastN: Optional[int] = None, log: Optional[bool] = None, bar: Optional[bool] = None):
            """
            Returns a png image of the plotted Attribute (see Attributes) for a list of Countries(comma seperated). The URL needs to be in the following form:
            **/api/data/<country codes comma separated>/<attribute to be plotted>
            ?log=(True or False)[&lastN=X if you want to plot lastNdays][&sinceN=X if you want to plot since the Nth case]**
            SinceN and lastN plots the data starting from the given case or just the lastN days. Log is a boolean value that converts the y-scale to the logarithmic unit.
            """
            # read the geoIds and plot the file
            geo_ids = re.split(r",\s*", countries.upper())
            file = self.generate_plot(geo_ids, wanted_attrib,
                                      last_n=lastN if lastN != None else -1, log=log, since_n=sinceN if sinceN != None else -1, bar=bar)

            # return the created stream as png image
            return StreamingResponse(file, media_type="image/png")


# change matplotlib backend to agg (agg is not interactive and it can't be intaractive)
matplotlib.use('agg')
app = FastAPI()
Rest_API().setup_routes(app)
