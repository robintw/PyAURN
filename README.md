# PyAURN - [![latest-version](https://img.shields.io/pypi/v/pyaurn)](https://pypi.org/project/pyaurn)


This is a Python port of functions of the [openair](https://davidcarslaw.github.io/openair/) R package. The openair R package
relies on data provided as a set of .RData files on the Defra website, specifically designed for use by the openair project. This Python
package relies on the same data, however imports it into a Python friendly pandas dataframe without the need for R by utilising the [pyreadr](https://pypi.org/project/pyreadr) package.

## Getting started
Install the via pip: 

`pip install pyaurn`
  
  
Example quickstart functions in the package as below:

```python
from pyaurn import importAURN, importMeta, timeAverage

# Download metadata of site IDs, names, locations etc
metadata = importMeta()

# Download 4 years of data for the Marylebone Road site
# (MY1 is the site ID for this site)
# Note: range(2016, 2022) will produce a list of six years: 2016, 2017, 2018, 2019, 2020, and 2021. 
# Alternatively define a list of years to use eg. [2016,2017,2018,2019,2020,2021]
data = importAURN("MY1", range(2016, 2022))

# Group the DataFrame by a frequency of monthly, and the statistic mean(). 
data_monthly = timeAverage(data,avg_time="month",statistic="mean")
```

## Current Functions
The following functions are currently available in the package:
* importMeta - download meta information on the different sents for specified data source.
* importAURN - import AURN data for a specified site and year(s).
* importUKAQ - import UK Air Quality data for a specified site, year(s), and data source.
* importEurope - import European Air Quality data for a specified site, year(s) - WIP (final dataframe format needs widening to clean pollutants)
* timeAverage - time average the data to a specified frequency and statistic.


## Future developments

* integrate other openair functions
* open to suggestions (please leave enhancement tag in [Issues](https://www.github.com/robintw/PyAURN/issues))