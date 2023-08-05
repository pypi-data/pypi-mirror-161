# This is ready for writing "connectors" to various external data "sources" (e.g. AWS S3, Postgres DB, etc.)
import os
import fnmatch
import tempfile
import datetime
from typing import Optional
# Strategy: Use a class structure to enforce new connectors having the same key functions

# Note: TYPE is a reserved keyword in the parameters for each source
# This static generator will create any type of connector -- need to add new types to this method
def _GetConnector(parameters):
    if 'TYPE' in parameters:
        type_lower = parameters['TYPE'].lower()
    elif 'type' in parameters:
        type_lower = parameters['type'].lower()
    else:
        print("ERROR: Cannot create Connector with parameters {} since TYPE is not defined".format(parameters))
        return None
    
    if type_lower=='s3':
        #print("Created S3 connector...")
        return S3_Connector(parameters)
    elif type_lower=='postgres' or type_lower=='postgresql' or type_lower=='redshift':
        #print("Created Postgres/Redshift connector...")
        return Postgres_Connector(parameters)
    elif type_lower=='sql' or type_lower=='mssql':
        #print("Created Microsoft SQL connector...")
        return SQL_Connector(parameters)
    elif type_lower=='sftp' or type_lower=='ftp':
        #print("Created SFTP connector...")
        return SFTP_Connector(parameters)
    elif type_lower=='sharepoint':
        #print("Created Sharepoint connector...")
        return Sharepoint_Connector(parameters)
    
def _DecryptFile(filepath, decryption_key):
    return

# Utility function to decrypt data given a decryption key/passphrase
# decryption_key can either be a string (for the local path to the key) or a dict with {'path':[local filepath], 'passphrase':[some passphrase]}
def _EncryptDecryptData(data, decryption_key, encrypt_or_decrypt='decrypt'):
    # If there's a decryption key, use it here
    decrypted_file = None
    if decryption_key is not None:
        decryption_key_filepath = None
        if isinstance(decryption_key, str):
            # By default the passphrase is blank
            decryption_key_filepath = decryption_key
            decryption_key_passphrase = ''
        elif isinstance(decryption_key, dict):
            # Look for 'path' and 'passphrase'
            decryption_key_filepath = decryption_key.get('path', None)
            decryption_key_passphrase = decryption_key.get('passphrase', '')

        if decryption_key_filepath is not None:
            # Check that the key file exists
            if not os.path.exists(decryption_key_filepath) or not os.path.isfile(decryption_key_filepath):
                print("ERROR: Cannot find encryption/decryption key at the given path: {}".format(decryption_key_filepath))
                raise

            # Use the given (local) decryption key to decrypt the local TEMP file
            import pgpy
            key,_ = pgpy.PGPKey.from_file(decryption_key_filepath)
            emsg = pgpy.PGPMessage.from_blob(data) #from_file(local_filepath)
            with key.unlock(passphrase=decryption_key_passphrase):
                if encrypt_or_decrypt == 'decrypt':
                    # Decrypt
                    decrypted_bytesarray = (key.decrypt(emsg).message)
                else:
                    # Encrypt
                    decrypted_bytesarray = key.encrypt(emsg).message
                print(type(decrypted_bytesarray))
                return decrypted_bytesarray

    return None
    
##############################
### Parent Connector class ###
class Connector:
    parameters = None
    connection = None
    
    def __init__(self, parameters, required=None):
        self.parameters = parameters
        
        # If provided a list of required parameters, then confirm that each one is defined
        if required is not None:
            for param in required:
                if param not in parameters:
                    print("ERROR: Required parameter {} has not been defined for this connector of type {}".format(param, 
                                                                                                                   type(self)))
                    raise
        
    def connect(self):
        return
    
    def read(self, path, type=None):
        return
    
    def write(self, data, destination):
        return
    

    
