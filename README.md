# PyFa
Python wrapper on Rfa using [Xarray](https://docs.xarray.dev/en/stable/). The goal of this package is to import FA files into Xarray and provide basic and user friendly commands for visualising FA files.  


## Required software
This package is developed for Linux distributions with a Python3 installation. In addition, R should be installed and the [Rfa](https://gitlab-me.oma.be/aladin/Rfa) (RMI-vpn required), [meteogrid](https://github.com/harphub/meteogrid) libraries as well. 

(This software is available in the modules on the RMI servers).


## Setup
There are two ways to use the PyFa package:
* Use this as a python package to convert FA to Xarray, and make your own analysis
* Use this as backand for shell commands to make some basic visualisations. 


## Installing the python package




## Setup the shell commands
To use this package as a shell command, run the setup_shell_commands.py

```bash
python3 setup_shell_commands.py
```
This file will add the `pyfa` alias to your `~\.bashrc` file, and will propagate arguments to the python package. 


## Usage
The FA file, and some settings are given throug arguments ex.:
```bash
main.py FA_file --print_fields --proj=EPSG:4326 --save
```
or using the shell command:

```bash
pyfa FA_file --print_fields --proj=EPSG:4326 --save
```

To see all possible arguements run `pyfa -h`.



