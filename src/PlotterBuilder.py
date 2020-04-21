import matplotlib.pyplot as plt
import matplotlib.dates as mdates


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
        self.__xaxis_formatter = mdates.DateFormatter('%Y-%m-%d')
        self.__yfield = yfield

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

    def set_grid(self):
        """
        Sets the grid value to True.
        """
        self.__grid = True
        return self

    def set_log(self):
        """
        Formats the yscale to logarithmic.
        """
        self.__yscale = 'log'
        return self

    def set_xaxis_index(self):
        """
        Tells the x-axis that you don't want to plot a date.
        """
        self.__xaxis_formatter = None
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
        if self.__xaxis_formatter:
            ax.xaxis.set_major_formatter(self.__xaxis_formatter)

        return [fig, ax]

    def plot_dataFrame(self, df, **options):
        """
        Plots the DataFrame. If you want to plot an index on the x-axis you have to set it within the DataFrame object.
        If not the column date is used.
        """
        if self.__xaxis_formatter is None:
            # plot an index, not a date
            pldf = df.pivot_table(values=self.__yfield, index=df.index, columns='Country')
        else:
            # plot it with a date formatted x axis
            pldf = df.pivot_table(values=self.__yfield, index='Date', columns='Country')
        fig, ax = self.build()
        pldf.plot(ax=ax, **options)
        ax.grid(self.__grid)