#######################################
### Amazon AWS S3 Bucket connnector ###
class S3_Connector(Connector):
    required_params = []
    DEFAULT_REGION = 'us-east-1'
    
    def __init__(self, parameters):
        Connector.__init__(self, parameters, required=self.required_params)
        self.type = 's3'
        self.bucket = None
        self.session = None
        self.client = None
     
    def _s3_list_all_files(self, prefix):
        paginator = self.client.get_paginator("list_objects")

        bucket_name = self.parameters['BUCKET']
        page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        keys = []
        for page in page_iterator:
            if "Contents" in page:
                for key in page["Contents"]:
                    keyString = key["Key"]
                    keys.append(keyString)

        return keys if keys else []
        
    def connect(self, type='connection'):
        from boto.s3.connection import S3Connection
        from botocore.client import Config
        import boto3
        super().connect()

        config = Config(connect_timeout=5, retries={'max_attempts': 3})
        #s3 = boto3.client('s3', config=config)

        if self.parameters is not None:
            print("Connecting to AWS S3 Bucket:", self.parameters['BUCKET'])
            # Default is to create a connection and a bucket object
            self.connection = S3Connection(self.parameters['AWS_KEY'], self.parameters['AWS_SECRET'])
            self.bucket = self.connection.get_bucket(self.parameters['BUCKET'])
            print("...created connection to bucket")
            
            if type=='client':
                # Can create a client and session
                self.client = boto3.client('s3', 
                      aws_access_key_id=self.parameters['AWS_KEY'], 
                      aws_secret_access_key=self.parameters['AWS_SECRET'],
                      region_name=self.parameters.get('REGION', self.DEFAULT_REGION),
                      config=config
                )
                print("...created client")
            elif type=='session':
                self.session = boto3.Session(
                    aws_access_key_id=self.parameters['AWS_KEY'],
                    aws_secret_access_key=self.parameters['AWS_SECRET'],
                    region_name=self.parameters.get('REGION', self.DEFAULT_REGION),
                    config=config  # Need to confirm this is okay parameter to pass here
                )
                self.resource = self.session.resource('s3')
                print("...created session and resource")
        
    # type='list' if you want to read a list of the files in a given location (as the path)
    # decryption_key in kwargs supported for 'head' and '' type read(), not yet for 'download'
    def read(self, path, type=None, to_file=None, encoding='utf-8', **kwargs):
        super().read(path, type=type)

        # Check for a decryption_key in the keyword args
        decryption_key = kwargs.get('decryption_key', None)
        
        if type=='list':
            self.connect(type='client')
            if self.bucket is not None:
                prefix_len = len(path)
                full_s3_file_list = self._s3_list_all_files(path)
                print("...found {} files to list".format(len(full_s3_file_list)))
                s3_files = [fkey[prefix_len:] for fkey in full_s3_file_list]
                #s3_files = [fkey.key[prefix_len:] for fkey in self.bucket.list(prefix=path)]
                return s3_files

        elif type=='download':
            self.connect(type='client')
            if self.client is not None:
                if to_file is not None:
                    print("...downloading file from S3 client in path '{}' to local file '{}'".format(path, to_file))
                    self.client.download_file(self.parameters['BUCKET'], path, to_file)
                    print("...done")
                else:
                    print("ERROR: Need to pass to_file parameter when using type='download' in an S3 connector") 
                    
        elif len(type)>=4 and type[:4]=='head':
            self.connect(type='client')
            print("type:", type)
            # Get the # of lines from the 'type' parameter if it's like type='head:10'
            if ':' in type:
                type_split = type.split(':')
                num_rows = int(type_split[1])
            else:
                # Default is 5 rows
                num_rows = 5
                
            if self.client is not None:
                s3_response_object = self.client.get_object(Bucket=self.parameters['BUCKET'], 
                                                            Key=path)
                object_content = s3_response_object['Body']
                
                if decryption_key is not None:
                    # If a decryption key is passed, decrypt the contents of this file before returning it
                    # Note: This will stream the entire contents of the file from S3 beforehand
                    print("Decrypting file '{}' using key: {}...".format(path, decryption_key))
                    object_content_stream = _EncryptDecryptData(object_content.read(), decryption_key, 
                                                                encrypt_or_decrypt='decrypt')
                    print("...done.")
                    
                    object_content_lines = None
                    if isinstance(object_content_stream, bytearray):
                        # Need to split bytearray into lines
                        object_content_lines = object_content_stream.split(b'\n')
                    elif isinstance(object_content_stream, str):
                        object_content_lines = object_content_stream.split('\n')
                    
                    if object_content_lines is not None:
                        all_lines = ''
                        for i in range(num_rows):
                            line = object_content_lines[i]
                            all_lines += line.decode(encoding)
                        return all_lines 
                    else:
                        print("WARNING: Decrypted data has an unknown type, cannot split into lines. Returning entire file.")
                        return object_content_stream
                else:
                    # If the file is not encrypted, then just read line by line from the Boto S3 stream
                    all_lines = ''
                    for i in range(num_rows):
                        line = object_content._raw_stream.readline()
                        all_lines += line.decode(encoding)
                    return all_lines            

        elif type=='exists':
            import boto3
            from botocore.errorfactory import ClientError
            self.connect(type='client')
            try:
                self.client.head_object(Bucket=self.parameters['BUCKET'], Key=path)
                return True
            except ClientError:
                return False
                # Not found
                pass

        else:
            # Default is to return the file itself
            self.connect(type='client')
            s3_response_object = self.client.get_object(Bucket=self.parameters['BUCKET'], 
                                                        Key=path)
            object_content = s3_response_object['Body'].read()
            
            # If a decryption key is passed, decrypt the contents of this file before returning it
            if decryption_key is not None:
                return _EncryptDecryptData(object_content, decryption_key, 
                                           encrypt_or_decrypt='decrypt')
            
            return object_content
        
        return None
        
    # Need to explicitly set is_folder=True if just want to create a folder at this destination (and will ignore data)
    def write(self, data, destination, local_filename=None, overwrite=False, is_folder=False, suppress_overwrite_error=False):
        from boto.s3.key import Key
        super().write(data, destination)
        
        # make sure we have a bucket -- otherwise call connect() to initialize the connection
        if self.bucket is None:
            self.connect()
            assert self.bucket is not None, f'S3_Connector self.bucket is still None even after connecting'
        k = Key(self.bucket)
        k.key = destination
        
        if is_folder:
            # note: this isn't really needed (can create S3 files without empty files for folders), but ok to do
            # Then just create the stub folder "key" in S3
            # first check to make sure you're not overwriting unexpectedly
            if k.exists():
                if overwrite:
                    print(f'{destination} exists, will overwrite with empty file for folder')
                else:
                    # check if size 0 -- no problem if so
                    k.open_read()
                    if k.size != 0:
                        if suppress_overwrite_error:
                            print(f'{destination} exists on S3 (size {k.size}), will not overwrite')
                            return
                        else:
                            raise FileExistsError(f'{destination} exists on S3 (size {k.size}), will not overwrite')
            print("Creating folder in the S3 bucket: '{}'".format(destination))
