import geopandas as gpd
from os.path import dirname, join

def get_state(state):
    '''Extract an individual state from the DataFrame.

    Parameters
    ----------

    state : str
       The state to extract from the DataFrame.

    Returns
    -------
    df for a particular state.

    '''

    # load in the counties shape file

    module_path = dirname(__file__)
    df = gpd.read_file(join(module_path, 'shapefiles/cb_2018_us_county_500k/cb_2018_us_county_500k.shp'))

    # create a dictionary to map the 'STATEFP' values to each state
    state_dic = {'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06', 'CO': '08', 'CT': '09', 'DE': '10',
                 'DC': '11', 'FL': '12', 'GA': '13', 'HI': '15', 'ID': '16', 'IL': '17', 'IN': '18', 'IA': '19',
                 'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23', 'MD': '24', 'MA': '25', 'MI': '26', 'MN': '27',
                 'MS': '28', 'MO': '29', 'MT': '30', 'NE': '31', 'NV': '32', 'NH': '33', 'NJ': '34', 'NM': '35',
                 'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39', 'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44',
                 'SC': '45', 'SD': '46', 'TN': '47', 'TX': '48', 'UT': '49', 'VT': '50', 'VA': '51', 'WA': '53',
                 'WV': '54', 'WI': '55', 'WY': '56'}

    # use the dictionary key to create a state specific mask
    mask = df['STATEFP'] == state_dic[state]

    # use the mask to extract an individual state from the DataFrame
    state_df = df[mask]

    # return the DataFrame for the individual state
    return state_df