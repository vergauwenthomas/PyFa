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
 To use PyFa as a package, take a look at these notebook examples:
 * [Demo on the use of the pyfa package](examples/pyfa-python-example.ipynb)
 * [Demo on the use of collections](examples/FaCollection_demo.ipynb)




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
pyfa -d  PFAR07+0001 # --> describe the content of a file
pyfa -c --whitelist=CLSTEMPERATURE,CLSVENT.ZONAL --proj=EPSG:4326 PFAR*+000* # --> convert a FA-file, or a collection of them (by regex) to a netCDF file.
pyfa -p --whitelist=CLSTEMPERATURE --proj=EPSG:4326 PFAR07+0002 vmin=294 cmap='viridis' # --> 2D plot of (reprojected) field with **kwargs passed to the plot.
```
To see all possible arguements run `pyfa -h`. (Don't forget to setup the shell commands first)


