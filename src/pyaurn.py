from urllib.request import urlretrieve
from urllib.error import HTTPError
import warnings
import pandas as pd
import pyreadr
from tqdm import tqdm
import ssl
import windrose

def __my_hook(t):
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

def __download_and_import_RData_file(url,**kwargs):
    site = kwargs.get('site', None)
    year = kwargs.get('year', None)

    ## fix for ssl certificate error: likely needs better solution, but works for now as calling trusted urls
    ssl._create_default_https_context = ssl._create_unverified_context
    if site is None:
        with tqdm(unit = 'B', unit_scale = True, unit_divisor = 1024, miniters = 1, desc = f"Downloading meta data:") as t:
            filename, headers = urlretrieve(url, reporthook = __my_hook(t))

    elif site is not None:
        with tqdm(unit = 'B', unit_scale = True, unit_divisor = 1024, miniters = 1, desc = f"Downloading data {site} {year}:") as t:
            filename, headers = urlretrieve(url, reporthook = __my_hook(t))
    
    # Load the RData file into python variable using pyreadr
    r_obj_name = pyreadr.read_r(filename)

    # get the first object in the list which is data
    data = r_obj_name[list(r_obj_name)[0]]

    # create the dataframe
    df = pd.DataFrame(data)

    return df

def __download_and_import_gz_file(url,**kwargs):
    site = kwargs.get('site', None)
    year = kwargs.get('year', None)

    ## fix for ssl certificate error: likely needs better solution, but works for now as calling trusted urls
    ssl._create_default_https_context = ssl._create_unverified_context
    if site is None:
        with tqdm(unit = 'B', unit_scale = True, unit_divisor = 1024, miniters = 1, desc = f"Downloading meta data:") as t:
            filename, headers = urlretrieve(url, reporthook = __my_hook(t))

    elif site is not None:
        with tqdm(unit = 'B', unit_scale = True, unit_divisor = 1024, miniters = 1, desc = f"Downloading data {site} {year}:") as t:
            filename, headers = urlretrieve(url, reporthook = __my_hook(t))
    
    # Load the RData file into R and get the name of the new variable created
    df = pd.read_csv(filename, compression='gzip',
                    error_bad_lines=False)
    return df

def importMeta(source="aurn"):
    """
    Function to import a DataFrame of meta information for a selected source of air quality data.

    Parameters
    ----------
    source : str
        Source of meta data to download. ["aurn","saqn","aqe","waqn","ni"]. Default is "aurn".

    Returns
    ----------
    pandas.DataFrame
        returns a pandas.DataFrame of meta information for all available AURN sites.
    """
    source_dict = {"aurn":"http://uk-air.defra.gov.uk/openair/R_data/AURN_metadata.RData",
                   "saqn":"https://www.scottishairquality.scot/openair/R_data/SCOT_metadata.RData",
                   "aqe":"https://airqualityengland.co.uk/assets/openair/R_data/AQE_metadata.RData",
                   "waqn":"https://airquality.gov.wales/sites/default/files/openair/R_data/WAQ_metadata.RData",
                   "ni":"https://www.airqualityni.co.uk/openair/R_data/NI_metadata.RData"}

    df = __download_and_import_RData_file(source_dict[source])

    df = df.drop_duplicates(subset=['site_id'])
    
    return df

