from typing import Union
from dotenv import load_dotenv
import pyodbc # Python interface for ODBC API         https://github.com/mkleehammer/pyodbc
import os
from datetime import datetime
import logging
import platform

def get_read_connection(driver: Union[str, None]=None) -> pyodbc.Connection:
    """Function for getting a connection using the configured read environment.

    Allowed connection protocols include 'ActiveDirectoryIntegrated', 'ActiveDirectoryInteractive', 'ActiveDirectoryMsi' and 'SqlPassword'
    and is controlled by the 'IMBALANCE_LOG_PROTOCOL' environment parameter. Further the 'IMBALANCE_LOG_ASSIGNED_UID' variable is needed
    for user assigned identities

    :param str driver: Configurable driver override, defaults to system determinable

    :returns: Read connection to the imbalance server
    :rtype: pyodbc.Connection
    """
    try:
        load_dotenv(verbose=False, override=True)
    except:
        logging.info('Error in load_dotenv')

    # Extract the database properties
    server=os.environ['IMBALANCE_LOG_SERVER']
    database=os.environ['IMBALANCE_LOG_DATABASE']

    # Define the authentication protocol
    protocol=os.environ.get('IMBALANCE_LOG_PROTOCOL', 'SqlPassword')

    # Allow for driver override
    if driver is None:
        driver='ODBC Driver 17 for SQL Server'
        if platform.system() == 'Windows':
            driver='SQL Server'

    # Set the base connection string
    connection_string = 'DRIVER={' + driver + '};SERVER='+server+';DATABASE='+database

    # Update connection string for username and password if needed
    if protocol not in ['ActiveDirectoryIntegrated', 'ActiveDirectoryInteractive', 'ActiveDirectoryMsi']:
        username=os.environ['IMBALANCE_LOG_READ_USERNAME']
        password=os.environ['IMBALANCE_LOG_READ_PASSWORD']
        connection_string += ';UID=' + username + ';PWD=' + password
    else:
        connection_string += ';Authentication=' + protocol

        # Assign the UID for user assigned identities
        if protocol == 'ActiveDirectoryMsi':
            user_id = os.environ.get('IMBALANCE_LOG_ASSIGNED_UID', None)
            if user_id is not None:
                connection_string += ';UID=' + user_id


    tries=0
    while tries < 5:
        try:
            connection = pyodbc.connect(connection_string)
            break
        except:
            tries = tries + 1
            logging.info('get_connection retry')
    
    return connection

