## Using PyFa on the VSC

On the VSC Tier 1 PyFa is installed in /dodrio/scratch/projects/starting_2022_075/Software/PyFa/.
To use it on the VSC use the following steps.

### First time usage
#### RFA
Add the Rfa library (R) needed to read FA files to your .Renviron File. Every time an R module is loaded, the Rfa package will be available.
```bash
echo R_LIBS=/dodrio/scratch/projects/starting_2022_075/accord/software/R-libs >> ~/.Renviron
```
#### Load environment
Load the correct environments.
```bash
#Load the modules
module load Python/3.10.4-GCCcore-11.3.0 
module load Tkinter/3.10.4-GCCcore-11.3.0
module load GDAL/3.5.0-foss-2022a
module load R/4.2.1-foss-2022a
#Activate the virtual-env for pyfa
source /dodrio/scratch/projects/starting_2022_075/Software/PyFa/pyfa_env/bin/activate
```
#### Add PyFa to your .bashrc
```bash
#Add the pyfa function to your .bash.rc
cd /dodrio/scratch/projects/starting_2022_075/Software/PyFa/PyFa
python
import pyfa_tool as pyfa
pyfa.setup_shell_command()
```

This creates the following in your bash.rc which allows you to use pyfa in the command line interface.
```bash
<<<  PyFa  >>>
PYFA_BASH="/dodrio/scratch/projects/starting_2022_075/Software/PyFa/PyFa/pyfa_tool/bash_executor.sh"
alias pyfa="source ${PYFA_BASH} "$@""

```
> [!WARNING] 
> Restart your session or source your .bashrc before trying out pyfa in the command line!

### Recurring usage
Load the modules and the v-env. After that you are good to go.
```bash
#Load the modules
module load Python/3.10.4-GCCcore-11.3.0 
module load Tkinter/3.10.4-GCCcore-11.3.0
module load GDAL/3.5.0-foss-2022a
module load R/4.2.1-foss-2022a

#Load the v-env
source /dodrio/scratch/projects/starting_2022_075/Software/PyFa/pyfa_env/bin/activate
```

This could be simplified by adding the following into your .bashrc manually.
```bash
function pyfa_env() {
        #Load the modules
		module load Python/3.10.4-GCCcore-11.3.0 
		module load Tkinter/3.10.4-GCCcore-11.3.0
		module load GDAL/3.5.0-foss-2022a
		module load R/4.2.1-foss-2022a

        #Load the v-env
        source /dodrio/scratch/projects/starting_2022_075/Software/PyFa/pyfa_env/bin/activate
}
```
#### Clear the working environment
To completely clear the working environment you will have to purge the modules AND deactivate the v-env. If not loading other modules may interact unexpectedly with the v-env.
```bash
module purge #Unload all the loaded modules
deactivate #Deactivate the venv
```