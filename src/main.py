import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model, metrics
from scipy import signal

dataset_url = str.format("https://opendata-ajuntament.barcelona.cat/data/dataset/{0}/resource/{1}/download/{2}",
                         "5334c15e-0d70-410b-85f3-d97740ffc1ed",
                         "6f1fb778-0767-478b-b332-c64a833d26d2",
                         "precipitacionsbarcelonadesde1786.csv")

starting_year = 1970


def retrieve_yearly_rainfall() -> pd.DataFrame:
    monthly_rainfall = pd.read_csv(dataset_url)

    years = monthly_rainfall.iloc[:, :1]
    rainfall = monthly_rainfall.iloc[:, 1:].sum(axis='columns')

    yearly_rainfall = pd.concat((years, rainfall), axis='columns').set_axis(['Year', 'Rainfall'], axis='columns')
    yearly_rainfall = yearly_rainfall[yearly_rainfall['Year'] >= starting_year]

    return yearly_rainfall \
        .reset_index() \
        .drop(columns='index')


def get_average_yearly_rainfall(yearly_rainfall: pd.DataFrame, begin_year: int, end_year: int) -> float:
    yearly_rainfall = yearly_rainfall[yearly_rainfall['Year'] <= end_year]
    yearly_rainfall = yearly_rainfall[begin_year <= yearly_rainfall['Year']]
    yearly_rainfall = yearly_rainfall.sum(axis='rows')

    return round(yearly_rainfall.loc['Rainfall'] / (end_year - begin_year), 2)


def apply_linear_regression_to_yearly_rainfall(yearly_rainfall: pd.DataFrame) -> pd.DataFrame:
    reg = linear_model.LinearRegression()
    reg.fit(yearly_rainfall["Year"].values.reshape(-1, 1), yearly_rainfall["Rainfall"].values)
    yearly_rainfall["Linear Regression"] = reg.predict(yearly_rainfall["Year"].values.reshape(-1, 1))

    print("Coefficient of determination:", metrics.r2_score(yearly_rainfall["Rainfall"].values,
                                                            yearly_rainfall["Linear Regression"].values))

    return yearly_rainfall


def apply_savgol_filter_to_yearly_rainfall(yearly_rainfall: pd.DataFrame) -> pd.DataFrame:
    yearly_rainfall["Savgol Filter"] = signal.savgol_filter(yearly_rainfall["Rainfall"].values,
                                                            window_length=len(yearly_rainfall["Rainfall"].values),
                                                            polyorder=5)

    return yearly_rainfall


def add_deviation_from_normal(yearly_rainfall: pd.DataFrame, normal: float):
    yearly_rainfall['Percentage of normal'] = round(yearly_rainfall['Rainfall'] / normal * 100.0, 2)


def count_years_above_normal(yearly_rainfall: pd.DataFrame) -> int:
    return yearly_rainfall[yearly_rainfall["Percentage of normal"] > 100.0].count()["Year"]


def count_years_below_normal(yearly_rainfall: pd.DataFrame) -> int:
    return yearly_rainfall[yearly_rainfall["Percentage of normal"] < 100.0].count()["Year"]


def group_yearly_rainfall_by_decade(yearly_rainfall: pd.DataFrame) -> pd.DataFrame:
    decades_rainfall = []
    for year in range(starting_year, yearly_rainfall['Year'].iloc[-1] + 1, 10):
        decade = yearly_rainfall.iloc[year - starting_year: year - starting_year + 10]
        decade.loc[decade["Year"] // 10 == year // 10, "Year"] = year // 10
        decades_rainfall.append(decade.groupby('Year').sum().drop('index', axis='columns'))

    df = decades_rainfall[0]
    for decade_rainfall in decades_rainfall[1:]:
        df = pd.concat((df, decade_rainfall), axis='rows')

    df.index.names = ['Decade']

    return df


def plot_yearly_rainfall(yearly_rainfall: pd.DataFrame):
    yearly_rainfall.plot(x="Year",
                         y="Rainfall",
                         ylabel="Rainfall (mm)")


def plot_yearly_rainfall_savgol_filter(yearly_rainfall: pd.DataFrame):
    yearly_rainfall.plot(x="Year",
                         y="Savgol Filter",
                         ylabel="Rainfall (mm)")


def plot_yearly_rainfall_deviation_from_normal(yearly_rainfall: pd.DataFrame):
    yearly_rainfall.plot(x="Year",
                         y="Percentage of normal",
                         label="Percentage of normal (%)",
                         kind="scatter",
                         title="Barcelona rainfall deviation from normal")


def plot_yearly_rainfall_linear_regression(yearly_rainfall: pd.DataFrame):
    yearly_rainfall.plot(x="Year",
                         y="Linear Regression",
                         ylabel="Rainfall (mm)",
                         label="Linear Regression of Rainfall",
                         title="Barcelona linear regression of rainfall")
    plt.scatter(yearly_rainfall["Year"].values.reshape(-1, 1),
                yearly_rainfall["Rainfall"].values,
                color="red",
                label="Rainfall")
    plt.legend()


def run():
    yearly_rainfall = retrieve_yearly_rainfall()
    avg_1970_2000 = get_average_yearly_rainfall(yearly_rainfall, 1970, 2000)
    avg_1980_2010 = get_average_yearly_rainfall(yearly_rainfall, 1980, 2010)
    avg_1990_2020 = get_average_yearly_rainfall(yearly_rainfall, 1990, 2020)

    print("Normal 1970 - 2000:", avg_1970_2000)
    print("Normal 1980 - 2010:", avg_1980_2010)
    print("Normal 1990 - 2020:", avg_1990_2020)

    add_deviation_from_normal(yearly_rainfall, avg_1980_2010)

    nb_years_above_normal = count_years_above_normal(yearly_rainfall)
    nb_years_below_normal = count_years_below_normal(yearly_rainfall)
    print("Number of years above normal:", nb_years_above_normal)
    print("Number of years below normal", nb_years_below_normal)

    apply_linear_regression_to_yearly_rainfall(yearly_rainfall)
    plot_yearly_rainfall_linear_regression(yearly_rainfall)

    apply_savgol_filter_to_yearly_rainfall(yearly_rainfall)
    plot_yearly_rainfall_savgol_filter(yearly_rainfall)

    plot_yearly_rainfall_deviation_from_normal(yearly_rainfall)
    plt.axhline(y=100.0, color='orange', linestyle="--", label="Normal")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    run()
