import ee
import numpy as np

def sample_image(Image, band, geom, scale):
    """
    Sample all pixel values in the specified band from the ee.Image.

    Parameters
    ----------
    Image : ee.Image
        Image to be sampled.
    band : str
        Band of interest.
    geom : ee.Geometry or ee.Feature or ee.FeatureCollection Region of interest to sample
    scale : float
        Pixelsize of image to be sampled.

    Returns
    -------
    data : np.array
        Array with all the values sampled.
    """
    if type(geom) == ee.geometry.Geometry:
        geom = ee.FeatureCollection([ee.Feature(geom, {"id": 0})])
    elif type(geom) == ee.feature.Feature:
        geom == ee.FeatureCollection(geom)
    try:
        sample = Image.sampleRegions(collection=geom, scale=scale, geometries=False)

        sample = sample.toList(sample.size())
        raw = sample.getInfo()

        data = np.array([r["properties"][band] for r in raw])
    except:
        data = np.array([np.nan])

    return data


def sample_collection(ImageCollection, band, geom, scale):
    """
    This function sample all ee.Image in an ee.ImageCollection applying the sample_image function to all ee.Image.

    Parameters
    ----------
    Image : ee.ImageCollection
        ImageCollection with the ee-Image of interest to be sampled.
    band : str
        Band of interest.
    geom : ee.Geometry or ee.Feature or ee.FeatureCollection
        Region of interest to sample
    scale : float
        Pixelsize of image to be sampled.

    Returns
    -------
    data : list
        list of np.array with ell the sampled values per image.
    """
    N = ImageCollection.size().getInfo()
    ic_list = ImageCollection.toList(N)

    data = []

    for i in range(N):
        image = ee.Image(ic_list.get(i))
        values = sample_image(image, band=band, geom=geom, scale=scale)
        data.append(values)

    return data
