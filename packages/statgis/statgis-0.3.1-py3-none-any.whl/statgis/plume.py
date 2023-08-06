import ee

def plume_characterization(
    Image, sample_region, blue="SR_B2", green="SR_B3", red="SR_B4", nir="SR_B5"
):
    """
    Extract river plume from a ee.Image.

    Parameters
    ----------
    Image : ee.Image
        Image to be classified.
    sample_region : ee.Geometry
        Polygon that enclosess a region of the Image that the user indetifies as river plume.
    blue : str, optional
        Key of ee.Image blue band (by default SR_B2).
    green : str, optional
        Key of ee.Image green band (by default SR_B3).
    red : str, optional
        Key of ee.Image red band (by default SR_B4).
    nir : str, optional
        Key of ee.Image nir band (by default SR_B5).

    Returns
    -------
    plume : ee.Image
        Plume characterized in the three color bands of Image.
    """
    Image = Image.addBands(
        Image.expression(
            f"(b('{green}') - b('{nir}'))/(b('{green}') + b('{nir}'))"
        ).rename("NDWI"),
        None,
        True,
    )

    mask = Image.select("NDWI").gt(0)
    Image = Image.updateMask(mask)

    reducer = ee.Reducer.min().combine(reducer2=ee.Reducer.max(), sharedInputs=True)

    limits = Image.select([blue, green, red]).reduceRegion(
        reducer=reducer, geometry=sample_region, scale=30
    )

    Image = Image.addBands(
        Image.expression(
            f"(b('{blue}') > MINI && b('{blue}') < MAXI) ? 1 : 0",
            {
                "MAXI": limits.getNumber(blue + "_max"),
                "MINI": limits.getNumber(blue + "_min"),
            },
        ).rename("plume_blue"),
        None,
        True,
    )

    Image = Image.addBands(
        Image.expression(
            f"(b('{green}') > MINI && b('{green}') < MAXI) ? 1 : 0",
            {
                "MAXI": limits.getNumber(green + "_max"),
                "MINI": limits.getNumber(green + "_min"),
            },
        ).rename("plume_green"),
        None,
        True,
    )

    Image = Image.addBands(
        Image.expression(
            f"(b('{red}') > MINI && b('{red}') < MAXI) ? 1 : 0",
            {
                "MAXI": limits.getNumber(red + "_max"),
                "MINI": limits.getNumber(red + "_min"),
            },
        ).rename("plume_red"),
        None,
        True,
    )

    Image = Image.addBands(
        Image.expression(
            "(b('plume_blue') + b('plume_green') + b('plume_red'))/3"
        ).rename("plume"),
        None,
        True,
    )

    plume_mask = Image.select("plume").gt(0.5)

    pixel_count = plume_mask.select(0).connectedPixelCount(100, False)
    count_mask = pixel_count.select(0).gt(50)

    Image = Image.updateMask(plume_mask).updateMask(count_mask)

    return Image
