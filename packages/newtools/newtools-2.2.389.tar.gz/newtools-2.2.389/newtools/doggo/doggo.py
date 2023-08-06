# (c) 2012-2020 Deductive, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)


import gzip
import json
import logging
import os
import re
from datetime import datetime
from io import BytesIO

from newtools.aws import S3Location
from newtools.optional_imports import AWSRetry
from newtools.optional_imports import boto3
from newtools.optional_imports import pandas as pd


def _gzip_wrapped(func):
    def gzip_open(self, *args, **kwargs):
        if self.compression == 'gzip':
            f = func(self, *args, **kwargs)
            self._to_close.append(f)
            return gzip.open(f, self.mode)
        return func(self, *args, **kwargs)

    return gzip_open


class PandasDoggo:
    """
    Is a Panda a doggo?

    .. parsed-literal::

        ░░░░░░░░▄██▄░░░░░░▄▄░░
        ░░░░░░░▐███▀░░░░░▄███▌
        ░░▄▀░░▄█▀▀░░░░░░░░▀██░
        ░█░░░██░░░░░░░░░░░░░░░
        █▌░░▐██░░▄██▌░░▄▄▄░░░▄
        ██░░▐██▄░▀█▀░░░▀██░░▐▌
        ██▄░▐███▄▄░░▄▄▄░▀▀░▄██
        ▐███▄██████▄░▀░▄█████▌
        ▐████████████▀▀██████░
        ░▐████▀██████░░█████░░
        ░░░▀▀▀░░█████▌░████▀░░
        ░░░░░░░░░▀▀███░▀▀▀░░░░


    A class designed to simplify file IO operation to and from local or s3 files, with specific functionality for csv and parquet file formats

    Key features
    ------------

    - read / write csv and parquet files
    - read and write both locally and to s3
    - support gzip, snappy and zip compression
    - sensible s3 handling of different profiles / credentials

    Usage
    -----

    .. code-block:: python

        from newtools import PandasDoggo

        fh = PandasDoggo()

        df = fh.load('filename.ext')

        fh.save(df, 'path/to/new_file/ext')

    """

    def __init__(self,
                 boto_session=None,
                 logger=logging.getLogger("newtools.pandas_doggo")):
        """

        :param boto_session: optional boto3 session to use for
        :type boto_session: boto3.Session
        :param logger: the logger to use
        """

        if boto_session:
            self.s3_client = boto_session.client('s3')
        else:
            self.s3_client = None

        self._logger = logger

    @staticmethod
    def _extract_file_format(path):

        for part in reversed(path.split(".")[-2:]):
            if part in ('csv', 'parquet', 'pq'):
                return part

        raise ValueError(f'could not determine format of path: {path}, use file_format param to specify')

    @staticmethod
    def _extract_compression(path):
        # extend for other compression

        if path.endswith('.gzip') or path.endswith('.gz'):
            return 'gzip'
        if ('.snappy' in path) or path.endswith('.sz'):
            return 'snappy'
        if path.endswith('.zip'):
            return 'zip'

    def load(self, path, file_format=None, compression=None, request_payer='bucketowner', *args, **kwargs):
        """Load a file into a Pandas.DataFrame from local or s3 locations.

        :param path: required. Can be s3 or local s3 must be in `s3://` format - accepts `S3Location`
        :type path: str
        :param file_format: None. Autodetects from path, can be set to `csv` or `parquet` to explicitly force a format
        :param compression: optional, 'gzip', 'snappy' or None. Autodetects from path if path ends in `.gz`, `.gzip` or contains `.snappy`
        :param request_payer: either 'bucketowner' (default) or 'requester' - who incurs the cost of said operation
        :param args: args to pass to the panda to load the file
        :param kwargs: kwargs to pass to the panda to load the file eg columns=['subset', 'of', 'columns']
        :return: Pandas.DataFrame
        """

        file_format = file_format or self._extract_file_format(path)

        if file_format not in ('csv', 'parquet', 'pq'):
            raise ValueError(f'detected format:{format} is not recognized file format for load')

        if file_format == 'csv':
            return self.load_csv(path, compression=compression, request_payer=request_payer, *args, **kwargs)

        elif file_format in ('parquet', 'pq'):
            return self.load_parquet(path, compression=compression, request_payer=request_payer, *args, **kwargs)

    def load_csv(self, path, compression=None, request_payer='bucketowner', *args, **kwargs):
        """alias for .load(path, format='csv')"""
        if 'chunksize' in kwargs:
            raise NotImplementedError("PandasDoggo does not support chunksize for loading data frames")

        compression = compression or self._extract_compression(path)
        fm = FileDoggo(path, mode='rb', client=self.s3_client, compression=compression, request_payer=request_payer)
        with fm as f:
            df = pd.read_csv(f, *args, **kwargs)

        return df

    def load_parquet(self, path, compression=None, request_payer='bucketowner', *args, **kwargs):
        """alias for .load(path, format='parquet')"""

        compression = compression or self._extract_compression(path)
        fm = FileDoggo(path, mode='rb', client=self.s3_client, compression=compression, request_payer=request_payer)
        with fm as f:
            df = pd.read_parquet(f, engine='pyarrow', *args, **kwargs)

        return df

    def save(self, df, path, file_format=None, compression=None, request_payer='bucketowner', *args, **kwargs):
        """Save a file into a Pandas.DataFrame from local or s3 locations.

        :param df: Data frame
        :type df: Pandas.DataFrame
        :param path: required. Can be s3 or local s3 must be in `s3://` format - accepts `S3Location`
        :type path: str
        :param file_format: 'None. Autodetects from path, can be set to `csv` or `parquet` to explicitly force a format
        :param compression: None. Supports gzip and snappy, autodetects from path if path ends in `.gz`, `.gzip` or contains `.snappy`
        :param request_payer: either 'bucketowner' (default) or 'requester' - who incurs the cost of said operation
        :param args: args to pass to the panda to save the file
        :param kwargs: kwargs to pass to the panda to save the file eg index=None
        """

        file_format = file_format or self._extract_file_format(path)

        if file_format == 'csv':
            return self.save_csv(df, path, compression=compression, request_payer=request_payer, *args, **kwargs)

        elif file_format in ('parquet', 'pq'):
            return self.save_parquet(df, path, compression=compression, request_payer=request_payer, *args, **kwargs)

    def save_csv(self, df, path, compression=None, request_payer='bucketowner', *args, **kwargs):
        """Alias for .save(df, format='csv')"""
        compression = compression or self._extract_compression(path)
        fm = FileDoggo(path, mode='wb', client=self.s3_client, compression=compression, request_payer=request_payer)
        with fm as f:
            f.write(df.to_csv(None, *args, **kwargs).encode('utf-8'))

    def save_parquet(self, df, path, compression=None, request_payer='bucketowner', *args, **kwargs):
        """Alias for .save(df, format='parquet')"""

        compression = compression or self._extract_compression(path)
        fm = FileDoggo(path, mode='wb', client=self.s3_client, compression=compression, request_payer=request_payer)
        with fm as f:
            df.to_parquet(f, *args, **kwargs)

    def save_partitioned(self,
                         df,
                         base_path,
                         name,
                         suffix,
                         partition_columns,
                         partition_string="",
                         date_time_format="%Y-%m-%d_%H%M%S.%f",
                         compression=None,
                         request_payer='bucketowner', *args, **kwargs):
        """Save a data frame into multiple files, partitioned by the specified columns. The base path can be
        local file system, or S3.

        Based on athena_partition from old tools. Notable differences are as follows:
        * PandasDoggo saves the index as default so pass index=False for comparable behavior
        * base_path - new parameter that was previously taken from the passed file_handler
        * partition_columns - replaces partition_categories
        * partition_dtypes - not supported so please apply any changes to dtype before passing using df.astype(dict(zip(["col1", "col7"], [int, int])
        * columns_to_keep - not supported, please only send a slice of the data frame with the columns you want to partition or save
        * file_handler - not supported, uses the PandasDoggo class.

        :param df: The data frame to be partitioned
        :param base_path: The base path to save the files to
        :param name: If provided all files filename will start with this
        :param suffix: The extension the file should be saved with, .csv for csv, and .parquet for parquet
        :param partition_columns: The columns to partition the data on
        :param partition_string: Allows formatting folder names, will be dependant on how many partition categories there
                are, defaults to creating hive-format folders and sub folders in order of partitioning
        :param date_time_format: To minimise chances of overwrite the saved files contain the date time of when this
                function was called, this param specifies the format of the date time
        :param compression: None. Supports gzip and snappy, autodetects from suffix if it ends in `.gz`, `.gzip` or contains `.snappy`
        :param request_payer: either 'bucketowner' (default) or 'requester' - who incurs the cost of said operation
        :param args: args to pass to the panda to save the file
        :param kwargs: kwargs to pass to the panda to save the file eg index=None
        :return: Returns a full list of all file paths created, doesnt return base path as part of this
        """

        if any(df[partition_columns].isna().any()) or any((df[partition_columns] == "").any()):  # pragma: no cover
            raise ValueError('The partition columns contain NaN values')

        # Set up the default partition string
        if not partition_string:
            partition_string = "/".join([col + "={}" for col in partition_columns])

        paths = list()

        # Create each partition file
        for partition_values, group_df in df.groupby(partition_columns, sort=False):

            # Format the partitions
            if len(partition_columns) == 1:
                partition_values = [partition_values]
            partitions = partition_string.format(*partition_values)

            # Get the time
            time = datetime.now().strftime(date_time_format)
            self._logger.info("time is {}".format(time))

            # Get the file
            file = f"{base_path}/{partitions}/{name}{datetime.now().strftime(date_time_format)}{suffix}"
            self._logger.info(json.dumps({"message": "Saving parquet to location {}".format(file)}))

            # Create the path if it doesn't exist...
            if file.startswith("/"):
                try:
                    os.makedirs(os.path.dirname(file))
                except FileExistsError:  # pragma: no cover
                    pass

            # Save the dataframe
            self.save(group_df[[col for col in df.columns if col not in partition_columns]],
                      file, compression=compression, request_payer=request_payer, *args, **kwargs)

            # Add to the list to return
            paths.append(file)

        return paths


