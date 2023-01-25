#!/bin/sh

#1 execute tests before building the package


#Use poetry to make dependencies (https://python-poetry.org/docs/basic-usage/)
export PATH="/home/thoverga/.local/bin:${PATH}" #for poetry
poetry add pandas
poetry add numpy
poetry add matplotlib
poetry add geopandas
poetry add xarray
poetry add rioxarray


#2 Build the package




echo "Removing old builds before building the package ..."

cd dist
rm *.whl
rm *.tar.gz
cd ..

echo "Make build ..."
python3 -m build

#3 Uploading to testPyPi
echo "Uploading to testPyPI ..."
python3 -m twine upload --verbose -u __token__ -p pypi-AgENdGVzdC5weXBpLm9yZwIkYmZlYzVmMTEtNzdhMy00N2I2LTgxNmEtNzYxNDljMGU2NjgyAAIqWzMsImZhNTY0NjMwLWQ4MjMtNDU0Zi1hMzU4LThmODFkM2JjNWNhMSJdAAAGIFbiJUx3A4A_m8uc47yrtqceaFr7erEI-RFpxTd-Qk4e --repository testpypi dist/*


#4  updateing the package on this computer
#echo "Uninstalling curren vlinder_toolkit package"
#yes | python3 -m pip uninstall vlinder_toolkit
#rm -rf /home/thoverga/anaconda3/lib/python3.8/site-packages/vlinder_toolkit*


#echo "Installing the package from testPyPI ..."
#pip3 install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple vlinder_toolkit --upgrade
#adding the extra-index-url makes shure that dependencies can by found on PiPY (an not limited to testPiPY)


#5 show info
#echo "Installed package information: "
#pip3 show vlinder_toolkit



#6 test import
#yes | conda create --name test_pypi python=3.7
#conda activate test_pypi

#pip3 install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple vlinder_toolkit --upgrade
#pip3 show vlinder_toolkit
#python3 tests/package_import_test.py


#deactivate
#conda deactivate
