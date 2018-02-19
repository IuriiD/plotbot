import os
import pygal
from pygal.style import DefaultStyle
import cairosvg

# Scatter chart
def pygal_scatter(data, chartname, file_name):
    xy_chart = pygal.XY(stroke=False)
    xy_chart.title = chartname
    for ds in data:
        for key, value in ds.items():
            xy_chart.add(key, value)
    xy_chart.render_to_file(file_name + '.svg')
    xy_chart.render_to_png(file_name + '.png')
    return True

data2plot = [{'TheBigOnes': [(1.0, 2.0), (2.0, 4.0), (3.0, 5.0)]}]

ourfilename = 'static/test'
chartname = 'test'

pygal_scatter(data2plot, chartname, ourfilename)