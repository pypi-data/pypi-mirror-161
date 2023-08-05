# Helper class for the Imbalance project
#
# Class Datalakes - initiate by 
#   import datalake from meimbalance
#   datalakes = datalake.Datalakes()
#
# Will do the following when included:
#   - Load environment variables
#   - Get Azure credentials
#   - Define instances for the datalakes
#
import os
import tempfile
from azure.identity._credentials.managed_identity import ManagedIdentityCredential
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient
from azure.datalake.store import core, lib, multithread
from pathlib import Path
import logging
import pandas as pd
from urllib.parse import urlparse

# Function to split a datalake URL on the form 
#   https://aezsharedlakeprd01.blob.core.windows.net/root/stage0/meteorology/forecast/weather/ecmwf/grib-new/main/2021/A2D02211200022209001 
# into separate directory and filename variables
def split_datalake_url(datalake_url):
    # Parsing the URL
    parsed_url = urlparse(datalake_url)
    # Directory and file is in the PATH of the url
    datalake_path = parsed_url.path.rstrip('/')
    # Splitting on the last /
    split_path = datalake_path.rsplit('/',1)
    directory_with_root=split_path[0]
    directory = directory_with_root.split('/', 2)[2]
    filename=split_path[1]
    return directory, filename

# Superclass for both generations of Datalakes
class Datalake:
    def __init__(self, datalake_name):
        self.datalake_name = datalake_name
    

