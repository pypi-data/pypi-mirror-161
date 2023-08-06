import geopandas as gpd
from os.path import dirname, join

def load_states():
    """Loads the shapefile for states in the United States.

    Returns
    --------
    data : DataFrame
        DataFrame containing the shapefile for the United States.
    """
    module_path = dirname(__file__)
    df = gpd.read_file(join(module_path, 'cb_2018_us_state_500k/cb_2018_us_state_500k.shp'))
    df = df.drop([37, 38, 45])
    df = df.set_index('STUSPS')
    return df

def load_counties():
    """Loads the shapefile for counties in the United States.

    Returns
    -------
    data : DataFrame
        DataFrame containing the shapefile for the United States.
    """
    module_path = dirname(__file__)
    df = gpd.read_file(join(module_path, 'cb_2018_us_county_500k/cb_2018_us_county_500k.shp'))
    return df
