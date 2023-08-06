import ee

def landsat_scaler(Image):
    '''
    Scale the optical and thermal bands from Landsat collections.

    Parameters
    ----------
    Image : ee.Image
        Image from Landsat Collection.

    Returns
    -------
    Image : ee.Image
        Image scaled.
    '''
    optical = Image.select('SR_B.').multiply(0.0000275).add(-0.2)
    thermal = Image.select('ST_B.*').multiply(0.00341802).add(149)
    
    Image = Image.addBands(optical, None, True).addBands(thermal, None, True)

    return Image

def landsat_cloud_mask(Image, all=True):
    '''
    Mask pixel clouds classifed in QA_PIXEL BAND for Image from
    Landsat Collection.

    Parameters
    ----------
    Image : ee.Image
        Image to be masked

    all : bool, optional
        If True, compute a mask for all classification values.

        If False, compute a mask only for cloud values.

    Returns
    -------
    Image : ee.Image
        Masked Image.
    '''
    qa = Image.select('QA_PIXEL')
    
    cirrus = qa.bitwiseAnd((1 << 2)).eq(0)
    cloud = qa.bitwiseAnd((1 << 3)).eq(0)
    shadow = qa.bitwiseAnd((1 << 4)).eq(0)
    snow = qa.bitwiseAnd((1 << 5)).eq(0)

    if all:
        Image = Image.updateMask(cirrus).updateMask(cloud).updateMask(shadow).updateMask(snow)
    else:
        Image = Image.updateMask(cloud)

    return Image

def landsat_ndvi_collection(ImageCollection, L8=True, add_bands=False):
    '''
    Calc NDVI for all image in an Landsat ImageCollection.

    Paremeters
    ----------
    ImageCollection : ee.ImageCollection
        ImageCollection with the image for NDVI calculation.

    L8 : bool, optional
        If True, The ImageCollection will be treated like a
        Landsat 8 (or 9) ImageCollection.

        If False, The ImageCollection will be treated like a
        Landsat 7 (or 4 or 5) ImageCollection.

    add_bands : bool, optional
        If True, The Image will be returned will all its bands.

        If False, the Image will be returned with only the NDVI
        calculated band.

    Returns
    -------
    ndvi : ee.ImageCollection
        Image collection with NDVI calculated.
    '''
    if L8:
        ndvi = ImageCollection.map(lambda x: x.addBands(x.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')))
    else:
        ndvi = ImageCollection.map(lambda x: x.addBands(x.normalizedDifference(['SR_B4', 'SR_B3']).rename('NDVI')))
    
    if not add_bands:
        ndvi = ndvi.select('NDVI')

    return ndvi

def landsat_ndvi(Image, L8=True):
    '''
    Calc NDVI for an Landsat Image.
    WARNING, this function can't be mapped

    Paremeters
    ----------
    Image : ee.Image
        Image for NDVI calculation.

    L8 : bool, optional
        If True, The Image will be treated like a
        Landsat 8 (or 9) Image.

        If False, The Image will be treate like a
        Landsat 7 (or 4 or 5) Image.

    Returns
    -------
    Image : ee.Image
        NDVI calculated.
    '''
    if L8:
        ndvi = Image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
    else: 
        ndvi = Image.normalizedDifference(['SR_B4', 'SR_B3']).rename('NDVI')

    Image.addBands(ndvi)

    return Image