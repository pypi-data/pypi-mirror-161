import ee
import numpy as np
import pandas as pd

def zonal_statistics_image(Image, band, geom, scale, tileScale):
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
            'system:time_start':Image.get('system:time_start'),
        }
    )

    data = data.set('mean', mean.get(band)).set('max', maxi.get(band)).set('min', mini.get(band)).set('count', count.get(band)).set('std', stdDev.get(band))

    raw_values = data.getInfo()
    stats = pd.DataFrame(raw_values['properties'], index=[0])

    return stats

def zonal_statistics_collection(ImageCollection, band, geom, scale, tileScale):  
    '''
    Calc the mean, maximum, minimum standard deviation
    of a band in all ee.Image in an ee.ImageCollection in the 
    specified ee.Geometry.

    Parameters
    ----------
    Image : ee.ImageCollection
        ImageCollection to perfom the zonal statistics.

    band : str
        band of interest.

    geom : ee.Geometry
        Region of interest to calc the zonal statistics.

    scale : int or float
        Pixel size to perform the zonal statistics.

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

        data = ee.Feature(
            geom=geom,
            opt_properties={
                'system:time_start':Image.get('system:time_start'),
            }
        )

        data = data.set('mean', stats.get(band+'_mean')).set('max', stats.get(band+'_max')).set('min', stats.get(band+'_min')).set('count', stats.get(band+'_count')).set('std', stats.get(band+'_stdDev'))

        return data

    fc = ee.FeatureCollection(ImageCollection.map(minimal_zonal_statistics))
    raw_data = fc.getInfo()['features']

    idx = np.arange(len(raw_data))

    for i in idx:
        data = pd.DataFrame(raw_data[i]['properties'], index=[i])

        if i == 0:
            dataframe = data
        else:
            dataframe = pd.concat([dataframe, data])

    return dataframe