class FileDoggo:
    """

He fetches the things you want. Tv remotes, slippers, newspapers, files. Mostly files though.

.. code-block:: python

    from newtools import FileDoggo
    import boto3

    path = 's3 or local path'
    s3_client = boto3.Session().client('s3')
    with FileDoggo(path, mode='rb', client=s3_client) as f:
        f.read()

This is written to treat local paths and s3 paths the same, returning a file like object for either.

"""
    _connection = None

    def __init__(self, path, mode='rb', is_s3=None, client=None, compression=None, request_payer='bucketowner'):
        """
        Creates the class

        :param path: path to file to connect to. s3 or local path
        :type path: str or S3Location
        :param mode: opening mode for file, note s3 only allows 'rb' or 'wb'
        :param is_s3: force Doggo to treat path as an S3Location, otherwise autodetects if beings with "s3://"
        :type is_s3: bool
        :param client: optional `boto3.Session().Client('s3')` instance to use for s3 operations
        :param compression: None, 'gzip' or 'snappy'.
        :param request_payer: either 'bucketowner' or 'requester' - who incurs the cost of said operation
        """

        self.buffer = BytesIO()
        self.mode = mode

        self.is_s3 = is_s3 or path.startswith('s3://')
        if self.is_s3:
            # allows you to specify s3 for paths that don't begin with s3:// for whatever reason you might want
            self.path = S3Location(path)
        else:
            self.path = path

        self.request_payer = request_payer

        self._client = client
        if compression in [None, 'gzip', 'snappy']:
            self.compression = compression
        else:
            raise NotImplementedError(f"Compression {compression} is not supported in FileDoggo")
        self._to_close = []

    @property
    def connection(self):
        if not self._connection:
            self._connection = self._connect()
        return self._connection

    @property
    def client(self):
        if not self._client:
            self._client = boto3.Session().client('s3')
        return self._client

    def close(self):

        if self._connection:
            for c in [self._connection] + self._to_close:
                if not c.closed:
                    c.close()

    def __enter__(self):
        return self.connection

    def __exit__(self, etype, value, traceback):
        # ¯\_(ツ)_/¯
        if self.is_s3 and 'w' in self.mode:
            self._write_s3()

        self.close()

    @_gzip_wrapped
    def _connect(self):

        if self.is_s3:
            if self.mode == 'rb':
                return self._read_s3()
            elif self.mode == 'wb':
                # check s3 exists? meh, writing to a buffer is so fast i think the overhead isn't worth
                return self.buffer  # write to this buffer and we'll upload later
            else:
                raise ValueError(f'mode {self.mode} is not supported')

        else:

            return open(self.path, self.mode)

    @AWSRetry.backoff(tries=5, delay=1, backoff=1, added_exceptions=['404'])
    def _read_s3(self):

        self.client.download_fileobj(Bucket=self.path.bucket, Key=self.path.key, Fileobj=self.buffer,
                                     ExtraArgs={'RequestPayer': self.request_payer})
        self.buffer.seek(0)
        return self.buffer

    def _write_s3(self):

        if self.compression == 'gzip':
            self.connection.close()  # flushes writing to gzip

        self.buffer.seek(0)
        self.client.upload_fileobj(Bucket=self.path.bucket, Key=self.path.key, Fileobj=self.buffer,
                                   ExtraArgs={'RequestPayer': self.request_payer})
