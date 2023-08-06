import ee

def sentinel_scaler(Image):
    '''
    Scale the optical bands from Sentinel 2 image.

    Parameters
    ----------
    Image : ee.Image
        Image to be scaled.

    Returns
    -------
    Image : ee.Image
        Scaled image.
    '''
    bands = Image.select('B.*').divide(10000)
    Image = Image.addBands(bands, None, True)

    return Image

def sentinel_cloud_mask(Image):
    '''
    Mask clouds for Sentinel 2 images using QA60
    band.

    Parameters
    ----------
    Image : ee.Image
        Image to be masked.

    Returns
    -------
    Image : ee.Image
        Masked image.
    '''
    qa = Image.select('QA60')

    cloud_mask = qa.bitwiseAnd((1 << 10)).eq(0)
    cirrus_mask = qa.bitwiseAnd((1 << 11)).eq(0)

    Image = Image.updateMask(cloud_mask).updateMask(cirrus_mask)
    
    return Image

def sentinel_probability_mask(Image, probability=20):
    '''
    Mask clouds for Sentinel 2 images using MSK_CLDPRB
    band.

    Parameters
    ----------
    Image : ee.Image
        Image to be masked.

    Returns
    -------
    Image : ee.Image
        Masked image.
    '''
    msk_cldprb = Image.select('MSK_CLDPRB')
    mask = msk_cldprb.lte(probability)

    Image = Image.updateMask(mask)

    return Image

def sentinel_ndvi_collection(ImageCollection, add_bands=False):
    '''
    Calc NDVI for a Sentinel 2 ImageCollection.

    Parameters
    ----------
    ImageCollection : ee.ImageCollection
        ImageCollection with the image to calc the NDVI.

    add_bands : bool, optional
        If True, return the original image with the NDVI
        added in a new band.

        If False, return a new image with only de NDVI calculated.

    Returns
    -------
    ndvi : ee.ImageCollection
        ImageCollection with the calculated NDVI per image.
    '''
    if add_bands:
        ndvi = ImageCollection.map(lambda x: x.addBands(x.normalizedDifference(['B8', 'B4']).rename('NDVI')))
    else:
        ndvi = ImageCollection.map(lambda x: x.normalizedDifference(['B8', 'B4']).rename('NDVI'))

    return ndvi

def sentinel_ndvi(Image:ee.Image) -> ee.Image:
    '''
    Calc NDVI for an ee.Image.

    Parameters
    ----------
    Image : ee.Image
        Image to calc NDVI.

    Returns
    Image : ee.Image
        Image with the NDVI calculated.
    '''
    ndvi = Image.normalizedDifference(['B8', 'B4']).rename('NDVI')

    Image = Image.addBands(ndvi)

    return Image