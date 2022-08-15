from urllib.request import urlretrieve
from urllib.error import HTTPError
import warnings
import pandas as pd
import pyreadr
from tqdm import tqdm

def _my_hook(t):
    """Wraps tqdm instance
    """
    last_b = [0]

    def update_to(b=1, bsize=1, tsize=None):
        """
        b  : int, optional
            Number of blocks transferred so far [default: 1].
        bsize  : int, optional
            Size of each block (in tqdm units) [default: 1].
        tsize  : int, optional
            Total size (in tqdm units). If [default: None] remains unchanged.
        """
        if tsize is not None:
            t.total = tsize
        t.update((b - last_b[0]) * bsize)
        last_b[0] = b

    return update_to

def _download_and_import_RData_file(url,**kwargs):
    site = kwargs.get('site', None)
    year = kwargs.get('year', None)

    if site is None:
        with tqdm(unit = 'B', unit_scale = True, unit_divisor = 1024, miniters = 1, desc = f"Downloading meta data:") as t:
            filename, headers = urlretrieve(url, reporthook = _my_hook(t))

    elif site is not None:
        with tqdm(unit = 'B', unit_scale = True, unit_divisor = 1024, miniters = 1, desc = f"Downloading data {site} {year}:") as t:
            filename, headers = urlretrieve(url, reporthook = _my_hook(t))
    
    # Load the RData file into R and get the name of the new variable created
    r_obj_name = pyreadr.read_r(filename)

    data = r_obj_name[list(r_obj_name)[0]]# let's check what objects we got

    # create the dataframe
    df = pd.DataFrame(data)

    return df

def importAURN(site, years):
    """
    Function to import a specific AURN site data across selected years. 
    Provide a site code (see importMeta for dataframe of sites) as a string, and a list of years.

    Parameters
    ----------
    site : str
        Site ID of the AURN station e.g. "MY1"
    years : list of int
        list of years of data to download. 

    Returns
    ----------
    pandas.DataFrame
        returns a pandas.DataFrame of the site data for selected years.
    """
    site = site.upper()

    # If a single year is passed then convert to a list with a single value
    if type(years) is int:
        years = [years]

    downloaded_data = []
    errors_raised = False

    for year in years:
        # Generate correct URL and download to a temporary file
        url = f"https://uk-air.defra.gov.uk/openair/R_data/{site}_{year}.RData"

        try:
            df = _download_and_import_RData_file(url,site=site,year=year)
        except HTTPError:
            errors_raised = True
            continue

        df = df.set_index('date')

        downloaded_data.append(df)

    if len(downloaded_data) == 0:
        final_dataframe = pd.DataFrame()
    else:
        final_dataframe = pd.concat(downloaded_data)

    if errors_raised:
        warnings.warn('Some data files were not able to be downloaded, check resulting DataFrame carefully')
    if len(final_dataframe) == 0:
        warnings.warn('Resulting DataFrame is empty')

    return final_dataframe

def importMeta():
    """
    Function to import a DataFrame of meta information for all the available to download AURN sites from the UK-AIR database.

    Parameters
    ----------
    None

    Returns
    ----------
    pandas.DataFrame
        returns a pandas.DataFrame of meta information for all available AURN sites.
    """
    df = _download_and_import_RData_file("http://uk-air.defra.gov.uk/openair/R_data/AURN_metadata.RData")

    df = df.drop_duplicates(subset=['site_id'])
    
    return df

def timeAverage(df,avg_time="daily",statistic="mean"):
    """
    Function to group the dataframe by a set time and specific statistic

    Parameters
    ----------
    avg_time : str
        time frequency with which to apply the grouping statistic. ["daily","month","year"]
    statistic : str
        statistical method to apply to group values. ["mean","max","min","median","sum"]

    Returns
    ----------
    pandas.DataFrame
        returns a pandas.DataFrame time averaged to specified frequency & statistic.
    """
    if avg_time == "daily":
        if statistic=="mean":
            time_df = df.groupby(pd.Grouper(freq='D')).mean()
        if statistic=="max":
            time_df = df.groupby(pd.Grouper(freq='D')).max()
        if statistic=="min":
            time_df = df.groupby(pd.Grouper(freq='D')).min()
        if statistic=="median":
            time_df = df.groupby(pd.Grouper(freq='D')).median()
        if statistic=="sum":
            time_df = df.groupby(pd.Grouper(freq='D')).sum()
                
    elif avg_time == "month":
        if statistic=="mean":
            time_df = df.groupby(pd.Grouper(freq='M')).mean()
        if statistic=="max":
            time_df = df.groupby(pd.Grouper(freq='M')).max()
        if statistic=="min":
            time_df = df.groupby(pd.Grouper(freq='M')).min()
        if statistic=="median":
            time_df = df.groupby(pd.Grouper(freq='M')).median()
        if statistic=="sum":
            time_df = df.groupby(pd.Grouper(freq='M')).sum()
    
    elif avg_time == "year":
        if statistic=="mean":
            time_df = df.groupby(pd.Grouper(freq='Y')).mean()
        if statistic=="max":
            time_df = df.groupby(pd.Grouper(freq='Y')).max()
        if statistic=="min":
            time_df = df.groupby(pd.Grouper(freq='Y')).min()
        if statistic=="median":
            time_df = df.groupby(pd.Grouper(freq='Y')).median()
        if statistic=="sum":
            time_df = df.groupby(pd.Grouper(freq='Y')).sum()
    return time_df
