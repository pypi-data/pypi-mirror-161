# encoding: utf-8
#
# Wrapper for interacting with Azure Blob Storage
# Copyright (c) 2020-2021 Klaus K. Holst.  All rights reserved.
#

import pandas as pd
import pickle
import os
from io import StringIO, BytesIO
from azure.storage.blob import BlobServiceClient
import azure.core as az
from .__utils__ import filesize # noqa F403
# import pyarrow.parquet as pq


class blob_storage:
    """Simple class for reading and writing files on Azure Blob Storage

    The connection string can either be given at the class
    initialization or alternatively it will be read from the
    environment variable AZURE_STORAGE_CONNECTION_STRING
    """
    blobservice = None
    active_container = None
    container_name = ""

    def __init__(self, container=None, connect_str=None,
                 account=None, credential=None, account_url=None, ):
        """Class initialization

        Examples
        --------
        import kvaser
        blob = kvaser.blob_storage('my-kvaser-test')
        df = kvaser.getdata() # A test pandas dataframe
        blob.write_pq(df, 'a.pq')
        {'etag': '"0x8D84D076069EDBB"', 'last_modified': datetime.datetime(2020, 8, 30, 17 ...
        blob.read_pq('a.pq')
        blob.write_csv(df, 'a.csv')
        blob.list()
        blob.read_csv('a.csv')

        Parameters
        ----------
        container: str
            Name of container to use
        connect_str: str
            Connection string (optional). If 'None' an attempt to retrieve this
            from the environment variable AZURE_STORAGE_CONNECTION_STRING will be made
        account: str
            Account (optional)
        credential: str
            SAS token (optional). If 'None' an attempt to retrieve this
            from the environment variable AZURE_SAS_TOKEN will be made
        account_url: str
            Account URL (optional)
        Returns
        -------
        blob_storage
            blob_storage object
        """
        if connect_str is None and credential is None:
            connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        if credential is None:
            credential = os.getenv('AZURE_SAS_TOKEN')

        if account_url is None:
            if account is None:
                account = os.getenv("OAUTH_STORAGE_ACCOUNT_NAME")
            account_url = "https://{}.blob.core.windows.net".format(account)

        if connect_str is not None:
            print("Connection string")
            self.blobservice = BlobServiceClient.from_connection_string(connect_str)
        else:
            # print("Credential")
            self.blobservice = BlobServiceClient(account_url=account_url,
                                                 credential=credential)

        if container is not None:
            self.select_container(container)

    def select_container(self, name):
        """Switch container.

        A new container will be created if the specified one does not yet exists.

        Parameters
        ----------
        name: str
            Name of container
        """
        self.container_name = name
        self.active_container = self.blobservice.get_container_client(name)
        try:
            self.active_container.get_container_properties()
        except az.exceptions.ResourceNotFoundError:
            self.active_container = self.active_container.create_container()

    def list(self):
        """List blobs in the container
        """
        for x in self.active_container.list_blobs():
            sz = filesize(x.size)
            print(x.name + '\t' + str(sz[0]) + ' ' + sz[1])

    def list_container(self):
        """List all containers
        """
        for x in self.blobservice.list_containers():
            print(x.name)

    def read_str(self, file):
        blob_client = self.blobservice.get_blob_client(container=self.container_name, blob=file)
        dl = blob_client.download_blob()
        return dl.content_as_text()

    def print(self, file):
        print(self.read_str(file))

    def write_str(self, string, file, append=True, sep=os.linesep):
        blob_client = self.blobservice.get_blob_client(container=self.container_name, blob=file)
        try:
            blob_client.get_blob_properties()
            if not append:
                blob_client.create_append_blob()
        except az.exceptions.ResourceNotFoundError:
            blob_client.create_append_blob()
        buf = StringIO()
        try:
            buf.writelines(str(string) + sep)
            val = blob_client.upload_blob(buf.getvalue(), blob_type='AppendBlob')
        finally:
            buf.close()
        return val

    def write(self, obj, file, type='pickle'):
        """Write pickle file on blob storage
        """
        blob_client = self.blobservice.get_blob_client(container=self.container_name, blob=file)
        buf = BytesIO()
        try:
            if type == 'parquet':
                obj.to_parquet(buf, index=False)
            else:
                pickle.dump(obj, buf)
            val = blob_client.upload_blob(buf.getvalue(), blob_type='BlockBlob', overwrite=True)
        finally:
            buf.close()
        return val

    def read(self, file, type='pickle'):
        """Read pickle file on blob storage
        """
        blob_client = self.blobservice.get_blob_client(container=self.container_name, blob=file)
        dl = blob_client.download_blob()
        obj = BytesIO(dl.content_as_bytes())
        if type == 'parquet':
            val = pd.read_parquet(obj)
        else:
            val = pickle.load(obj)
        return val

    def read_pq(self, file):
        """Read parquet file from blob storage
        """
        return self.read(file, type='parquet')

    def write_pq(self, df, file):
        """Write pandas dataframe to parquet file on blob storage
        """
        return self.write(df, file, type='parquet')

    def read_csv(self, file):
        """Read csv file from blob storage
        """
        blob_client = self.blobservice.get_blob_client(container=self.container_name, blob=file)
        dl = blob_client.download_blob()
        df = pd.read_csv(StringIO(dl.content_as_text()))
        return df

    def write_csv(self, df, file):
        """Write pandas dataframe to csv file on blob storage
        """
        blob_client = self.blobservice.get_blob_client(container=self.container_name, blob=file)
        output = df.to_csv(index=False, encoding='utf-8')
        return blob_client.upload_blob(output, blob_type='BlockBlob', overwrite=True)

    def delete(self, file):
        """Delete object (file) from blob storage
        """
        blob_client = self.blobservice.get_blob_client(container=self.container_name, blob=file)
        try:
            blob_client.delete_blob()
        except az.exceptions.ResourceNotFoundError:
            pass

    def delete_container(self, name=None):
        """Delete container
        """
        if name is None:
            name = self.container_name
        self.blobservice.delete_container(name)
