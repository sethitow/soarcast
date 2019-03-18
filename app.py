import calendar
import datetime
import itertools
import json
import logging
import pytz
import statistics

from dateutil.parser import parse as date_parse
from flask import Flask, jsonify
import requests


app = Flask(__name__)

with open("launches.json") as f:
    launches = json.load(f)


@app.route("/api/launches")
def get_launches():
    return jsonify(launches)


@app.route("/api/launch/<launch_slug>")
def get_launch_by_slug(launch_slug):
    return jsonify(get_forecast(launches[launch_slug]))


def get_forecast(launch):
    data = requests.get(
        f"https://api.weather.gov/points/{launch['lat']},{launch['lng']}/forecast/hourly"
    ).json()
    app.logger.debug(data)
    grouped = itertools.groupby(
        data["properties"]["periods"], lambda x: date_parse(x["startTime"]).weekday()
    )

    result = []
    for day, hours in grouped:
        wind = []
        wind_dir = []
        for hour in hours:
            start = date_parse(hour["startTime"])
            if 6 < start.hour < 16:
                wind_speed = float(hour["windSpeed"][:-4])

                wind.append(wind_speed)
                wind_dir.append(wind_dir_lookup[hour["windDirection"]])
        try:
            result.append(
                {
                    calendar.day_name[day]: {
                        "wind_speed": statistics.mean(wind),
                        "wind_dir": statistics.mean(wind_dir),
                    }
                }
            )
        except statistics.StatisticsError as _:
            pass

    return result


wind_dir_lookup = {
    "N": 0.0,
    "NNE": 22.5,
    "NE": 45.0,
    "ENE": 67.5,
    "E": 90.0,
    "ESE": 112.5,
    "SE": 135.0,
    "SSE": 157.5,
    "S": 180.0,
    "SSW": 202.5,
    "SW": 225.0,
    "WSW": 247.5,
    "W": 270.0,
    "WNW": 292.5,
    "NW": 315.0,
    "NNW": 337.5,
}

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True)
