#! /usr/bin/env python3

from flask import Flask, make_response, jsonify, abort, send_file, request
import re
import pandas as pd
import matplotlib.pyplot as plt
import io
from src.PlotterBuilder import PlotterBuilder
from src.CovidCases import CovidCases


def setup_errorhandlers(app):
    """
    Setup of error handlers for common HTTP errors.
    """

    @app.errorhandler(404)
    def not_found(_):
        return make_response(jsonify({'error': 'Not found'}), 404)

    @app.errorhandler(400)
    def bad_request(_):
        return make_response(jsonify({'error': 'bad request'}), 400)


def setup_routes(app):
    """
    Setup of the route. The url has to be in the form:
    /api/data/<country codes comma separated>/<attribute to be plotted>
        ?log=(True or False)[&lastN=X if you want to plot lastNdays][&sinceN=X if you want to plot since the Nth case]
    """

    # setting up routes and implement methods
    @app.route('/api/data/<countries>/<wanted_attrib>', methods=['GET'])
    def get_data(countries, wanted_attrib):
        # get path parameters for lastN days and sinceN days if given
        last_n = int(request.args['lastN']) if request.args.__contains__('lastN') else -1
        since_n = int(request.args['sinceN']) if request.args.__contains__('sinceN') else -1

        # get log parameter which is needed
        try:
            log = request.args['log'] == 'True'
        except AttributeError:
            log = False

        # read the geoIds and plot the file
        geo_ids = re.split(r",\s*", countries)
        file = generate_plot(geo_ids, wanted_attrib, last_n=last_n, log=log, since_n=since_n)

        # return the created stream as png image
        return send_file(file, mimetype='image/PNG')


def generate_plot(geo_ids, wanted_attrib, log=False, last_n=-1, since_n=-1):
    """
    Generates a plot for given GeoIds and returns it in form of a byteIO stream
    Parameters:
        geo_ids: [String] -> countries that should be plotted
        wanted_attrib: String -> the field you want to plot, e.g. CumultativeCases
        log: bool -> should the plot be logarithmic
        last_n: int -> plot the last n days, if not further specified all available data is plotted
        since_n: int -> plot since the nth case, if not further specified all available data is plotted
    """

    # load the cases
    covid_cases = CovidCases('../../data/db.json')

    # try to collect the data for given geoIds, if a wrong geoId is passed, the operation will abort with a 400
    # bad request error
    dfdata = []
    try:
        for geoId in geo_ids:
            dfdata.append(pd.DataFrame(
                covid_cases.get_country_data_by_geoID(geoId, lastNdays=last_n, sinceNcases=since_n)))
    except IndexError:
        return abort(400)
    # concat to one DataFrame and set date
    df = pd.concat(dfdata)
    df[['Date']] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

    # create pivot table with all needed values, if the x-axis shows a timedelta with days since the nth case the index
    # has to change
    pldf = df.pivot_table(values=wanted_attrib, index='Date', columns='Country') if since_n == -1 \
        else df.pivot_table(values=wanted_attrib, index=df.index, columns='Country')

    # use the PlotterBuilder to set up the plot
    builder = (PlotterBuilder(wanted_attrib)
               .set_title(re.sub("([a-z])([A-Z])", "\g<1> \g<2>", wanted_attrib))
               .set_grid())
    if log:
        builder.set_log()
    if since_n != -1:
        # if the plot has a timedelta on the x-axis, the label has to be reset
        builder.set_axis_labels(xlabel="Days since case " + str(since_n))
        builder.set_xaxis_index()
    # generate plot
    fig, ax = builder.build()
    pldf.plot(ax=ax)
    ax.grid()
    # write image to io stream
    byte_io = io.BytesIO()
    plt.savefig(byte_io, dpi=fig.dpi)
    byte_io.seek(0)

    return byte_io


if __name__ == '__main__':
    # setup the Flask app
    app = Flask(__name__)
    setup_errorhandlers(app)
    setup_routes(app)
    app.run(debug=True)