# Class to handle Gen2 Datalakes
class DatalakeGen2(Datalake):
    def __init__(self,datalake_name, azure_credential, copy_instance=False):
            self.datalake_name = datalake_name
            self.azure_credential = azure_credential
            self.container_name = 'root'
            # Add code to cache service client
            super().__init__(datalake_name)
            self.__service_client = self.__get_service_client()
            # Add code to cache file system client
            self.__file_system_client = self.__get_file_system_client()

            # Check if this is a datalake instance of the imbalance store running in prod
            self.running_in_prod = False
            self.copy_to_dev = False

            if (self.datalake_name == 'aezstoimbalanceprdstore') and (copy_instance == False):
                self.running_in_prod = True
                try:
                    self.imbalance_datalake_name_dev=os.environ['IMBALANCE_DATALAKE_NAME_DEV']
                except:
                    message = 'ERROR: Missing environment variable IMBALANCE_DATALAKE_NAME_DEV'

                    # Print for backwards compatibility
                    print(message)

                    raise EnvironmentError(message)
                
                # Check for copy-to-dev
                try:
                    
                    if os.environ['COPY_TO_DEV'] == 'True':
                        self.copy_to_dev = True
                except:
                    # Ignore missing COPY_TO_DEV variable, assert False
                    pass
            
            # Initiate a new instance of the DatalakeGen2 class to handle Dev connections
            if self.copy_to_dev == True:
                self.imbalance_datalake_dev = DatalakeGen2(self.imbalance_datalake_name_dev, self.azure_credential, copy_instance=True)

            # And then the mirror feature: Check if this is the imbalance store running in dev
            self.running_in_dev = False
            self.copy_to_prod = False

            if (self.datalake_name == 'aezstoimbalancedevstore') and (copy_instance == False):
                self.running_in_dev = True
                try:
                    self.imbalance_datalake_name_prod=os.environ['IMBALANCE_DATALAKE_NAME_PROD']
                except:
                    message = 'ERROR: Missing environment variable IMBALANCE_DATALAKE_NAME_PROD'

                    # Print for backwards compatibility
                    print(message)

                    raise EnvironmentError(message)
                
                # Check for copy-to-prod
                try:
                    if os.environ['COPY_TO_PROD'] == 'True':
                        self.copy_to_prod = True
                except:
                    # Ignore missing COPY_TO_PROD variable, assert False
                    pass
            
            # Initiate a new instance of the DatalakeGen2 class to handle Dev connections
            if self.copy_to_prod == True:
                self.imbalance_datalake_prod = DatalakeGen2(self.imbalance_datalake_name_prod, self.azure_credential, copy_instance=True)


    # Get a service client
    def __get_service_client(self):
        service_client = DataLakeServiceClient(account_url="{}://{}.dfs.core.windows.net".format(
            "https", self.datalake_name), credential=self.azure_credential)
        return service_client

    # Get a file system client for the given root
    def __get_file_system_client(self):
        # service_client = self.__get_service_client()
        file_system_client = self.__service_client.get_file_system_client(file_system=self.container_name)
        return file_system_client

    # Get a directory client for the given directory_name
    def __get_directory_client(self, directory_name):
        file_system_client = self.__file_system_client
        try:
            directory_client = file_system_client.get_directory_client(directory=directory_name)
        except Exception as e:
            print('Error in getting directory client for ', directory_name, ': ', e)
            return None

        return directory_client

    # Get a file client for the given directory and file name
    def __get_file_client(self, directory_name, filename):
        directory_client = self.__get_directory_client(directory_name)
        file_client = directory_client.get_file_client(filename)
        return file_client

    # Helper function to download a file
    def __download_file(self, directory_name, filename, file):
        file_client = self.__get_file_client(directory_name, filename)
        download = file_client.download_file()
        downloaded_bytes = download.readall()
        file.write(downloaded_bytes)
        file.seek(0,0)
        return

    # Helper function to check if a file exists
    def __check_if_file_exists(self, directory_name, filename):
        if directory_name == '/':
            file_path = filename
        else:
            file_path = directory_name[1:] + '/' + filename
        file_system_client = self.__file_system_client
        try:
            paths = file_system_client.get_paths(path=directory_name, recursive=False)
            for path in paths:
                if file_path == path.name:
                    return True

        except:
            # If we cant find the path, then just return False
            return False 

        return False

    # List content of a directory
    def list_files_in_directory(self, directory_name):
        file_system_client = self.__file_system_client
        files = []
        paths = file_system_client.get_paths(path=directory_name, recursive=False)
        for path in paths:
            directory_name, filename = os.path.split(path.name)
            files.append(filename)
        return files

    # Get newest file in directory
    def get_latest_file_in_directory(self, directory_name):
        files_df = self.list_files_attributes_in_directory(directory_name=directory_name)
        count = len(files_df)
        if count == 0:
            return None

        files_df.sort_values(by=['last_modified','filename'],ascending=False, inplace=True)
        file_df = files_df[['filename']].head(1)
        filename = file_df.iloc[0]['filename']
        return filename

    # Get Dataframe with directory listing
    def list_files_attributes_in_directory(self, directory_name):
        file_system_client = self.__file_system_client
        names = []
        etags = []
        deleteds = []
        metadatas = []
        last_modifieds = []
        creation_times = []
        sizes = []

        paths = file_system_client.get_paths(path=directory_name, recursive=False)
        count = 0
        for path in paths:
            directory_name, filename = os.path.split(path.name)
            file_client = self.__get_file_client(directory_name, filename)
            properties = file_client.get_file_properties()
            if  not(('hdi_isfolder') in properties.metadata and properties.metadata['hdi_isfolder'] == 'true'):
                count = count + 1
                names.append(filename)
                etags.append(properties.etag)
                deleteds.append(properties.deleted)
                metadatas.append(properties.metadata)
                last_modifieds.append(properties.last_modified)
                creation_times.append(properties.creation_time)
                sizes.append(properties.size)

        data = {'filename':names, 'etag': etags, 'deleted': deleteds, 'metadata': metadatas, 'last_modified': last_modifieds, 'creation_time': creation_times, 'size': sizes}
        dataframe = pd.DataFrame(data=data)
        return dataframe


    # Download a file from the datalake, write it to a local temporary file, and open the file for processing
    def open_file(self, directory_name, filename): 
        localfile=tempfile.TemporaryFile()
        self.__download_file(directory_name, filename, localfile)
        localfile.seek(0,0)
        return localfile

    # Download a file from the datalake, write it to a local temporary file, and open the file for processing
    def open_text_file(self, directory_name, filename): 
        file_client = self.__get_file_client(directory_name, filename)
        download = file_client.download_file()
        downloaded_bytes = download.readall()
        downloaded_text = downloaded_bytes.decode("utf-8")
        localfile=tempfile.TemporaryFile(mode='a+t')
        localfile.writelines(downloaded_text)
        localfile.seek(0,0)
        return localfile

    # Upload a local file to a new file in the Datalake
    def upload_file(self, file, directory_name, filename, overwrite=False):
        file.seek(0,0)
        file_contents = file.read()
        directory_client = self.__get_directory_client(directory_name)
        
        # Check if file already exist in the lake if Owerwrite is False
        if overwrite == False:
            if self.__check_if_file_exists(directory_name=directory_name, filename=filename):
                logging.error('File ' + filename + ' already exists in directory ' + directory_name)
                return

        directory_client.create_file(file=filename)
        file_client = directory_client.get_file_client(filename)
        file_client.append_data(data=file_contents, offset=0, length=len(file_contents))
        file_client.flush_data(len(file_contents))

        # If copy-to-dev is set, then upload to dev also
        if self.copy_to_dev == True:
            self.imbalance_datalake_dev.upload_file(file, directory_name, filename, overwrite=True)
        
        # If copy-to-prod is set, then upload to prod also
        if self.copy_to_prod == True:
            self.imbalance_datalake_prod.upload_file(file, directory_name, filename, overwrite=True)

    # Upload a local named file to the datalake
    def upload_local_file(self, local_filepath, directory_name, filename, overwrite=False):
        file=open(local_filepath,"rb")
        self.upload_file(file, directory_name, filename, overwrite=overwrite)
        file.close()

        # Download a file to a local filesystem
    def download_to_local_file(self, directory_name, filename, local_filepath):
        file=open(local_filepath, "wb")
        self.__download_file(directory_name, filename, file)
        file.close()
        pass    

    

