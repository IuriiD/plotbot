import pygal
import cairosvg

input = [{"fibo": [1, 2, 4, 8]},{"next": [2, 3, 4, 5]}]

def pygal_bar_chart(data, png_file_name):
    bar_chart = pygal.Bar()
    for ds in data:
      for key, value in ds.items():
        bar_chart.add(key, value)
    bar_chart.render_to_png(png_file_name)
    return True

pygal_bar_chart(input,'test.png')