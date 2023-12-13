#!/usr/bin/env bash


# To use this add the following line to your .bashrc or profile


#PYFY_BASH="path_of_this_script"
#alias pyfa="source ${PYFY_BASH} "$@""

# This script will format and pass the argumenst, comming from an alias-bash-call to the python script.



## ----------------------- Create PyFA path

PYFA_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
main="${PYFA_DIR}/main.py"

## ---------------------- PASS ARGUMENTS ------------------
python ${main} "$@"
