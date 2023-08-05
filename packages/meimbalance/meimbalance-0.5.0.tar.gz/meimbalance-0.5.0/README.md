# python-imbalance

Python helper package for accessing the datalakes and other services for the solution.

Submodule datalake contains the methods for manipulating the various datalakes.


## Develop and build
- CD to the root of the package (platform/meimbalance)

### Test develop
- pip install .

### Build
- Make sure version in setup.py is incremented
- python3 setup.py sdist bdist_wheel

### Upload to PyPi index
- twine upload dist/meimbalance-<version>.tar.gz