import sys
import os
# append the src directory to the sys path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from CovidCasesECDC import CovidCasesECDC
from CovidCasesOWID import CovidCasesOWID
from PlotterBuilder import PlotterBuilder
from CovidCasesWHO import CovidCasesWHO
from CovidCases import CovidCases
from typing import Optional
import re
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib
import io
import requests
from datetime import date
from starlette.responses import StreamingResponse
from fastapi import FastAPI, HTTPException
from enum import Enum


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
    DailyVaccineDosesAdministered7DayAverage = 'DailyVaccineDosesAdministered7DayAverage'
    PeopleReceivedFirstDose = 'PeopleReceivedFirstDose'
    PercentPeopleReceivedFirstDose = 'PercentPeopleReceivedFirstDose'
    PeopleReceivedAllDoses = 'PeopleReceivedAllDoses'
    PercentPeopleReceivedAllDoses = 'PercentPeopleReceivedAllDoses'
    VaccineDosesAdministered = 'VaccineDosesAdministered'

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
    DailyVaccineDosesAdministered7DayAverage = '7-day rolling average of daily vaccination doses administered'
    PeopleReceivedFirstDose = 'Number of citizens that received first dose'
    PercentPeopleReceivedFirstDose = 'Percent of citizens that received first dose'
    PeopleReceivedAllDoses = 'Number of citizens that received all doses'
    PercentPeopleReceivedAllDoses = 'Percent of citizens that received all doses'
    VaccineDosesAdministered = 'Vaccine doses administered'

class DataSource(Enum):
    """
    Enumeration of all possible data sources.
    """
    WHO = 'WHO'  # World Health Organization
    OWID = 'OWID'  # Our World in data

class Rest_API:

    def generate_plot(self, geo_ids, wanted_attrib, data_source, log=False, last_n=-1, since_n=-1, bar=False):
        """
        Generates a plot for given GeoIds and returns it in form of a byteIO stream
        Parameters:
            geo_ids: [String] -> countries that should be plotted
            wanted_attrib: String -> the field you want to plot, e.g. Cases
            data_source: DataSource -> Source of the data defined by the enum. Note! If vaccination data is selected and another
                                       source than OWID is selected this will implicitly switch!
            log: bool -> should the plot be logarithmic
            last_n: int -> plot the last n days, if not further specified all available data is plotted
            since_n: int -> plot since the nth case, if not further specified all available data is plotted
        """
        # vaccination data is only available with OWID
        if data_source != DataSource.OWID: 
            if (wanted_attrib == Attributes.VaccineDosesAdministered) or (wanted_attrib == Attributes.DailyVaccineDosesAdministered7DayAverage):
                data_source = DataSource.OWID
            if (wanted_attrib == Attributes.PeopleReceivedAllDoses) or (wanted_attrib == Attributes.PercentPeopleReceivedAllDoses):
                data_source = DataSource.OWID
            if (wanted_attrib == Attributes.PeopleReceivedFirstDose) or (wanted_attrib == Attributes.PercentPeopleReceivedFirstDose):
                data_source = DataSource.OWID
        """ 
        Alternatively in latest Python version
        match (data_source, wanted_attrib):
            case (DataSource.WHO, Attributes.VaccineDosesAdministered | Attributes.PeopleReceivedAllDoses | Attributes.PercentPeopleReceivedAllDoses | Attributes.PeopleReceivedFirstDose | Attributes.PercentPeopleReceivedFirstDose | Attributes.DailyVaccineDosesAdministered7DayAverage):
                data_source = DataSource.OWID
            case (_, _): pass
        """
        # load the cases
        if data_source == DataSource.OWID:
            csv_file = CovidCasesOWID.download_CSV_file()
            self.covid_cases = CovidCasesOWID(csv_file)
        if data_source == DataSource.WHO:
            csv_file = CovidCasesWHO.download_CSV_file()
            self.covid_cases = CovidCasesWHO(csv_file)  
        """ 
        Alternatively in latest Python version
        match data_source:
            case DataSource.OWID:
                csv_file = CovidCasesOWID.download_CSV_file()
                self.covid_cases = CovidCasesOWID(csv_file)
            case DataSource.WHO:
                csv_file = CovidCasesWHO.download_CSV_file()
                self.covid_cases = CovidCasesWHO(csv_file)
        """
        # try to collect the data for given geoIds, if a wrong geoId is passed, the operation will abort with a 400
        # bad request error
        try:
            df = self.covid_cases.get_data_by_geoid_list(
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
            df = self.covid_cases.add_incidence_7day_per_100Kpopulation(df)

        # create pivot table with all needed values, if the x-axis shows a timedelta with days since the nth case the index
        # has to change
        pldf = df.pivot_table(values=wanted_attrib.name, index='Date', columns='GeoName') if since_n == -1 \
            else df.pivot_table(values=wanted_attrib.name, index=df.index, columns='GeoName')

        # use the PlotterBuilder to set up the plot
        builder = (PlotterBuilder(wanted_attrib)
                   # .set_title(re.sub(r"([a-z])([A-Z])", r"\g<1> \g<2>", wanted_attrib.name))
                   .set_title(AttributeTitles[wanted_attrib.value].value)
                   .set_grid())
        if log:
            builder.set_log()
        if since_n != -1:
            # if the plot has a timedelta on the x-axis, the label has to be reset
            builder.set_axis_labels(
                xlabel="Days since case " + str(since_n))
            builder.set_xaxis_index()
        # take care of the y-axis format
        if wanted_attrib == Attributes.R or wanted_attrib == Attributes.R7:
            builder.set_yaxis_formatter(mpl.ticker.StrMethodFormatter('{x:,.2f}'))
        if wanted_attrib == Attributes.PercentPeopleReceivedAllDoses or wanted_attrib == Attributes.PercentPeopleReceivedFirstDose:
            builder.set_yaxis_formatter(mpl.ticker.PercentFormatter())
        if wanted_attrib == Attributes.PercentDeaths:
            builder.set_yaxis_formatter(mpl.ticker.PercentFormatter())
        if wanted_attrib == Attributes.Incidence7DayPer100Kpopulation:
            builder.set_yaxis_formatter(mpl.ticker.StrMethodFormatter('{x:,.2f}'))
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
        def get_data(countries: str, wanted_attrib: Attributes, dataSource: Optional[DataSource] = DataSource.WHO, sinceN: Optional[int] = None, lastN: Optional[int] = None, log: Optional[bool] = None, bar: Optional[bool] = None):
            """
            Returns a png image of the plotted Attribute (see Attributes) for a list of Countries(comma seperated). The URL needs to be in the following form:
            **/api/data/<country codes comma separated>/<attribute to be plotted>
            ?log=(True or False)[&lastN=X if you want to plot lastNdays][&sinceN=X if you want to plot since the Nth case]**
            SinceN and lastN plots the data starting from the given case or just the lastN days. Log is a boolean value that converts the y-scale to the logarithmic unit.
            """
            # read the geoIds and plot the file
            countries = countries.upper()
            countries = countries.replace('UK', 'GB')
            countries = countries.replace('EL', 'GR')
            countries = countries.replace('NA', 'NAM')
            geo_ids = re.split(r",\s*", countries)
            file = self.generate_plot(geo_ids, wanted_attrib,
                                      dataSource, last_n=lastN if lastN != None else -1, log=log, since_n=sinceN if sinceN != None else -1, bar=bar)

            # return the created stream as png image
            return StreamingResponse(file, media_type="image/png")


# change matplotlib backend to agg (agg is not interactive and it can't be interactive)
matplotlib.use('agg')
app = FastAPI()
Rest_API().setup_routes(app)
