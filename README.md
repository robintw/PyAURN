# PyAURN - [![latest-version](https://img.shields.io/pypi/v/pyaurn)](https://pypi.org/project/pyaurn)

https://img.shields.io/pypi/l/pyaurn
This is a reworked fork of the `robintw/PyAURN` utilising pyreadr instead of rpy2. This negates having a local installation of R, and therefore can remain a python only configuration. 

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

# Download 4 years of data for the Southampton Central site
# (SOUT is the site ID for this site)
# Note: range(2015, 2019) will produce a list of four years: 2015, 2016, 2017 and 2018
data = importAURN("SOUT", range(2015, 2019))
```
