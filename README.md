# PyFa-tool
Python wrapper on Rfa using [Xarray](https://docs.xarray.dev/en/stable/). The goal of this package is to import FA files into Xarray and provide basic and user friendly commands for inspecting FA files.


## Required software and install

This package is developed for Linux distributions with a Python3 installation. In addition, R should be installed and the [Rfa](https://github.com/harphub/Rfa) library as well.


For the most stable versions use the github main, or use the version on [PyPI](https://pypi.org/project/PyFa-tool/). Install this with:
```bash
pip install PyFa-tool --upgrade
```

## Setup
There are two ways to use the PyFa package:
* Use this as a python package to convert FA to Xarray, and make your own analysis
* Use this as backand for shell commands to make some basic visualisations.

### Python package usage
 To use PyFa as a package, import it and try the available functions:

 ```python
import pyfa_tool as pyfa

fa_file = "/home/....." #FA file path
# Inspection of the FA file without reading the data
FA = pyfa.FaFile(fa_file) #Create an FaFile object

print(FA.get_fieldnames()) #Get dataframe with fieldnames
FA.describe() #print out detailed description

# Read in the data
data = pyfa.FaDataset(fa_file)
#import all available fields
data.import_fa(whitelist=None,
               blacklist=None,
               rm_tmpdir=True,
               reproj=False,
               target_epsg='EPSG:4326')

# Plot
ax = data.plot(variable='CLSTEMPERATURE',
               level=None,
               title=None,
               grid=False,
               land=None,
               coastline=None,
               contour=False,
               contour_levels=10)

# Save
data.save_nc(outputfolder='/home/....',
             filename='netCDF_version_of_FA',
             overwrite=False)

```


### Setup the shell commands
To use this package as a shell command, execute following python code only once:

```python
import pyfa_tool as pyfa
pyfa.setup_shell_command()
```
Restart a terminal, and you are ready to go.
This file will add the `pyfa` alias to your `~\.bashrc` file, and will propagate arguments to the python package.


## Shell Usage
The FA file, and some settings are given throug arguments ex.:
```bash
pyfa FA_file --print_fields --proj=EPSG:4326 --save
```

To see all possible arguements run `pyfa -h`. (Don't forget to setup the shell commands first)


