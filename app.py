import calendar
import itertools
import json
import logging
import statistics

from dateutil.parser import parse as date_parse
from flask import Flask, jsonify
import flask.logging
import requests


app = Flask(__name__)
log = flask.logging.create_logger(app)

with open("launches.json") as f:
    launches = json.load(f)


@app.route("/api/v1/launches")
def get_launches():
    return jsonify(launches)


@app.route("/api/v1/launches/<launch_slug>")
def get_launch_by_slug(launch_slug):
    return jsonify(get_forecast(launches[launch_slug]))


def get_forecast(launch):
    data = requests.get(
        f"https://api.weather.gov/points/{launch['lat']},{launch['lng']}/forecast/hourly"
    ).json()
    log.debug(data)
    grouped = itertools.groupby(
        data["properties"]["periods"], lambda x: date_parse(x["startTime"]).weekday()
    )

    result = []
    for day, hours in grouped:
        wind = []
        wind_direction = []
        for hour in hours:
            start = date_parse(hour["startTime"])
            if 6 < start.hour < 16:
                wind_speed = float(hour["windSpeed"][:-4])

                wind.append(wind_speed)
                wind_direction.append(DIRECTION_DEGREES_LOOKUP[hour["windDirection"]])
        try:
            avg_speed = statistics.mean(wind)
            avg_direction = statistics.mean(wind_direction)
            wind_speed_score = score(avg_speed, launch["speed"])
            wind_direction_score = score(avg_direction, launch["direction"])

            result.append(
                {
                    calendar.day_name[day]: {
                        "wind_speed": avg_speed,
                        "wind_direction": avg_direction,
                        "wind_speed_score": wind_speed_score,
                        "wind_direction_score": wind_direction_score,
                        "total_score": wind_direction_score * wind_speed_score,
                    }
                }
            )
        except statistics.StatisticsError as _:
            pass

    return result


def score(value, limits):
    if limits["ideal_min"] <= value <= limits["ideal_max"]:
        # Within ideal limits, so we're good.
        return 1
    if not limits["edge_min"] < value < limits["edge_max"]:
        # Outside edge limits, so no go.
        return 0
    if value > limits["ideal_max"]:
        # Between Ideal and Edge on upper side, interpolate.
        slope = 1 / (limits["ideal_max"] - limits["edge_max"])
        return value * slope - limits["edge_max"] * slope
    if value < limits["ideal_min"]:
        # Between Ideal and Edge on lower side, interpolate.
        slope = 1 / (limits["ideal_min"] - limits["edge_min"])
        return (value - limits["edge_min"]) * slope


DIRECTION_DEGREES_LOOKUP = {
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