# Class to handle Gen1 Datalakes
class DatalakeGen1(Datalake):
    def __init__(self,datalake_name, token):
        self.token = token
        super().__init__(datalake_name)

    # Helper function to download a file from the datalake
    def __download_file(self, directory_name, filename, file):
        filepath=directory_name+filename
        adlFileSystem = core.AzureDLFileSystem(self.token, store_name=self.datalake_name)
        with adlFileSystem.open(filepath, 'rb') as f:
            downloaded_bytes = f.read()
            file.write(downloaded_bytes)
            file.seek(0,0)
    
    # Download a file from the datalake, write it to a local temporary file, and open the file for processing
    def open_file(self, directory_name, filename):
        localfile=tempfile.TemporaryFile()
        self.__download_file(directory_name=directory_name, filename=filename, file=localfile)
        return localfile

    # Download a file to a local filesystem
    def download_to_local_file(self, directory_name, filename, local_filepath):
        file=open(local_filepath, "w")
        self.__download_file(directory_name, filename, file)
        file.close()
        pass  


    # Old code
    def old_open_file(self, directory_name, filename):
        filepath=directory_name+filename

        adlFileSystem = core.AzureDLFileSystem(self.token, store_name=self.datalake_name)
        with adlFileSystem.open(filepath, 'rb') as f:
            downloaded_bytes = f.read()
            localfile=tempfile.TemporaryFile()
            localfile.write(downloaded_bytes)
            localfile.seek(0,0)
            return localfile


# Helper class to initialize instances for the 3 datalakes in use in the project and 
# get Azure Credentials and token
class ImbalanceDatalakes:
    def __init__(self, exclude_managed_identity_credential: bool = True):
        """Helper class to initialize instances for the 3 datalakes in use in the project and 
        get Azure Credentials and token.

        :param bool exclude_managed_identity_credential: Whether to exclude managed identity for data lake access, Defaults to True for backwards compatibility purposes.
        """
        self.__check_for_multiple_env()
        # Try to update the environment from dotenv.
        try:
            load_dotenv(verbose=False, override=True)
        except:
            logging.info('Error in load_dotenv')

        try:
            self.imbalance_datalake_name=os.environ['IMBALANCE_DATALAKE_NAME']
            self.shared_datalake_gen2_name=os.environ['SHARED_DATALAKE_GEN2_NAME']
            self.shared_datalake_gen1_name=os.environ['SHARED_DATALAKE_GEN1_NAME']
            self.azure_tenant_id=os.environ['AZURE_TENANT_ID']
            self.azure_client_id=os.environ['AZURE_CLIENT_ID']
            self.azure_client_secret=os.environ['AZURE_CLIENT_SECRET']
        except:
            # Construct the error message
            message_components = [
                'ERROR: Missing environment variables, need to declare IMBALANCE_DATALAKE_NAME, SHARED_DATALAKE_GEN2_NAME and SHARED_DATALAKE_GEN1_NAME',
                'Hint: Put these variables in the .env file in the project root, and create a source statement in ~/.bashrc:',
                'if [ -f ~/source/Imbalance/.env ]; then',
                '    source ~/source/Imbalance/.env',
                'fi'
            ]
            message = os.linesep.join(message_components)

            # For backwards compsatibility in stdout dependent processes
            print(message)

            # Raise error for incomplete environment
            raise EnvironmentError(message)
            
        self.azure_credential = DefaultAzureCredential(exclude_managed_identity_credential = exclude_managed_identity_credential)

        token = lib.auth(tenant_id = self.azure_tenant_id, client_id = self.azure_client_id, client_secret = self.azure_client_secret)

        self.imbalance_datalake = DatalakeGen2(self.imbalance_datalake_name, self.azure_credential)
        self.shared_datalake_gen2 = DatalakeGen2(self.shared_datalake_gen2_name, self.azure_credential)
        self.shared_datalake_gen1 = DatalakeGen1(self.shared_datalake_gen1_name, token)


    def __check_for_multiple_env(self):
        results = self.__find_all__(name='.env', path=str(Path.home()))
        if len(results) > 1:
            print('Warning: Multiple .env found: ' + str(len(results)))
            for result in results:
                print('  ' + result)


    def __find_all__(self, name, path):
        result = []
        for root, dirs, files in os.walk(path):
            if name in files:
                if 'pythonFiles' not in root:
                    result.append(os.path.join(root, name))
        return result

class ImbalanceDatalakesMsi(ImbalanceDatalakes):

    def __init__(self):
        """Helper subclass to initialize instances for the 3 datalakes in use in the project and 
        get Azure Credentials and token. This class does not disable managed identity from the credentials
        """
        super().__init__(exclude_managed_identity_credential=False)