#             k = self.bucket.new_key(destination)
            k.set_contents_from_string('')
            
        else:
            # LS note: for now, we want to throw an error to make sure we convert to using local_filename everywhere
            if local_filename is None:
                raise NotImplementedError("Must specify local_filename for S3_Connector.write()")

            # check if file already exists
            print(f"Checking if destination S3 file {destination} already exists")
            if k.exists():
                # found the file, should not continue unless it's ok to overwrite
                if overwrite:
                    print("Will overwrite existing S3 file")
                else:
                    if suppress_overwrite_error:
                        print("Will not overwrite existing S3 file")
                        return
                    else:
                        raise FileExistsError("File exists on S3, will not overwrite")
            else:
                print("S3 file not found, ok to proceed")
            # Otherwise push the data/file into a file at the given destination
            if local_filename is not None:
                print("Writing local file '{}' to S3 at '{}'".format(local_filename, destination))
                k.set_contents_from_filename(local_filename)
            # TODO: uncomment below when removing the NotImplementedError above
#             else:
#                 if data is None:
#                     print('Did not pass in data, will just create an empty file')
#                     data = ''
#                 expected_size = len(data.encode()) if data is not None else None
#                 print("Writing passed in data of size={} to S3 at '{}'".format(expected_size, destination))
#                 k.set_contents_from_string(data)
        print('...done')


        
