import ee
import pandas as pd

def extract_dates(ImageCollection):
    """
    Extract serie with the dates of all image in a Image Collection.

    Parameters
    ----------
    ImageCollection : ee.ImageCollection
        Collection to extract dates.

    Returns
    -------
    dates : pd.DatetimeIndex
        PanDas series with the image dates from the ImageCollection.
    """
    dates = (
        ImageCollection.reduceColumns(ee.Reducer.toList(), ["system:time_start"])
        .get("list")
        .getInfo()
    )
    dates = pd.to_datetime(dates, unit="ms")
    dates = pd.DatetimeIndex(dates)

    return dates


def trend(ImageCollection, band):
    """
    Add linear trend and stationally to an ImageCollection.

    Parameters
    ----------
    ImageCollection : ee.imageCollection
        ImageCollection to perform the linear trend and detrend.

    band : str
        Name of the band to perform the calc.

    Returns
    -------
    ImageCollection : ee.ImageCollection
        ImageCollection with the Raw data, Time, Trend and Statinally bands.
    """

    def time_func(Image):
        """Calc Time Band for linear regression"""
        time = (
            Image.metadata("system:time_start")
            .divide(1000 * 60 * 60 * 24 * 365)
            .rename("time")
        )
        Image = Image.addBands(time)
        return Image

    def pred_func(Image):
        """Calc Linear Trend band"""
        pred = (
            Image.select("time")
            .multiply(fitted.select("scale"))
            .add(fitted.select("offset"))
            .rename("predicted")
        )
        Image = Image.addBands(pred.toFloat())
        return Image

    def stat_func(Image):
        """Calc statinally band with mean restored"""
        stat = Image.expression(
            "band - pred + mean",
            {
                "band": Image.select(band),
                "pred": Image.select("predicted"),
                "mean": mean,
            },
        ).rename("stational")
        Image = Image.addBands(stat)
        return Image

    mean = ImageCollection.select(band).reduce(ee.Reducer.mean())

    ImageCollection = ImageCollection.map(time_func)
    ImageCollection = ImageCollection.select(["time", band])

    fitted = ImageCollection.reduce(ee.Reducer.linearFit())

    ImageCollection = ImageCollection.map(pred_func).map(stat_func)

    return ImageCollection


def reduce_by_year(ImageCollection, reducer, bands, start, end):
    """
    Function for calculate the reducer by year.

    Parameters
    ----------
    ImageCollection : ee.ImageCollection
        ImageCollection to perform the process.

    reducer : ee.Reducer
        ee.Reducer to apply.

    bands : list
        List with the band names to apply the reducer.

    start : int
        First year.

    end : int
        Last year.

    Returns
    -------
    yearly : ee.ImageCollection
        ImageCollection reduced by year.

    """
    years = ee.List.sequence(start, end)

    def filter_calc(year):
        """Filter and calculate the reducer by year"""
        data = ImageCollection.filter(ee.Filter.calendarRange(year, year, "year"))
        data = data.select(bands).reduce(reducer).set("year", year)
        return data

    yearly = ee.ImageCollection.fromImages(years.map(filter_calc))

    return yearly


def reduce_by_month(ImageCollection, reducer, bands):
    """
    Calc monthly statistics from an image based in the reducer
    required.

    Parameters
    ----------
    ImageCollection : ee.ImageCollection
        ImageCollection to perform the monthly statistical.

    reducer : ee.Reducer
        ee.Reducer to apply.

    bands : list
        List with the band names to apply the reducer.

    Returns
    -------
    monthly : ee.ImageCollection
        ImageCollection reduced by month.
    """
    months = ee.List.sequence(1, 12)

    def filter_calc(month):
        """Filter an calc the reducer by month"""
        data = ImageCollection.filter(ee.Filter.calendarRange(month, month, "month"))
        data = data.select(bands).reduce(reducer).set("month", month)
        return data

    monthly = ee.ImageCollection.fromImages(months.map(filter_calc))

    return monthly


def calc_anomalies(ImageCollection, monthly_mean):
    """
    Calc the anomalies of a ImageCollection subtracting the monthly mean values.

    Parameters
    ----------
    ImageCollection : ee.ImageCollection
        ImageCollection trended by the trend function to calc the anomalies.

    monthly_mean : ee.ImageCollection
        ImageCollection with the monthly means of ImageCollection calculated by the `reduce_by_month` function.

    Returns
    -------
    data : ee.ImageCollection
        ImageCollection with stational means added and anomalies calcualted.
    """
    def calc_anomaly(Image):
        """Function for calculate anomalies."""
        anomaly = Image.expression(
            "stat - mean",
            {"stat": Image.select("stational"), "mean": Image.select("stational_mean")},
        ).rename("anomaly")

        Image = Image.addBands(anomaly)

        return Image

    m01 = ImageCollection.filter(ee.Filter.calendarRange(1, 1, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 1)).first())
    )
    m02 = ImageCollection.filter(ee.Filter.calendarRange(2, 2, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 2)).first())
    )
    m03 = ImageCollection.filter(ee.Filter.calendarRange(3, 3, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 3)).first())
    )
    m04 = ImageCollection.filter(ee.Filter.calendarRange(4, 4, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 4)).first())
    )
    m05 = ImageCollection.filter(ee.Filter.calendarRange(5, 5, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 5)).first())
    )
    m06 = ImageCollection.filter(ee.Filter.calendarRange(6, 6, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 6)).first())
    )
    m07 = ImageCollection.filter(ee.Filter.calendarRange(7, 7, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 7)).first())
    )
    m08 = ImageCollection.filter(ee.Filter.calendarRange(8, 8, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 8)).first())
    )
    m09 = ImageCollection.filter(ee.Filter.calendarRange(9, 9, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 9)).first())
    )
    m10 = ImageCollection.filter(ee.Filter.calendarRange(10, 10, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 10)).first())
    )
    m11 = ImageCollection.filter(ee.Filter.calendarRange(11, 11, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 11)).first())
    )
    m12 = ImageCollection.filter(ee.Filter.calendarRange(12, 12, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 12)).first())
    )

    data = (
        m01.merge(m02)
        .merge(m03)
        .merge(m04)
        .merge(m05)
        .merge(m06)
        .merge(m07)
        .merge(m08)
        .merge(m09)
        .merge(m10)
        .merge(m11)
        .merge(m12)
    )

    data = data.sort("system:time_start")
    data = data.map(calc_anomaly)

    return data


def time_series_preocessing(ImageCollection, band):
    """
    Basic Time Series Processing.

    This function take an ee.ImageCollection and calculate the linear trend, the stational varaition, the stational mean and anomalies for the selected band.

    To calc the linear trend the function use `ee.Reducer.linearFit()`, next, calc the stational variation subtracting the linear_fitted values to the original series and restoring its mean, the monthly means are calculeted by selecting all the image in the specific month and reduce it by its mean, finally, subtracting the monthly means to the stational variation.

    This function is a "wrapper" function of `trend()`, `reduce_by_month()` and `calc_anomalies()`.

    Parameters
    ----------
    ImageCollection : ee.ImageCollection
        ImageCollection with the band to analyze.

    band : str
        Name of the band to perform the analyze.

    Returns
    -------
    data : ee.ImageCollection
        ImageCollection with the raw data, the linear trend, the stational variation, stational mean and the anomalies.

    monthly_mean : ee.ImageCollection
        ImageCollection with the twelves monthly means calculated.
    """

    trended = trend(ImageCollection, band)
    monthly_mean = reduce_by_month(trended, ee.Reducer.mean(), "stational")
    data = calc_anomalies(trended, monthly_mean)

    return data, monthly_mean
