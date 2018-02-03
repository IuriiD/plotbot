from flask import Flask, render_template, url_for, request, redirect, flash
import pygal
import cairosvg

chart_name = 'Fibonacci'
data = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
png_file_name = 'bar_chart1.png'

def pygal_bar_chart(chart_name, data, png_file_name):
    bar_chart = pygal.Bar()             # Then create a bar graph object
    bar_chart.add(chart_name, data)     # Add some values
    bar_chart.render_to_png(png_file_name)
    return True

pygal_bar_chart(chart_name, data, png_file_name)

# https://plotbot.glitch.me/webhook