############################################
### PostgreSQL or Redshift DB connnector ###
class Postgres_Connector(Connector):
    
    required_params = ['user', 'password', 'db', 'host']
    default_timeout_secs = 5
    max_retries = 5
        
    def __init__(self, parameters):
        Connector.__init__(self, parameters, required=self.required_params)
        self.type = 'postgres'
        self.cursor = None
        
    def connect(self):
        import psycopg2
        super().connect()
        
        if self.parameters is not None:
            print("Connecting to Postgres/Redshift DB:", self.parameters['db'], "at host:", self.parameters['host'])

            ### Make a connection or re-try if the previous attempt failed
            is_connected = False
            num_tries = 0
            while not is_connected and num_tries < self.max_retries:
                is_connected = self._try_connect()
                num_tries += 1
            
            ### Check if any of the tries succeeded
            if not is_connected:
                print("Could not connect to the SFTP server using SSH after {} retries".format(self.max_retries))
                return
            
            if self.connection is not None:
                print("...connected.") 
        else:
            print("WARNING: Do not have parameters to connect to the DB.")
    
    def _try_connect(self):
        import psycopg2
        try:
            conn_string = "dbname='{}' port='{}' user='{}' password='{}' host={}".format(self.parameters['db'], 
                                                                                         self.parameters.get('port', None), 
                                                                                         self.parameters['user'], 
                                                                                         self.parameters['password'], 
                                                                                         self.parameters['host'])
            self.connection = psycopg2.connect(conn_string, connect_timeout=self.default_timeout_secs)
            self.cursor = self.connection.cursor()
            return True
        except:
            print("...timeout reached during psycopg2.connect")
            return False
        
    def read(self, path, type=None):
        super().read(path, type=type)

        import pandas as pd
        
        self.connect()
        
        # Query for the data to get all the columns
        if type=='select' and isinstance(path, str) and path[:6]=='SELECT':
            query = path
            query_df = pd.read_sql_query(query, con=self.connection)
            return query_df
            
        elif type=='columns':
            table = path
            query = f"SELECT * from {table} LIMIT 1;"
            print("Running query to get columns:", query)
            query_result = self.cursor.execute(query)
            print("...done:", datetime.datetime.now())
            query_df = pd.read_sql_query(query, con=self.connection)
            if query_df is not None:
                print("Columns:", query_df.columns)
                return query_df.columns
                
        return None
        
        
    def write(self, data, destination):
        super().write(data, destination)
        # TODO: Fill this in for postgres
        
############################################
### SQL connnector ###
class SQL_Connector(Connector):
    
    required_params = ['user', 'password', 'db', 'server', 'port', 'driver']
    default_timeout_secs = 5
    max_retries = 5
        
    def __init__(self, parameters):
        Connector.__init__(self, parameters, required=self.required_params)
        self.type = 'sql'
        self.cursor = None
        print("creating SQL_Connector")
      
        
    def connect(self):
        import pyodbc
        super().connect()
        
        if self.parameters is not None:
            print("Connecting to SQL DB:", self.parameters['db'], "at server:", self.parameters['server'])

            ### Make a connection or re-try if the previous attempt failed
            is_connected = False
            num_tries = 0
            while not is_connected and num_tries < self.max_retries:
                is_connected = self._try_connect()
                num_tries += 1
            
            ### Check if any of the tries succeeded
            if not is_connected:
                print("Could not connect to the SQL server after {} retries".format(self.max_retries))
                return
            
            if self.connection is not None:
                print("...connected.") 
                
        else:
            print("WARNING: Do not have parameters to connect to the DB.")
    
    # Note: Need to pre-instll the ODBC driver for Linux/Windows correctly first
    # See here: https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15
    def _try_connect(self, encrypt=True):
        import pyodbc
        import sys

        try:
            conn_string = "DRIVER={};SERVER={};PORT={};DATABASE={};UID={};PWD={};ENCRYPT={};TrustServerCertificate={};Connection Timeout=15;".format(self.parameters['driver'], self.parameters['server'], self.parameters['port'], self.parameters['db'], self.parameters['user'], self.parameters['password'], 'yes' if encrypt else 'no', 'no' if encrypt else 'yes')
            self.connection = pyodbc.connect(conn_string)
            print("...connection succeeded.")
            self.cursor = self.connection.cursor()
                        
            # Set default parameters for this connection
            self.cursor.fast_executemany = True
            self.connection.autocommit = False
            return True
        except:
            print("...timeout reached during SQL pyodbc connect")
            print("...error:", sys.exc_info())
            print("...connection string:", conn_string)
            return False
        
    def read(self, path, type='select'):
        super().read(path, type=type)
        import pandas as pd
        
        self.connect()
        
        # Query for the data to get all the columns
        if type=='select' and isinstance(path, str) and path[:6]=='SELECT':
            query = path
            query_df = pd.read_sql_query(query, con=self.connection)
            return query_df
            
        elif type=='columns':
            table = path
            query = f"SELECT TOP 1 * from {table};"
            print("Running query to get columns:", query)
            query_result = self.cursor.execute(query)
            print("...done:", datetime.datetime.now())
            if query_result.description is not None:
                # If this is a SELECT query --> get the results into a pandas dataframe
                query_result_columns = [column[0] for column in query_result.description]
                print("Columns:", query_result_columns)
                return query_result_columns
            
        elif type=='rows':
            table = path
            query = f"SELECT count(*) as num_rows from {table};"
            print("Running query to get # rows:", query)
            num_rows_df = pd.read_sql_query(query, con=self.connection)
            return num_rows_df.loc[0,'num_rows']
                
        return None
