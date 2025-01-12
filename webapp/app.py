"""
Webapp run with Flask that communicates with an API (FastAPI/Uvicorn) to display rainfall-related data.
Work-in-progress!
"""

import plotly.graph_objs as go
from flask import Flask, render_template
from plotly.io import from_json

from webapp import api_client
from webapp.views import metrics

flask_app = Flask(__name__)
flask_app.register_blueprint(metrics)


def _aggregate_json_traces_as_figure(traces_json: list[str]) -> go.Figure:
    figure = go.Figure()
    for trace_json in traces_json:
        figure.add_traces(list(from_json(trace_json).select_traces()))

    return figure


@flask_app.route("/")
def index():
    normal_year = 1981
    begin_year = 2014
    end_year = 2023

    summer_rainfall = api_client.get_rainfall_by_year_as_plotly_json(
        time_mode="seasonal",
        begin_year=begin_year,
        end_year=end_year,
        season="summer",
        plot_average=True,
        plot_linear_regression=True,
    )

    ## Averages ##

    monthly_averages = api_client.get_rainfall_averages_as_plotly_json(
        time_mode="monthly",
        begin_year=begin_year,
        end_year=end_year,
    )

    seasonal_averages = api_client.get_rainfall_averages_as_plotly_json(
        time_mode="seasonal",
        begin_year=begin_year,
        end_year=end_year,
    )

    fig_averages = _aggregate_json_traces_as_figure(
        [monthly_averages, seasonal_averages]
    )
    fig_averages.update_layout(
        title=f"Average rainfall (mm) between {begin_year} and {end_year}"
    )
    fig_averages.update_yaxes(title_text="Rainfall (mm)")

    ## LinReg slopes ##

    monthly_linreg_slopes = api_client.get_rainfall_linreg_slopes_as_plotly_json(
        time_mode="monthly",
        begin_year=begin_year,
        end_year=end_year,
    )

    seasonal_linreg_slopes = api_client.get_rainfall_linreg_slopes_as_plotly_json(
        time_mode="seasonal",
        begin_year=begin_year,
        end_year=end_year,
    )

    fig_linreg_slopes = _aggregate_json_traces_as_figure(
        [monthly_linreg_slopes, seasonal_linreg_slopes]
    )
    fig_linreg_slopes.update_layout(
        title=f"Average linear regression slope (mm/year) between {begin_year} and {end_year}"
    )
    fig_linreg_slopes.update_yaxes(title_text="Linear regression slope (mm/year)")

    ## Relative distances to normal ##

    monthly_relative_distances_to_normal = (
        api_client.get_rainfall_relative_distances_to_normal_as_plotly_json(
            time_mode="monthly",
            normal_year=normal_year,
            begin_year=begin_year,
            end_year=end_year,
        )
    )

    seasonal_relative_distances_to_normal = (
        api_client.get_rainfall_relative_distances_to_normal_as_plotly_json(
            time_mode="seasonal",
            normal_year=normal_year,
            begin_year=begin_year,
            end_year=end_year,
        )
    )

    fig_relative_distances_to_normal = _aggregate_json_traces_as_figure(
        [monthly_relative_distances_to_normal, seasonal_relative_distances_to_normal]
    )
    fig_relative_distances_to_normal.update_layout(
        title=f"Relative distance to {normal_year}-{normal_year + 29} normal (%) between {begin_year} and {end_year}"
    )
    fig_relative_distances_to_normal.update_yaxes(
        title_text="Relative distance to normal (%)"
    )

    return render_template(
        "index.html",
        title="Barcelona Rainfall",
        plotlySummerRainfallJSON=summer_rainfall,
        plotlyAveragesJSON=fig_averages.to_json(),
        plotlyLinRegJSON=fig_linreg_slopes.to_json(),
        plotlyRelativeDistance2NormalJSON=fig_relative_distances_to_normal.to_json(),
    )
