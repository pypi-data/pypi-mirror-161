import pandas as pd
import requests
from progressbar import ProgressBar

pbar = ProgressBar()
# create progress bar for the loop

# Construct function to make api call for qwi
def get_qwi(state = '24', key = "your api key", the_vars = ['Emp', 'TurnOvrS', 'EarnBeg']):
    """ Get data from Quarterly Workforce Indicators

    Parameters
    ----------
    state: str
        a string with the state fips code (i.e.: '27' for Minnesota, '01' for Alabama).
    key: str
        your api key, you should get it from census: https://api.census.gov/data/key_signup.html
    the_vars: list
        a list of the variables you want to request from QWI

    Returns
    -------
    A pandas data frame for the requested state QWI data. pd.DataFrame object

    Examples
    --------
    >>> get_qwi(state = '24', key = 'your api key', the_vars= ['Emp', 'TurnOverS', 'EarnBeg'])
    """
    HOST = 'http://api.census.gov/data/timeseries/qwi/sa?'
    get_vars = the_vars
    predicates = {}
    predicates['get'] = ",".join(get_vars)
    predicates['for'] = 'county:*'
    predicates['in'] = 'state:' + state
    predicates['sex'] = '0'
    predicates['agegrp'] = 'A00'
    predicates['industry'] = '6244'
    predicates['ownercode'] = 'A00'
    predicates['time'] = 'from 2001-Q1 to 2007-Q4'
    predicates['seasonadj'] = 'U'
    predicates['key'] = f'{key}'
    r = requests.get(HOST, params = predicates)
    df = pd.DataFrame(data = r.json()[1:])
    return df # columns = r.json()[0],


def create_qwi_df(states = "states", col_names = "col_names", my_key = "your key"):
    """ Get QWI data for a list of states and concatenate into a pandas dataframe

    Parameters
    ----------
    states: str or list
        if you need a single state QWI data input it as a string. If you need more than one state, use a list
    col_names: list
        a list with strings defining the names of the new column. This is evolving and might be modified
    my_key: str
        a string with the api key you get from census: https://api.census.gov/data/key_signup.html

    Returns
    -------
    A pandas dataframe: pd.DataFrame object

    Examples
    --------
    >>> col_names = ['emp', 'turn_overs', 'earn_beg', 'sex', 'age_group', 'industry', 'owner_code','quarter', 'season_adj', 'state', 'county']
    >>> api_key = "Your api key"
    >>> create_qwi_df(states = ['01', '27'], col_names = col_names, my_key = api_key)
    """
    appended_data = []
    if isinstance(states, list):
        print("Getting your states...")
        for st in pbar(states):
            df = get_qwi(state = st, key=my_key)
            appended_data.append(df)
    elif isinstance(states, str):
        print("Getting your state...")
        df = get_qwi(state = states, key=my_key)
        appended_data.append(df)
    data = pd.concat(appended_data)
    data.columns = col_names
    return data