#                 # Try to auto-detect whether this was a SELECT query or an INSERT/UPDATE query
#                 # TODO: This might not work for other SQL databases not using pyodbc --> should push this into connectors
#                 if connector.type=='postgres':
#                     data_query = f"SELECT * from {to_database_table} LIMIT 1;"
#                 else:
#                     data_query = f"SELECT TOP 1 * from {to_database_table};"
#                 print(data_query)
#                 database_df = pd.read_sql_query(data_query, con=connector.connection)
        
        
    def write(self, data, destination):
        super().write(data, destination)
        
        # Reconnect first
        self.connect()
        
        try:
            # Detect what type of INSERT/UPDATE query this is
            if data is not None:
                # Have data to insert
                if isinstance(destination, str) and destination[:6].upper()=="INSERT":
                    # This is an INSERT query using a list of values in data
                    query = destination
                    print("Going to execute: ", query)
                    self.cursor.executemany(query, data)
                    print("...done:", datetime.datetime.now())
                    self.connection.commit()
                    print("...committed.")
            else:
                # No data to insert, just run a query
                if isinstance(destination, str) and (destination[:6].upper() in ['INSERT', 'UPDATE'] \
                                                     or destination[:8].upper() in ['TRUNCATE']):
                    # Just run the given INSERT/UPDATE query
                    query = destination
                    print("Going to execute: ", query)
                    self.cursor.execute(query)
                    print("...done:", datetime.datetime.now())
                    self.connection.commit()
                    print("...committed.")
                else:
                    print("Cannot run query in 'to' parameters since it's not an INSERT, UPDATE, or TRUNCATE query:", destination)
                    
        except Exception as e:
            # If error thrown, raise it
            print(e)
            print(data[:5])
            self.connection.commit()
            raise
                
            
    def truncate(self, db_table):
        # Truncate the table
        self.connect()
        print("...connected")
        cursor = self.connection.cursor()
        print("...have cursor")
        query = "TRUNCATE TABLE {};".format(db_table)
        print(query)
        cursor.execute(query)
        print("...executed")
        self.connection.commit()
        print("Truncated DB table", db_table)


    
