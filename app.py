import calendar
import itertools
import json
import logging
import statistics

from dateutil.parser import parse as date_parse
import flask
from flask import Flask, jsonify, request
import flask.logging
import requests


app = Flask(__name__)
log = flask.logging.create_logger(app)

with open("launches.json") as f:
    launches = json.load(f)


@app.route("/api/v1/launches", methods=["GET"])
def get_launches():
    return jsonify(launches)


@app.route("/api/v1/launches/<launch_slug>", methods=["GET"])
def get_launch_by_slug(launch_slug):
    launch = launches[launch_slug]
    data = requests.get(
        f"https://api.weather.gov/points/{launch['lat']},{launch['lng']}/forecast/hourly"
    ).json()
    log.debug(data)
    interval = request.args.get("interval")

    if interval == None or interval == "daily":
        result = []
        grouped = itertools.groupby(
            data["properties"]["periods"],
            lambda x: date_parse(x["startTime"]).date().isoformat(),
        )
        for day, hours in grouped:
            wind_speed = []
            wind_direction = []
            for hour in hours:
                start = date_parse(hour["startTime"])
                if 6 < start.hour < 16:
                    wind = make_wind_dict(hour)
                    wind_speed.append(wind["speed"])
                    wind_direction.append(wind["direction"])
            try:
                speed_average = statistics.mean(wind_speed)
                direction_average = statistics.mean(wind_direction)
            except statistics.StatisticsError as _:
                pass
            finally:
                result.append(
                    {day: make_time_unit_dict(speed_average, direction_average, launch)}
                )

        return jsonify(result)
    elif interval == "hourly":
        result = []
        for hour in data["properties"]["periods"]:
            wind = make_wind_dict(hour)
            result.append(
                {
                    date_parse(hour["startTime"]).isoformat(): make_time_unit_dict(
                        wind["speed"], wind["direction"], launch
                    )
                }
            )
        return jsonify(result)
    else:
        return "Invalid interval", 400


def make_wind_dict(period):
    return {
        "speed": float(period["windSpeed"][:-4]),
        "direction": DIRECTION_DEGREES_LOOKUP[period["windDirection"]],
    }


def make_time_unit_dict(speed, direction, launch):
    speed_score = score(speed, launch["speed"])
    direction_score = score(direction, launch["direction"])
    return {
        "wind_speed": speed,
        "wind_direction": direction,
        "wind_speed_score": speed_score,
        "wind_direction_score": direction_score,
        "total_score": speed_score * direction_score,
    }


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
