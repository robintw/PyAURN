# PyAURN
This is a simple Python module to import data from the UK Automatic Urban Rural Network - an air pollution network run by the UK government.

This is basically a Python port of a couple of functions of the [openair](http://www.openair-project.org/) R package. This R package
relies on data provided as a set of .RData files on the Defra website, specifically designed for use by the openair project. This Python
package relies on the same data - and, as there is no way to import RData files in pure Python, this package also requires a functional
installation of R.

## Getting started
Install the dependences:
  - `R` (a working installation of R is required)
  - `rpy2` (for interfacing with R from Python)
  - `pandas` (for manipulating tabular data)
  
Run the two functions in the package as below:

```python
from importAURN import importAURN, importMetadata

# Download metadata of site IDs, names, locations etc
metadata = importMetadata()

# Download 4 years of data for the Southampton Central site
# (SOUT is the site ID for this site)
# Note: range(2015, 2019) will produce a list of four years: 2015, 2016, 2017 and 2018
data = importAURN("SOUT", range(2015, 2019))
```
