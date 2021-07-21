import math
import pandas as pd
import numpy as np
from math import log10
from PIL import Image, ImageDraw
from dataclasses import dataclass

@dataclass
class heatmapResult:
    """somehow a struct holding the information about the map that should be generated
    """
    # the minmum of the given value
    minimum: float
    # the maximum of the given values
    maximum: float
    # an array of colors, one per given value
    colors: [] = None

class Colormap:
    """funtions to map values in the range minValue to maxValue to an rgb color.

    Raises:
        ValueError: If a tuple has not 3 elements for RGB, or if a list of such tuples is empty

    Returns:
        Colormap: An object to access the class
    """
    # constructor
    def __init__(self, minVal, maxVal):
        """constructor
        """
        
    @staticmethod
    def convert_float_to_byte_colors(floatColors):
        """conversion of float color values (0.0 - 1.0) to byte values (0x00 - 0xFF)

        Args:
            floatColors (list): A list of float tuples in the range 0.0 - 1.0 representing RGB values

        Raises:
            ValueError: If a tuple has not 3 elements for RGB, or if a list of such tuples is empty
  
        Returns:
            list: A list of byte tuples in the range 0x00 - 0xFF representing RGB values
        """
        # check parameters
        if len(floatColors) == 0:
            raise ValueError('Expect an array of R, G, B tuples. Instead len(colorValues) is 0.')
        if len(floatColors[0]) != 3:
            raise ValueError('Tuple length of colorValues should be 3. Instead it is: ' + str(len(floatColors) + '.'))
        result = []
        byteColors = []
        for floatColor in floatColors:
            r = round(floatColor[0] * 255)
            g = round(floatColor[1] * 255)
            b = round(floatColor[2] * 255)
            byteColors.append((r, g, b))
        return byteColors

    @staticmethod
    def create_heatmap_bar(barSize, blendValue=None, blendFactor=0.0):
        """creates a png showing the heatmap colors as a bar

        Args:
            barSize (tuple): A tuple holding 2 ints for the width and height
            blendValue (tuple, optional): A tuple holding 3 float values ranging from 0.0 to 1.0 representing a RGB color. Defaults to None.
            blendFactor (float, optional): A blend factor ranging from 0.0 to 1.0. The original color will be weight with (1-blendFactor), the blendValue with blendFactor. Defaults to 0.0.

        Returns:
            PIL.Image: The image showing the heatmap
        """
        # create a new image
        bar = Image.new(mode='RGB', size=barSize)
        # create a df holding the x positions
        values = []
        # the x-positions
        for x in range(barSize[0]):
            values.append(x)
        # the df
        df = pd.DataFrame(np.asarray(values))
        # ...and a name for the column
        df.columns = ['Values']
        
        # get the RGB values as floats ranging from 0.0 to 1.0
        res = Colormap.heatmap_from_dataframe(df, 'Values')
        # blend colors if requested
        if blendFactor != 0.0:
            colorValues = Colormap.blend_color_values(res.colors, blendValue=blendValue, blendFactor=blendFactor)
        # convert them to bytes ranging from 0 to 0xFF
        colorValues = Colormap.convert_float_to_byte_colors(colorValues)
        
        # get a drawing context
        draw = ImageDraw.Draw(bar)
        for x in range(barSize[0]):
            p0 = (x, 0)
            p1 = (x, barSize[1] - 1)
            draw.line((p0, p1), fill=colorValues[x])
        return bar

    @staticmethod
    def color_values_to_hex_triplets(colorValues):
        """converts converts float color values to a hex string

        Args:
            colorValues (tuple): A list of float tuples in the range 0.0 - 1.0 representing RGB values

        Raises:
            ValueError: If a tuple has not 3 elements for RGB, or if a list of such tuples is empty
 
        Returns:
            list: A list of strings holding color information in the form of #RRGGBB
        """
        # check parameters
        if len(colorValues) == 0:
            raise ValueError('Expect an array of R, G, B tuples. Instead len(colorValues) is 0.')
        # check the men of the given tuple
        if len(colorValues[0]) != 3:
            raise ValueError('Tuple lenght should be 3. Instead it is: ' + str(len(colorValues[0]) + '.'))
        result = []
        for colorValue in colorValues:
            # maps it to a RGB string holding hex values
            hexTriplet = '#%02x%02x%02x' % (round(colorValue[0] * 255), round(colorValue[1] * 255), round(colorValue[2] * 255))
            result.append(hexTriplet)
        return result

    @staticmethod
    def blend_color_values(colorValues, blendValue, blendFactor):
        """alpha-blending of an array of float color values and a given blend float color value

        Args:
            colorValues (list): A list of float tuples in the range 0.0 - 1.0 representing RGB values
            blendValue (tuple): A tuple holding 3 float values ranging from 0.0 to 1.0 representing a RGB color.
            blendFactor (float): A blend factor ranging from 0.0 to 1.0. The original color will be weight with (1-blendFactor), the blendValue with blendFactor.

        Raises:
            ValueError: If a tuple has not 3 elements for RGB, or if a list of such tuples is empty

        Returns:
            list: A list of float tuples in the range 0.0 - 1.0 representing RGB values
        """
        # check parameters
        if len(colorValues) == 0:
            raise ValueError('Expect an array of R, G, B tuples. Instead len(colorValues) is 0.')
        if len(blendValue) != 3:
            raise ValueError('Tuple length of blendValue should be 3. Instead it is: ' + str(len(blendValue) + '.'))
        if len(colorValues[0]) != 3:
            raise ValueError('Tuple length of colorValues should be 3. Instead it is: ' + str(len(colorValues) + '.'))
        result = []
        for colorValue in colorValues:
            r = colorValue[0] * (1 - blendFactor) + blendValue[0] * blendFactor
            g = colorValue[1] * (1 - blendFactor) + blendValue[1] * blendFactor
            b = colorValue[2] * (1 - blendFactor) + blendValue[2] * blendFactor
            result.append((r, g, b))
        return result 

    @staticmethod
    def heatmap_from_dataframe(df, column, useLog = False, gain = 1.0, offset = 0.0):
        """[Returns an array of color tuples for each value in the given column of a dataframe as a heatmap.
            values close to minValue will become blue and values close to maxValue will become red.
            refer to: 
            http://stackoverflow.com/questions/7706339/grayscale-to-red-green-blue-matlab-jet-color-scale 

        Args:
            df (DataFrame): A dataFrame generated by the Covid-19 analysis
            column (str): The name of the column to be processed
            useLog (bool, optional): If True the it will use the logarithm of the values. Defaults to False.
            gain (float, optional): A gain to be applied to the values. Defaults to 1.0.
            offset (float, optional): An offset to be applied to the values. Defaults to 0.0.

        Returns:
            list: A list of float tuples in the range 0.0 - 1.0 representing RGB values
        """
        # get min and max
        minVal = df[column].min() * gain + offset
        maxVal = df[column].max()
        result = heatmapResult(minVal, maxVal)
        if (useLog):
            # get the log10 of min and max, take care of small values
            if (minVal < 0.00001):
                minVal = -5.0
            else:
                minVal = math.log10(minVal)
            if (maxVal < 0.00001):
                maxVal = -5.0
            else:
                maxVal = math.log10(maxVal)
        # init result
        resultColors = []
        for index, value in df[column].iteritems():
            # apply gain and offset
            val = value * gain + offset
            if (useLog):
                # use the log of the value
                if (val < 0.00001):
                    val = 0.00001
                # get the color value
                val = Colormap.heatmap_from_value(log10(val), minVal, maxVal)
            else:
                # get the color value
                val = Colormap.heatmap_from_value(val, minVal, maxVal)
            # append it to the result
            resultColors.append(val)
        result.colors = resultColors
        return result

    # returns a heatmap color value for a given value
    @staticmethod
    def heatmap_from_value(val, minVal, maxVal):
        """returns a heatmap color value for a given value

        Args:
            val (float): The input value for which a heatmap color should be generated
            minVal (float): The minimum value representing blue in the heatmap
            maxVal (float): The maximum value representing red in the heatmap

        Returns:
            list: A list of float tuples in the range 0.0 - 1.0 representing RGB values
        """
        # init the color
        r = 1.0
        g = 1.0
        b = 1.0
        # check if the val is NaN and return white for this case
        if math.isnan(val):
            return (r, g, b)
        # check the limits
        if (val < minVal):
            val = minVal
        if (val > maxVal):
            val = maxVal
        # the range
        dv = maxVal - minVal
        if dv == 0:
            # nothing to map when there is no range -> red
            r = 1
            g = 0
            b = 0
        elif (val < (minVal + 0.25 * dv)):
            # blue-green part
            r = 0
            g = 4 * (val - minVal) / dv
        elif (val < (minVal + 0.5 * dv)):
            # green-blue part
            r = 0
            b = 1 + 4 * (minVal + 0.25 * dv - val) / dv
        elif (val < (minVal + 0.75 * dv)):
            # green-red part
            r = 4 * (val - minVal - 0.5 * dv) / dv
            b = 0
        else:
            # red-green part
            g = 1 + 4 * (minVal + 0.75 * dv - val) / dv
            b = 0
        return (r, g, b)
