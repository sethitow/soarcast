import calendar
import datetime
import itertools
import pytz
import statistics

from dateutil.parser import parse as date_parse
from flask import Flask, jsonify
import requests


app = Flask(__name__)

@app.route("/api")
def hello():
    return jsonify(get_forecast(sites[0]))

def get_forecast(site):
    data = requests.get(
        f"https://api.weather.gov/points/{site['lat']},{site['lng']}/forecast/hourly").json()

    grouped = itertools.groupby(data['properties']['periods'], lambda x: date_parse(x['startTime']).weekday())

    result = []
    for day, hours in grouped:
        wind = []
        for hour in hours:
            wind_speed = float(hour['windSpeed'][:-4])
            wind.append(wind_speed)
        try:
            result.append({calendar.day_name[day]: statistics.mean(wind)})
        except statistics.StatisticsError as _:
            pass

    return result

sites = [{'name': "Ed Levin",
          'lat': 37.475,
          'lng': -121.861,
          'ideal_min': 0,
          'ideal_max': 8,
          'dir_ideal': ['SSE', 'S', 'SSW', 'SW', 'WSW', 'W']
          }]

if __name__ == '__main__':
    app.run()