import pandas as pd
import numpy as np
import pygal
import os
from pygal.maps.world import World
from pygal.style import Style
from PIL import Image, ImageDraw, ImageFont
from datetime import timedelta, date
from IPython.display import SVG, display
from dataclasses import dataclass
from Colormap import Colormap

def date_range(start_date, end_date):
    """an iterator for a range of dates given by start_date and end_date

    Args:
        start_date (date): The start date
        end_date (date): The end date, yields for all dates < end_date

    Yields:
        date: the actual date
    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

@dataclass
class mapInfo:
    """somehow a struct holding the information about the map that should be generated
    """
    # the attribute name within the dataframe
    attribute: str
    # the map title
    title: str
    # the output directory for the map in a SVG format
    output_directory: str = ''

@dataclass
class mapResult:
    """somehow a struct holding the information of the results of the map generation
    """
    # the SVG
    svg: SVG
    # the minimum (blue) value of a country in the map
    minimum: float
    # the maximum (red) value of a country in the map
    maximum: float

class CovidMap:
    """a class to calculuate pygal maps from a dataframe column

    Returns:
        CovidMap: the object to access the class
    """
    # constructor
    def __init__(self, df):
        """constructor

        Args:
            df (DataFrame): The data frame to be processed
        """
        # keep the data frame
        self.__df = df

    @staticmethod
    def add_heatmap_bar_to_all_png(info):
        """adds a heatmap bar and some text to all png in a given directory

        Args:
            info (mapInfo): Information about the graph such as the title of the map
        """
        # create the bar
        bar = Colormap.create_heatmap_bar((1024, 32), (0.1, 0.1, 0.1), 0.1)
        # the output directory
        directory = info.output_directory + '/' + info.attribute + '/'
        # fonts for the text output
        fntAxis = ImageFont.truetype("Calibri.ttf", 18)
        fntInfo = ImageFont.truetype("Calibri.ttf", 12)
        for filename in sorted(os.listdir(directory)):
            if filename.endswith(".png"):
                # open the file
                img = Image.open(directory + filename)
                # place the bar into the image
                img.paste(bar, (690, 850))
                # create a drawer
                draw = ImageDraw.Draw(img)
                # label on the left of the bar
                draw.text((690, 850 + 32 + 2), 
                        'Daily minimum', 
                        font=fntAxis, 
                        fill=(255,255,255,0))
                # label on the right of the bar
                draw.text((690 + 1024 - 110, 850 + 32 + 2), 
                        'Daily maximum', 
                        font=fntAxis, 
                        fill=(255,255,255,0))
                # info label
                draw.text((690 + 240, 850 + 32 + 6), 
                        'Source: ECDC data, More information: http://mb.cmbt.de, GitHub: https://github.com/1c3t3a/Covid-19-analysis', 
                        font=fntInfo, 
                        fill=(255,255,255,0))
                # img.show()
                # save the image
                img.save(directory + filename)
                print(filename)
        return

    def create_map_for_date(self, info, the_day):
        """creates a svg for a date showing a worldmap of the data

        Args:
            info (mapInfo): Information about the graph such as the title of the graph
            the_day (date): The date for whichn the graph sould be created

        Returns:
            mapResult: A struct to hold information about the generated map
        """
        # the output directory
        outputDirectory = info.output_directory + '/' + info.attribute + '/'
        print(info.attribute + ': ' + str(the_day))
        # converted into a pandas date
        pdDate = pd.to_datetime(the_day)
        # get the data for this day
        dfDate = self.__df.loc[self.__df['Date'] == pdDate]
        # now get those countries who had at least 1 case
        dfDateNoneZero = dfDate.loc[dfDate['Cases'] != 0]
        
        # get the heatmap colors
        hmResult = Colormap.heatmap_from_dataframe(dfDateNoneZero, info.attribute, useLog=True, gain=1.0, offset = 0)
        # blend them
        heatmapColors = Colormap.blend_color_values(hmResult.colors, (0.1, 0.1, 0.1), 0.1)
        # create hex triplets 
        heatmapColors = Colormap.color_values_to_hex_triplets(heatmapColors)
        # select a custom style for the map
        custom_style = Style(colors=heatmapColors, 
                            font_family='Calibri',
                            title_font_size=28, 
                            #background='transparent',
                            #plot_background='transparent',
                            #foreground='#53E89B',
                            #foreground_strong='#53A0E8',
                            #foreground_subtle='#630C0D',
                            #opacity='.6',
                            #opacity_hover='0.9')#,
                            #transition='400ms ease-in'
                            )
        # create a map using the style
        myMap = pygal.maps.world.World(style=custom_style, show_legend=False, width=1920, height=1080, print_values=True)
        # set the title
        myMap.title = the_day.strftime("%Y-%m-%d") + ': ' + info.title

        # the list of GeoIDs in the dataframe
        geoIDs = dfDateNoneZero['GeoID'].unique()
        # show the contries
        for geoID in geoIDs:
            # mapping of ISO and WHO country names
            if geoID == 'UK':
                myMap.add(geoID, 'gb')
            elif geoID == 'EL':
                myMap.add(geoID, 'gr')
            else:   
                # add it to the map      
                dfc = dfDateNoneZero.loc[dfDateNoneZero['GeoID'] == geoID]
                # add the value as a tooltip
                val = dfc[info.attribute].values[0]
                myMap.add(geoID, {geoID.lower():"{:.4f}".format(val)})
        # render the map
        filename = outputDirectory + '/' + the_day.strftime("%Y-%m-%d") + '-' + info.attribute + '.svg'
        myMap.render_to_file(filename)
        svg = myMap.render()
        result = mapResult(svg, hmResult.minimum, hmResult.maximum)
        return result

    def create_map_for_date_range(self, info, start_date, end_date):
        """creates the svg's for a date range showing a worldmap of the data

        Args:
            info (mapInfo): Information about the graph such as the title of the graph
            start_date (date): The start date
            end_date ([type]): The end date
        """
        # init the result
        hmResults = []
        # loop through all dates  
        for single_date in date_range(start_date, end_date):
            # create the map for this date
            res = self.create_map_for_date(info, single_date)
        return