#######################
### SFTP connnector ###
class SFTP_Connector(Connector):
    
    required_params = ['key_path', 'key_password', 'username', 'host_ip', 'host_port']
    ssh = None
    default_timeout_secs = 5
    max_retries = 5
    
    def __init__(self, parameters):
        Connector.__init__(self, parameters, required=self.required_params)
        self.type = 'sftp'
        self.cursor = None
        self.ssh = None
    
    def connect(self):
        import sys
        import paramiko
        super().connect()

        if self.parameters is not None:
            print("Connecting to SFTP:", self.parameters['username'], "at host:", self.parameters['host_ip'])

            ### creating RSAKey object
            key=paramiko.RSAKey.from_private_key_file(self.parameters['key_path'], 
                                                      password=self.parameters['key_password'])

            ### Create ssh client
            self.ssh=paramiko.SSHClient()

            ### Automatically add the host to varified host file
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            ### Make a connection or re-try if the previous attempt failed
            is_connected = False
            num_tries = 0
            while not is_connected and num_tries < self.max_retries:
                is_connected = self._try_connect(key=key)
                num_tries += 1
                
            ### Check if any of the tries succeeded
            if not is_connected:
                print("Could not connect to the SFTP server using SSH after {} retries".format(self.max_retries))
                return
                

            ### Create SFTP connection
            sftp = self.ssh.open_sftp()
            sftp.sshclient = self.ssh
            self.connection = sftp
            if self.connection is not None:
                print("...connected.") 
        else:
            print("WARNING: Do not have parameters to connect to the SFTP site.")
            
    def _try_connect(self, key):
        try:
            self.ssh.connect(hostname=self.parameters['host_ip'], 
                             username=self.parameters['username'], 
                             pkey=key, timeout=self.default_timeout_secs)
            print("...connect() success")
            return True
        except:
            print("...timeout reached during SSH connect")
            return False
        
    def _connection_is_active(self):        
        if self.ssh is not None and self.connection is not None:
            transport = self.ssh.get_transport()
            if transport is not None:
                if transport.is_active():
                    # use the code below if is_active() returns True
                    try:
                        # According to this, need to try multiple pings
                        # https://stackoverflow.com/questions/28288533/check-if-paramiko-ssh-connection-is-still-alive
                        transport.send_ignore()
                        self.ssh.exec_command('ls', timeout=self.default_timeout_secs)
                        return True
                    except:
                        # connection is closed
                        return False
        return False
    
    def _is_remote_directory(self, path):
        from stat import S_ISDIR
        try:
            return S_ISDIR(self.connection.stat(path).st_mode)
        except IOError:
            # Path doesn't exist so this is not a directory
            return False
        
    def read(self, path, type=None, sftp_file_string='*', local_dir='.', 
             local_filename=None, overwrite=False, entire_folder=True):
        super().read(path, type=type)
        
        print("SFTP read() called with path={}, type={}, sftp_file_string={}, local_dir={}, local_filename={}, overwrite={}, entire_folder={}".format(path, type, sftp_file_string, local_dir, local_filename, overwrite, entire_folder))
        #def sync_files_remote_sftp_to_local(sftp_conn, sftp_dir, sftp_file_string, local_dir):
        local_files = [f for f in os.listdir(local_dir) if os.path.isfile(os.path.join(local_dir, f))]
        #print(local_files)
        
        # Reset the SFTP connection
        if not self._connection_is_active():
            print("Connection inactive...reconnecting")
            self.connect()
        else:
            print("Connection is active")
        
        self.connection.chdir(path)
        sftp_file_list = self.connection.listdir()
        if type=='download':
            for filename in sftp_file_list:
                if fnmatch.fnmatch(filename, sftp_file_string):
                    print(filename)
                    # Only download the file if we don't have it in the target local directory already
                    # or if the 'overwrite' flag is set to True
                    output_filename = local_filename or filename
                    if output_filename not in local_files or overwrite:
                        local_filepath = os.path.join(local_dir, output_filename)
                        print('...downloading {} to {}'.format(filename, local_filepath))
                        if self._is_remote_directory(filename):
                            print("...{} is a directory".format(filename))
                            if entire_folder:
                                # Download the entire folder that matched the filestring
                                print("...recursing to download entire folder")
                                # Initiate recursive call but don't let it continue to recurse downward (for now)
                                self.read(os.path.join(path,filename), type=type, sftp_file_string='*', local_dir=local_dir,
                                          local_filename=local_filename, overwrite=overwrite, entire_folder=False)
                            else:
                                print("...not downloading")
                        else:
                            print("...getting filename={} and saving as {}".format(filename, local_filepath))
                            self.connection.get(filename, local_filepath)
                        print('...done')
                    else:
                        print("...already have a copy")

        elif type=='list':
            sftp_files = []
            for filename in sftp_file_list:
                if fnmatch.fnmatch(filename, sftp_file_string):
                    sftp_files.append(filename)
            return sftp_files

        elif type=='exists':
            for filename in sftp_file_list:
                if fnmatch.fnmatch(filename, sftp_file_string):
                    return True
            return False

        else:
            print("Not a valid 'type' parameter for SFTP read():", type)
            return None

    def write(self, data, destination, local_filename=None, overwrite=False, 
              suppress_overwrite_error=False,
              encryption_key=None):
        from io import BytesIO
        super().write(data, destination)
        
        expected_size = len(data.encode()) if data is not None else None
        print("SFTP write() called with data of size={}, destination={}, local_filename={}, overwrite={}".format(
            expected_size, destination, local_filename, overwrite))

        # Reset the SFTP connection
        if not self._connection_is_active():
            print("Connection inactive...reconnecting")
            self.connect()
        else:
            print("Connection is active")

        # check if file exists
        print("Checking if destination file already exists")
        try:
            stats = self.connection.stat(destination)
        except FileNotFoundError:
            print("File not found, ok to proceed")
        else:
            # found the file, should not continue
            import datetime
            print("File {} found on SFTP: size={}, mtime={}".format(destination, stats.st_size,
                                                                    datetime.datetime.fromtimestamp(stats.st_mtime)))
            if overwrite:
                print("Will overwrite existing file")
            else:
                if suppress_overwrite_error:
                    print("Will not overwrite existing SFTP file")
                    return
                else:
                    raise FileExistsError("File exists on SFTP, will not overwrite")

            
        # NOTE: put() and putfo() by default will do stat() on the file afterwards to confirm the file size
        if local_filename is not None:
            print("Provided local_filename, will put this file on SFTP and ignore anything passed in data")
            if encryption_key is None:
                self.connection.put(local_filename, destination)
            else:    
                # Encrypt the data in the file first
                with open(local_filename, "rb") as local_file:
                    # read all file data
                    file_data = local_file.read()
                    
                    # Encrypt the file's data first using the given encryption_key
                    data_encrypted = _EncryptDecryptData(file_data, encryption_key, 
                                                         encrypt_or_decrypt='encrypt')
                    
                    # Then write that to SFTP
                    self.connection.putfo(BytesIO(data_encrypted), destination)

        else:
            print("Will write passed in data to SFTP file")
            if encryption_key is None:
                self.connection.putfo(BytesIO(data.encode()), destination)
            else:
                # Encrypt the data first using the given encryption_key
                data_encrypted = _EncryptDecryptData(data.encode(), encryption_key, 
                                           encrypt_or_decrypt='encrypt')
                self.connection.putfo(BytesIO(data_encrypted), destination)
            
        print("Done!")
        
        
