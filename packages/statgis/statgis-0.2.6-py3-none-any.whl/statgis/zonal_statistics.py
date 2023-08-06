import ee
import numpy as np
import pandas as pd

def zonal_statistics_image(Image, band, geom, scale, tileScale=2):
    '''
    Calc the mean, maximum, minimum standard deviation
    of a band ee:Image in the specified ee.Geometry.

    Parameters
    ----------
    Image : ee.Image
        Image to perfom the zonal statistics.

    band : str
        band of interest.

    geom : ee.Geometry
        Region of interest to calc the zonal statistics.

    scale : int or float
        Pixel size to perform the zonal statistics.

    Returns
    -------
    stats : pandas.DataFrame
        DataFrame with all the stats per column.

    '''
    mean = Image.reduceRegion(reducer=ee.Reducer.mean(), geometry=geom, scale=scale, tileScale=tileScale)
    maxi = Image.reduceRegion(reducer=ee.Reducer.max(), geometry=geom, scale=scale, tileScale=tileScale)
    mini = Image.reduceRegion(reducer=ee.Reducer.min(), geometry=geom, scale=scale, tileScale=tileScale)
    count = Image.reduceRegion(reducer=ee.Reducer.count(), geometry=geom, scale=scale, tileScale=tileScale)
    stdDev = Image.reduceRegion(reducer=ee.Reducer.stdDev(), geometry=geom, scale=scale, tileScale=tileScale)

    data = ee.Feature(
        geom=geom,
        opt_properties={
            'time':Image.get('system:time_start'),
        }
    )

    data = data.set('mean', mean.get(band)).set('max', maxi.get(band)).set('min', mini.get(band)).set('count', count.get(band)).set('std', stdDev.get(band))

    raw_values = data.getInfo()
    stats = pd.DataFrame(raw_values['properties'], index=[0])

    stats['time'] = pd.to_datetime(stats['time'], unit='ms')
    stats['time'] = pd.DatetimeIndex(stats['time'])
    
    return stats

def zonal_statistics_collection(ImageCollection, geom, scale, tileScale=16):  
    '''
    Calc the mean, maximum, minimum standard deviation
    of a band in all ee.Image in an ee.ImageCollection in the 
    specified ee.Geometry.

    Parameters
    ----------
    Image : ee.ImageCollection
        ImageCollection to perfom the zonal statistics.

    geom : ee.Geometry
        Region of interest to calc the zonal statistics.

    scale : int or float
        Pixel size to perform the zonal statistics.

    tileScale : int
        Scale of the mosaic to allow EarthEngine to split the task to more cores.

    Returns
    -------
    dataframe : pandas.DataFrame
        DataFrame with all the stats per column of all image.

    '''
    def minimal_zonal_statistics(Image):
        '''
        This is a minimal version of zonal_statistics_image function
        to be mapped in an ee.ImageCollection.
        '''
        stats = Image.reduceRegion(
            ee.Reducer.mean().combine(
                ee.Reducer.stdDev().combine(
                    ee.Reducer.max().combine(
                        ee.Reducer.min().combine(
                            ee.Reducer.count(),
                            sharedInputs=True
                        ),
                        sharedInputs=True
                    ),
                    sharedInputs=True
                ),
                sharedInputs=True
            ),
            geometry=geom,
            scale=scale,
            tileScale=tileScale
        )

        stats = ee.Feature(geom, stats)
        stats = stats.set('time', Image.get('system:time_start'))

        return stats

    fc = ee.FeatureCollection(ImageCollection.map(minimal_zonal_statistics))
    
    entries = [feature['properties'] for feature in fc.getInfo()['features']]

    keys = list(entries[0].keys())

    data = {key: [entry['properties'][key] for entry in entries] for key in keys}
    data = pd.DataFrame(data)
    data['date'] = pd.DatetimeIndex(pd.to_datetime(data['time'], unit='ms').dt.date)

    return None

def reduce_collection(ImageCollection, bands, geom, reducer, scale, tileScale=16):
    '''
    Reduce a ImageCollection to the given reducer in the selected bands 
    in the specified region.

    Parameters
    ----------
    ImageCollection : ee.ImageCollection
        ImageCollection to reduce.
    
    bands : list
        List with the name of the bands to reduce or the band name.

    geom : ee.Geometry
        Region of interest.

    reducer : string
        reducer to apply, it can be 'mean', 'max', 'min', 'count' or 'stdDev'.

    Scale : float
        Scale of image to perform the reduction.

    tileScale : int
        Scale of the mosaic to allow EarthEngine to split the task to more cores.

    Returns
    -------
    dataframe : pandas.dataframe
        Dataframe with the bandes reduced by region.
    '''
    
    if reducer == 'mean':
        ee_reducer = ee.Reducer.mean()
    elif reducer == 'max':
        ee_reducer = ee.Reducer.max()
    elif reducer == 'min':
        ee_reducer = ee.Reducer.min()
    elif reducer == 'count':
        ee_reducer = ee.Reducer.count()
    elif reducer == 'stdDev':
        ee_reducer = ee.Reducer.stdDev()

    def reduce_image(Image):
        stats = Image.reduceRegion(
            reducer = ee_reducer,
            geometry = geom,
            scale = scale,
            tileScale = tileScale
        )

        stats = ee.Feature(geom, stats)
        stats = stats.set('system:time_start', Image.get('system:time_start'))

        return stats

    fc = ee.FeatureCollection(ImageCollection.map(reduce_image))

    entries = [feature['properties'] for feature in fc.getInfo()['features']]
    
    data = pd.DataFrame(entries)
    data = data[bands+['system:time_start']]
    data['date'] = pd.DatetimeIndex(pd.to_datetime(data['system:time_start'], unit='ms').dt.date)

    return data