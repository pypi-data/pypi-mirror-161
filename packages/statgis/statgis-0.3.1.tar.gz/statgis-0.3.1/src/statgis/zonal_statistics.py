import ee
import pandas as pd

def zonal_statistics_image(Image, geom, scale, bands="all", reducer="all", tileScale=16):
    """
    Function to calculate a statistic in the specified region for al Image in a Image Collection.

    Parameters
    ----------
    Image : ee.Image
        Image of interest.

    geom : ee.Geometry
        Region of interest to reduce the image.

    scale : float
        Pixel size for the sample to perform the zonal statistics.

    bands : iterable
        List, tuple with the bands of interest or, if you only want one band, the name of the band. By default the process takes into consideration all bands.

    reducer : ee.Reducer
        Reducer to apply to all image. By default, image are reduced to its, mean, standard deviation, maximum, minimum, and count.

    tileScale : int
        Scale of the mosaic to allow EarthEngine to split the task to more cores.

    Return
    ------
    data : pandas.DataFrame
        DataFrame with all the stats for all spcified bands.
    """
    if bands != "all":
        Image = Image.select(bands)

    if reducer == "all":
        reducer = ee.Reducer.mean().combine(
            ee.Reducer.stdDev().combine(
                ee.Reducer.max().combine(
                    ee.Reducer.min().combine(ee.Reducer.count(), sharedInputs=True),
                    sharedInputs=True,
                ),
                sharedInputs=True,
            ),
            sharedInputs=True,
        )

    stats = Image.reduceRegion(
        reducer=reducer, geometry=geom, scale=scale, tileScale=tileScale
    )
    stats = stats.set("system:time_start", Image.get("system:time_start"))

    data = pd.DataFrame(stats.getInfo(), index=[0])
    data["date"] = pd.DatetimeIndex(
        pd.to_datetime(data["system:time_start"], unit="ms").dt.date
    )

    return data


def zonal_statistics_collection(
    ImageCollection, geom, scale, bands="all", reducer="all", tileScale=16
):
    """
    Function to calculate a statistic in the specified region for al Image in a Image Collection.

    Parameters
    ----------
    ImageCollection : ee.ImageCollection
        Image Collection with the image to analyse.

    geom : ee.Geometry
        Region of interest to reduce the images.

    scale : float
        Pixel size for the sample to perform the zonal statistics.

    bands : iterable
        List, tuple with the bands of interest or, if you only want one band, the name of the band. By default the process takes into consideration all bands.

    reducer : ee.Reducer
        Reducer to apply to all image. By default, Images are reduced to its, mean, standard deviation, maximum, minimum, and count.

    tileScale : int
        Scale of the mosaic to allow EarthEngine to split the task to more cores.

    Return
    ------
    data : pandas.DataFrame
        DataFrame with all the stats for all spcified bands.
    """
    if bands != "all":
        ImageCollection = ImageCollection.map(lambda image: image.select(bands))

    if reducer == "all":
        reducer = ee.Reducer.mean().combine(
            ee.Reducer.stdDev().combine(
                ee.Reducer.max().combine(
                    ee.Reducer.min().combine(ee.Reducer.count(), sharedInputs=True),
                    sharedInputs=True,
                ),
                sharedInputs=True,
            ),
            sharedInputs=True,
        )

    def reduce_image(Image):
        stats = Image.reduceRegion(
            reducer=reducer, geometry=geom, scale=scale, tileScale=tileScale
        )

        stats = ee.Feature(geom, stats)
        stats = stats.set("system:time_start", Image.get("system:time_start"))

        return stats

    fc = ee.FeatureCollection(ImageCollection.map(reduce_image))

    entries = [feature["properties"] for feature in fc.getInfo()["features"]]

    data = pd.DataFrame(entries)
    data["date"] = pd.DatetimeIndex(
        pd.to_datetime(data["system:time_start"], unit="ms").dt.date
    )

    return data