#######################################
### Microsoft Office Sharepoint connnector ###
class Sharepoint_Connector(Connector):
    required_params = ['domain', 'site', 'username', 'password']
    #DEFAULT_REGION = 'us-east-1'
    #from authentication import Auth
    #from shareplum import Site

    def __init__(self, parameters):
        Connector.__init__(self, parameters, required=self.required_params)
        self.type = 'sharepoint'
        self.authorization_cookie = None
        #self.bucket = None
        #self.session = None
        #self.client = None
     
 #     def _s3_list_all_files(self, prefix):
#         paginator = self.client.get_paginator("list_objects")

#         bucket_name = self.parameters['BUCKET']
#         page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
#         keys = []
#         for page in page_iterator:
#             if "Contents" in page:
#                 for key in page["Contents"]:
#                     keyString = key["Key"]
#                     keys.append(keyString)

#         return keys if keys else []
        
    def connect(self, type='connection'):
        from shareplum import Site, Office365
        from shareplum.site import Version

        if self.parameters is not None:
            print("Connecting to Sharepoint site: {} on the domain: {}".format(self.parameters['site'], 
                                                                               self.parameters['domain']))
            self.authorization_cookie = Office365(self.parameters['domain'], 
                                                   username=self.parameters['username'], 
                                                   password=self.parameters['password']).GetCookies()
            self.connection = Site(self.parameters['site'],
                                   version=Version.v365,
                                   authcookie=self.authorization_cookie)            
            print("...created connection to site")
            
        
    # type='list' if you want to read a list of the files in a given location (as the path)
    def read(self, path, type=None, to_file=None, encoding='utf-8'):
        super().read(path, type=type)

        if type=='list':
            self.connect(type='client')
            if self.bucket is not None:
                prefix_len = len(path)
                full_s3_file_list = self._s3_list_all_files(path)
                print("...found {} files to list".format(len(full_s3_file_list)))
                s3_files = [fkey[prefix_len:] for fkey in full_s3_file_list]
                #s3_files = [fkey.key[prefix_len:] for fkey in self.bucket.list(prefix=path)]
                return s3_files

        elif type=='download':
            self.connect(type='client')
            if self.client is not None:
                if to_file is not None:
                    print("...downloading file from S3 client in path '{}' to local file '{}'".format(path, to_file))
                    self.client.download_file(self.parameters['BUCKET'], path, to_file)
                    print("...done")
                else:
                    print("ERROR: Need to pass to_file parameter when using type='download' in an S3 connector") 
                    
        elif len(type)>=4 and type[:4]=='head':
            self.connect(type='client')
            print("type:", type)
            # Get the # of lines from the 'type' parameter if it's like type='head:10'
            if ':' in type:
                type_split = type.split(':')
                num_rows = int(type_split[1])
            else:
                # Default is 5 rows
                num_rows = 5
                
            if self.client is not None:
                s3_response_object = self.client.get_object(Bucket=self.parameters['BUCKET'], 
                                                            Key=path)
                object_content = s3_response_object['Body']
                all_lines = ''
                for i in range(num_rows):
                    line = object_content._raw_stream.readline()
                    all_lines += line.decode(encoding)
                return all_lines            

        elif type=='exists':
            import boto3
            from botocore.errorfactory import ClientError
            self.connect(type='client')
            try:
                self.client.head_object(Bucket=self.parameters['BUCKET'], Key=path)
                return True
            except ClientError:
                return False
                # Not found
                pass

        else:
            # Default is to return the file itself
            self.connect(type='client')
            s3_response_object = self.client.get_object(Bucket=self.parameters['BUCKET'], 
                                                        Key=path)
            object_content = s3_response_object['Body'].read()
            return object_content
        
        return None
        
    # Need to explicitly set is_folder=True if just want to create a folder at this destination (and will ignore data)
    def write(self, data, destination, local_filename=None, overwrite=False, is_folder=False, suppress_overwrite_error=False):
        from boto.s3.key import Key
        super().write(data, destination)
        
        # make sure we have a bucket -- otherwise call connect() to initialize the connection
        if self.bucket is None:
            self.connect()
            assert self.bucket is not None, f'S3_Connector self.bucket is still None even after connecting'
        k = Key(self.bucket)
        k.key = destination
        
        if is_folder:
            # note: this isn't really needed (can create S3 files without empty files for folders), but ok to do
            # Then just create the stub folder "key" in S3
            # first check to make sure you're not overwriting unexpectedly
            if k.exists():
                if overwrite:
                    print(f'{destination} exists, will overwrite with empty file for folder')
                else:
                    # check if size 0 -- no problem if so
                    k.open_read()
                    if k.size != 0:
                        if suppress_overwrite_error:
                            print(f'{destination} exists on S3 (size {k.size}), will not overwrite')
                            return
                        else:
                            raise FileExistsError(f'{destination} exists on S3 (size {k.size}), will not overwrite')
            print("Creating folder in the S3 bucket: '{}'".format(destination))