def importAURN(site, years,pollutant="all",hc=False,meta=False):
    """
    Function to import a specific AURN site data across selected years. 
    Provide a site code (see importMeta for dataframe of sites) as a string, and a list of years.

    Parameters
    ----------
    site : str
        Site ID of the AURN station e.g. "MY1"
    years : list of int
        list of years of data to download. 
    pollutant : str
        Pollutants to import. If omitted will import all pollutants from a site. To import only NOx and NO2 for example use pollutant = ["nox", "no2"].
    hc : bool
        A few sites have hydrocarbon measurements available and setting hc = True will ensure hydrocarbon data are imported. The default is however not to as most users will not be interested in using hydrocarbon data and the resulting data frames are considerably larger.
    meta : bool
        Should meta data be returned? If True all meta information is returned.
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
            df = __download_and_import_RData_file(url,site=site,year=year)
        except HTTPError:
            errors_raised = True
            continue
        
        ## not sure why this is here. May remove in future. 
        # df = df.set_index('date')

        downloaded_data.append(df)

    if len(downloaded_data) == 0:
        final_dataframe = pd.DataFrame()
    else:
        if pollutant == "all" and hc == True:
            init_df = pd.concat(downloaded_data)
            features = ['site','code']+df.columns.drop(['site','code']).to_list()
            final_dataframe = init_df[features]

        elif pollutant == "all" and hc == False:
            features = ['site','code','date', 'O3', 'NO', 'NO2','NOXasNO2', 'SO2', 'CO', 'PM10', 'NV10',   
       'V10', 'PM2.5', 'NV2.5', 'V2.5','AT10', 'AP10', 'AT2.5',
       'AP2.5','ws','wd','temp']
            final_dataframe = pd.concat(downloaded_data)[features]
        else:
            features = ['site','code','date']+pollutant+['ws','wd','temp']
            final_dataframe = pd.concat(downloaded_data)[features]

    if errors_raised:
        warnings.warn('Some data files were not able to be downloaded, check resulting DataFrame carefully')
    if len(final_dataframe) == 0:
        warnings.warn('Resulting DataFrame is empty')

    if meta == True:
        meta_df = importMeta()
        final_dataframe = pd.merge(final_dataframe,meta_df,how='left',left_on='code',right_on='site_id')
        final_dataframe = final_dataframe.drop(columns=['site_id'])

    return final_dataframe

def importUKAQ(site, years,source="aurn"):

    """
    Function to import a specific site data across selected years, from a number of different sources across the UK. 
    Provide a site code (see importMeta for dataframe of sites) as a string, a year or list of years, and also the source.

    Parameters
    ----------
    site : str
        Site ID of the station e.g. "MY1"
    years : list of int
        list of years of data to download. 
    source : str
        Source of data to download. ["aurn","saqn","aqe","waqn","ni"]. Default is "aurn".

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

    source_dict = {"aurn":"https://uk-air.defra.gov.uk/openair/R_data/",
                   "saqn":"https://www.scottishairquality.scot/openair/R_data/",
                   "aqe":"https://airqualityengland.co.uk/assets/openair/R_data/",
                   "waqn":"https://airquality.gov.wales/sites/default/files/openair/R_data/",
                   "ni":"https://www.airqualityni.co.uk/openair/R_data/"}

    source_url = source_dict[source]

    for year in years:
        # Generate correct URL and download to a temporary file
        url = f"{source_url}{site}_{year}.RData"

        try:
            df = __download_and_import_RData_file(url,site=site,year=year)
        except HTTPError:
            errors_raised = True
            continue

        ## not sure why this is here. May remove in future. 
        # df = df.set_index('date')

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

def importEurope(site,years):
    """
    Function to import a DataFrame of air quality data from a European station - based on R {saqgetr}.

    Parameters
    ----------
    site : str
        Site ID of the station e.g. "MY1"
    years : list of int
        list of years of data to download. 
    Returns
    ----------
    pandas.DataFrame
        returns a pandas.DataFrame of air quality data for selected years.
    """

    # If a single year is passed then convert to a list with a single value
    if type(years) is int:
        years = [years]

    downloaded_data = []
    errors_raised = False

    for year in years:
        # Generate correct URL and download to a temporary file
        url = f"http://aq-data.ricardo-aea.com/R_data/saqgetr/observations/{year}/air_quality_data_site_{site}_{year}.csv.gz"

        try:
            df = __download_and_import_gz_file(url,site=site,year=year)
      
        except HTTPError:
            errors_raised = True
            continue

        ## not sure why this is here. May remove in future. 
        # df = df.set_index('date')

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
        time_df = df.groupby(pd.Grouper(freq='D')).agg(statistic)
    elif avg_time == "month":
        time_df = df.groupby(pd.Grouper(freq='M')).agg(statistic)
    elif avg_time == "year":
        time_df = df.groupby(pd.Grouper(freq='Y')).agg(statistic)
    return time_df

def windRose(df,save=False):
    """
    Function to plot a wind rose from a dataframe of wind speed and direction. 
    Uses the windrose package - https://python-windrose.github.io/windrose/index.html - Lionel Roubeyrie & Sebastien Celles. 

    Parameters
    ----------
    df : pandas.DataFrame
        dataframe containing wind speed and direction columns.
    save : bool
        whether to save the plot to a file. Default is False.

    Returns
    ----------
    matplotlib.pyplot
        returns a matplotlib.pyplot wind rose plot.
    """
    ax = windrose.plot_windrose(df,kind='bar',var_name='ws',direction_name='wd',normed=True)
    years = set([df['date'].min().strftime('%Y'),df['date'].max().strftime('%Y')])
    # concat the years into a string
    years = "-".join(years)

    ax.set_title(f"{df['site'][0]} - {df['code'][0]} - {years} Wind Rose")
    ax
    if save == True:
        fig = ax.get_figure()
        fig.savefig(f"{df['site'][0]}_wind_rose.png")