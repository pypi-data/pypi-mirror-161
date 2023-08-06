import pandas as pd
import ee

def extract_dates(ImageCollection):
    '''
    Extract serie with the dates of all image in a 
    ImageCollection.

    Parameters
    ----------
    ImageCollection : ee.ImageCollection
        Collection to extract dates.
    
    Returns
    -------
    dates : pd.DatetimeIndex
        PanDas series with the image dates from the ImageCollection.
    '''
    dates = ImageCollection.reduceColumns(ee.Reducer.toList(), ['system:time_start']).get('list').getInfo()
    dates = pd.to_datetime(dates, unit='ms')
    dates = pd.DatetimeIndex(dates)

    return dates

def trend(ImageCollection, band):
    '''
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
    '''
    def time_func(Image: ee.Image) -> ee.Image:
        '''Calc Time Band for linear regression'''
        time = Image.metadata('system:time_start').divide(1000*60*60*24*365).rename('time')
        Image = Image.addBands(time)
        return Image
    
    def pred_func(Image: ee.Image) -> ee.Image:
        '''Calc Linear Trend band'''
        pred = Image.select('time').multiply(fitted.select('scale')).add(fitted.select('offset')).rename('predicted')
        Image = Image.addBands(pred.toFloat())
        return Image

    def stat_func(Image: ee.Image) -> ee.Image:
        '''Calc statinally band with mean restored'''
        stat = Image.expression(
            'band - pred + mean',
            {'band': Image.select(band), 'pred': Image.select('predicted'), 'mean': mean}
        ).rename('stational')
        Image = Image.addBands(stat)
        return Image
    
    mean = ImageCollection.select(band).reduce(ee.Reducer.mean())

    ImageCollection = ImageCollection.map(time_func)
    ImageCollection = ImageCollection.select(['time', band])
    
    fitted = ImageCollection.reduce(ee.Reducer.linearFit())

    ImageCollection = ImageCollection.map(pred_func).map(stat_func)

    return ImageCollection

def year_mean(ImageCollection, reducer, band, start, end):
    '''
    Function for calculate the reducer by year.

    Parameters
    ----------
    ImageCollection : ee.ImageCollection
        ImageCollection to perform the monthly statistical.

    reducer : ee.Reducer
        ee.Reducer to apply.

    band : str
        Name of the band to apply the reducer.

    start : int
        First year.

    end : int
        Last year.

    Returns
    -------
    yearly : ee.ImageCollection
        ImageCollection reduced by year.
    
    '''
    years = ee.List.sequence(start, end)

    def filter_calc(year):
        '''Filter and calculate the reducer by year'''
        data = ImageCollection.filter(ee.Filter.calendarRange(year, year, 'year'))
        data = data.select(band).reduce(reducer).set('year', year)
        return data

    yearly = ee.ImageCollection.fromImages(years.map(filter_calc))
    
    return yearly

def montlhy_calc(ImageCollection, reducer, band):
    ''''
    Calc monthly statistics from an image based in the reducer
    required.

    Parameters
    ----------
    ImageCollection : ee.ImageCollection
        ImageCollection to perform the monthly statistical.

    reducer : ee.Reducer
        ee.Reducer to apply.

    band : str
        Name of the band to apply the reducer.

    Returns
    -------
    monthly : ee.ImageCollection
        ImageCollection reduced by month.
    '''
    months = ee.List.sequence(1, 12)

    def filter_calc(month):
        '''Filter an calc the reducer by month'''
        data = ImageCollection.filter(ee.Filter.calendarRange(month, month, 'month'))
        data = data.select(band).reduce(reducer).set('month', month)
        return data

    monthly = ee.ImageCollection.fromImages(months.map(filter_calc))
    
    return monthly

def calc_anomalies(ImageCollection, monthly_mean):
    '''
    Calc the anomalies of a ImageCollection subtracting
    the monthly mean values.

    Parameters
    ----------
    ImageCollection : ee.ImageCollection
        ImageCollection trended by the trend function to
        calc the anomalies.

    monthly_mean : ee.ImageCollection
        ImageCollection with the monthly means of ImageCollection
        calculated by the `monthly_calc` function.

    Returns
    -------
    adata : ee.ImageCollection
        ImageCollection with stational means added and anomalies
        calcualted.
    '''
    # adata = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterDate('1998-12-31', '1999-01-01')
    m_idx = [i for i in range(1, 13)]

    def add_monthly_mean(Image):
        '''Add monthly mean from mothly_mean ee.ImageCollection'''
        Image = Image.addBands(monthly_mean.filter(ee.Filter.eq('month', i)).first())
        
        return Image

    def calc_anomaly(Image):
        '''Function for calc anomalies.'''
        anomaly = Image.expression(
            'stat - mean',
            {
                'stat': Image.select('stational'),
                'mean': Image.select('stational_mean')
            }
        ).rename('anomaly')

        Image = Image.addBands(anomaly)
        
        return Image

    for i in m_idx:
        data = ImageCollection.filter(ee.Filter.calendarRange(i, i, 'month'))
        data = data.map(add_monthly_mean)
        
        if i == 1:
            adata = data
        else:
            adata = adata.merge(data)

    adata = adata.sort('system:time_start')
    adata = adata.map(calc_anomaly)
    
    return adata

def basic_tsp(ImageCollection, band):
    '''
    Basic Time Series Processing.

    This function take an ee.ImageCollection and calc
    the linear trend, the stational varaition, the
    stational mean and anomalies for the selected band.

    To calc the linear trend the function use 
    `ee.Reducer.linearFit()`, next, calc the stational
    variation subtracting the linear_fitted values to the
    original series and restoring its mean, the monthly means
    are calculeted by selecting all the image in the 
    specific month and reduce it by its mean, finally, subtracting
    the monthly means to the stational variation.

    This function is a "wrapper" function of
    `trend()`, `monthly_mean()` and `calc_anomalies()`.

    Parameters
    ----------
    ImageCollection : ee.ImageCollection
        ImageCollection with the band to analyze.

    band : str
        Name of the band to perform the analyze.

    Returns
    -------
    tsp : ee.ImageCollection
        ImageCollection with the raw data, the linear trend, the
        stational variation, stational mean and the anomalies.

    monthly_mean : ee.ImageCollection
        ImageCollection with the twelves monthly means calculated.
    '''

    trended = trend(ImageCollection, band)
    monthly_mean = montlhy_calc(trended, ee.Reducer.mean(), 'stational')
    tsp = calc_anomalies(trended, monthly_mean)
    
    return tsp, monthly_mean
    