#             k = self.bucket.new_key(destination)
            k.set_contents_from_string('')
            
        else:
            # LS note: for now, we want to throw an error to make sure we convert to using local_filename everywhere
            if local_filename is None:
                raise NotImplementedError("Must specify local_filename for S3_Connector.write()")

            # check if file already exists
            print(f"Checking if destination S3 file {destination} already exists")
            if k.exists():
                # found the file, should not continue unless it's ok to overwrite
                if overwrite:
                    print("Will overwrite existing S3 file")
                else:
                    if suppress_overwrite_error:
                        print("Will not overwrite existing S3 file")
                        return
                    else:
                        raise FileExistsError("File exists on S3, will not overwrite")
            else:
                print("S3 file not found, ok to proceed")
            # Otherwise push the data/file into a file at the given destination
            if local_filename is not None:
                print("Writing local file '{}' to S3 at '{}'".format(local_filename, destination))
                k.set_contents_from_filename(local_filename)
            # TODO: uncomment below when removing the NotImplementedError above
#             else:
#                 if data is None:
#                     print('Did not pass in data, will just create an empty file')
#                     data = ''
#                 expected_size = len(data.encode()) if data is not None else None
#                 print("Writing passed in data of size={} to S3 at '{}'".format(expected_size, destination))
#                 k.set_contents_from_string(data)
        print('...done')
