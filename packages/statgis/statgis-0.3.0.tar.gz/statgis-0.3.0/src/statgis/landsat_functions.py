import ee

def landsat_scaler(Image):
    """
    Scale the optical and thermal bands from Landsat collections.

    Parameters
    ----------
    Image : ee.Image
        Image from Landsat Collection.

    Returns
    -------
    Image : ee.Image
        Image scaled.
    """
    optical = Image.select("SR_B.").multiply(0.0000275).add(-0.2)
    thermal = Image.select("ST_B.*").multiply(0.00341802).add(149)

    Image = Image.addBands(optical, None, True).addBands(thermal, None, True)

    return Image


def landsat_cloud_mask(Image, all=True):
    """
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
    """
    qa = Image.select("QA_PIXEL")

    cirrus = qa.bitwiseAnd((1 << 2)).eq(0)
    cloud = qa.bitwiseAnd((1 << 3)).eq(0)
    shadow = qa.bitwiseAnd((1 << 4)).eq(0)
    snow = qa.bitwiseAnd((1 << 5)).eq(0)

    if all:
        Image = (
            Image.updateMask(cirrus)
            .updateMask(cloud)
            .updateMask(shadow)
            .updateMask(snow)
        )
    else:
        Image = Image.updateMask(cloud)

    return Image
