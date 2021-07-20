import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import ScalarFormatter
from matplotlib.ticker import LogFormatter
from matplotlib.ticker import LogFormatterSciNotation
class PlotterBuilder:
    """
    A class that let's you easily build the wanted plotting configuration. If not further specified you get some
    default values like:
        - A figsize of 12, 8
        - No name
        - No grid
        - A linear y-axis-scale
        - A xaxis DateFormatter with format Y-m-d
    When plotting a DataFrame this class is always grouping by columns.
    """

    def __init__(self, yfield):
        """
        Creates an instance with mentioned default values.
        Parameter:
            yfield: The field of the DataFrame you want to plot.
        """
        self.__figsize = (12, 8)
        self.__title = ""
        self.__grid = False
        self.__yscale = 'linear'
        self.__xaxis_formatter = mdates.DateFormatter('%d/%m/%Y')
        self.__yaxis_formatter = mpl.ticker.StrMethodFormatter('{x:,.0f}')        
        self.__yfield = yfield
        self.__xlabel = ""
        self.__ylabel = ""
       
    def set_figsize(self, sizes):
        """
        Setter for the figure size.
        """
        self.__figsize = sizes
        return self

    def set_title(self, title):
        """
        Setter for the title.
        """
        self.__title = title
        return self

    def set_grid(self, grided=True):
        """
        Sets the grid value to True.
        """
        if grided == True:
            self.__grid = True
        else:
            self.__grid = False
        return self

    def set_log(self, logged=True):
        """
        Formats the yscale to logarithmic.
        """
        if logged == True:
            self.__yscale = 'log'
        else:
            self.__yscale = 'linear'
        return self

    def set_xaxis_index(self, indexed=True):
        """
        Tells the x-axis that you don't want to plot a date.
        """
        if indexed == True:
            self.__xaxis_formatter = None
        else:
            self.__xaxis_formatter = mdates.DateFormatter('%d/%m/%Y')
        return self

    def set_yaxis_formatter(self, formatter):
        self.__yaxis_formatter = formatter
        return self

    def set_axis_labels(self, xlabel="", ylabel=""):
        """
        Sets the axis labels.
        """
        self.__xlabel = xlabel
        self.__ylabel = ylabel
        return self

    def build(self):
        """
        Builds the configured plotting object.
        Returns:
             fig: figure object
             ax: axis object with the wanted configurations.
        """
        fig, ax = plt.subplots(1, 1, figsize=self.__figsize)
        ax.set_title(self.__title)
        ax.set_yscale(self.__yscale)
        if self.__yscale == 'log':
            formatter = LogFormatterSciNotation(labelOnlyBase=False, minor_thresholds=(3, 0.5))
            ax.yaxis.set_minor_formatter(formatter)
            ax.yaxis.set_major_formatter(formatter)
        else:
            ax.ticklabel_format(useOffset=False, style='plain')
            if self.__yaxis_formatter:
                ax.yaxis.set_major_formatter(self.__yaxis_formatter)
            if self.__xaxis_formatter:
                ax.xaxis.set_major_formatter(self.__xaxis_formatter)
        ax.set(xlabel=self.__xlabel)
        ax.set(ylabel=self.__ylabel)
        return [fig, ax]

    def plot_dataFrame(self, df, ylim_min=None, ylim_max=None, **options):
        """
        Plots the DataFrame. If you want to plot an index on the x-axis you have to set it within the DataFrame object.
        If not the column date is used.
        """
        if self.__xaxis_formatter is None:
            # plot an index, not a date
            pldf = df.pivot_table(values=self.__yfield, index=df.index, columns='GeoName')
        else:
            # plot it with a date formatted x axis
            pldf = df.pivot_table(values=self.__yfield, index='Date', columns='GeoName')
        fig, ax = self.build()
        pldf.plot(ax=ax, **options)
        ax.set_ylim(ymin=ylim_min, ymax=ylim_max)
        ax.grid(self.__grid)
