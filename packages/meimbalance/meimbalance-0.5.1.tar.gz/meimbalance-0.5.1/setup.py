from setuptools import setup, find_packages

VERSION = '0.5.1'
DESCRIPTION = 'A helper package for the Imbalance project'
LONG_DESCRIPTION = 'Contains methods to connect to the datalakes and handle files.  Also functions to log to a sql log database'

setup(
    name='meimbalance',
    version=VERSION,
    author='Håkon Klausen',
    author_email='hakon.klausen@ae.no',
    packages=find_packages(),
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    install_requires=[
        "azure-datalake-store",
        "azure-identity",
        "azure-storage-file-datalake",
        "pandas",
        "pyodbc",
        "python-dotenv",
		"requests",
		"sendgrid"
    ]
)