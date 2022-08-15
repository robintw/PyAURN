# PyAURN - [![latest-version](https://img.shields.io/pypi/v/pyaurn)](https://pypi.org/project/pyaurn)

This is a rework of the original function, utilising pyreadr instead of rpy2. This negates having a local installation of R, and therefore can remain a python only configuration. 

This is a simple Python package to import data from the UK Automatic Urban Rural Network - an air pollution network run by the UK government.

This is a Python port of a couple of functions of the [openair](http://www.openair-project.org/) R package. This R package
relies on data provided as a set of .RData files on the Defra website, specifically designed for use by the openair project. This Python
package relies on the same data. 

## Getting started
Install the via pip: 

`pip install pyaurn`
  
  
Run the two functions in the package as below:

```python
from pyaurn import importAURN, importMetadata

# Download metadata of site IDs, names, locations etc
metadata = importMetadata()

# Download 4 years of data for the Marylebone Road site
# (MY1 is the site ID for this site)
# Note: range(2016, 2022) will produce a list of six years: 2016, 2017, 2018, 2019, 2020, and 2021. Alternatively define a list of years to use eg. [2016,2017,2018,2019,2020,2021]
data = importAURN("MY1", range(2016, 2022))
```

## Future developments

* integrate other openair functions
* open to suggestions 