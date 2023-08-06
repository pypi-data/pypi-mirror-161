import unittest
import warnings
import os
import tempfile
import shutil

from newtools.optional_imports import boto3
from newtools.optional_imports import pandas as pd

from newtools import CSVDoggo, S3Location, log_to_stdout, DoggoFileSystem

from s3fs import S3FileSystem

FpCSVEncodingError = ValueError

logger = log_to_stdout("newtools")

s3_bucket = "newtools-tests"


class CSVFileTests(unittest.TestCase):
    saved_suffix = ".saved"
    root_prefix = "csvhandler"
    s3 = None
    local_base_path = None

    @classmethod
    def setUpClass(cls):

        # Original test data location
        cls.orig_base_path = "{0}/test_data/{1}/".format(
            os.path.dirname(os.path.abspath(__file__)), cls.root_prefix)

        # Upload test data to s3
        cls.s3_base_path = f"s3://{s3_bucket}/{cls.root_prefix}/"
        cls.s3 = S3FileSystem()
        cls.dfs = DoggoFileSystem()
        # cls.dfs.rm(f"{cls.s3_base_path}", recursive=True)
        if cls.dfs.exists(f"{cls.s3_base_path}"):
            cls.dfs.rm(f"{cls.s3_base_path}", recursive=True)

        cls.s3.put(lpath=cls.orig_base_path,
                   rpath=cls.s3_base_path,
                   recursive=True)

        # Save test data to local folder
        cls.local_base_path = tempfile.mkdtemp() + '/'
        os.mkdir(cls.local_base_path + cls.root_prefix)

    @classmethod
    def tearDownClass(cls):
        # Delete uploaded/created files
        cls.dfs.rm(f"{cls.s3_base_path}", recursive=True)
        shutil.rmtree(cls.local_base_path, ignore_errors=True)

    def test_files(self):

        warnings.simplefilter("ignore", ResourceWarning)

        # Test file location
        os.makedirs(self.local_base_path + self.root_prefix, exist_ok=True)

        # Get list of the files
        files = [S3Location(f).file for f in self.s3.glob(f"s3://{s3_bucket}/{self.root_prefix}/*.csv") if
                 'unable_to_decode' not in f]

        # Create the handlers
        csv_orig = CSVDoggo(base_path=self.orig_base_path,
                            detect_parameters=True)
        csv_s3 = CSVDoggo(base_path=self.s3_base_path,
                          detect_parameters=True)
        csv_local = CSVDoggo(base_path=self.local_base_path,
                             detect_parameters=True)
        csv_empty = CSVDoggo(detect_parameters=True)

        # Alternate how the path is split
        use_empty_base = True
        if len(files) < 1:
            raise ValueError('The test data folder is incorrect')
        for file in files:

            logger.info("testing file {0}".format(file))

            # Read file from S3
            if use_empty_base:
                if file.endswith(".gzip"):
                    df1 = csv_empty.load_df(self.s3_base_path + file, compression="gzip")
                else:
                    df1 = csv_empty.load_df(self.s3_base_path + file)
            else:
                if file.endswith(".gzip"):
                    df1 = csv_s3.load_df(file, compression="gzip")
                else:
                    df1 = csv_s3.load_df(file)

            # Write file to S3
            if use_empty_base:
                csv_empty.save_df(df1, self.s3_base_path +
                                  file + self.saved_suffix)
            else:
                csv_s3.save_df(df1, file + self.saved_suffix)

            # Check DataFrames match
            if use_empty_base:
                df2 = csv_empty.load_df(
                    self.s3_base_path + file + self.saved_suffix)
            else:
                df2 = csv_s3.load_df(file + self.saved_suffix)
            pd.testing.assert_frame_equal(df1, df2)

            # Check strings match
            str1 = csv_s3.df_to_string(df1)
            str2 = csv_s3.df_to_string(df2)
            self.assertMultiLineEqual(str1, str2)

            # Read file locally
            if use_empty_base:
                df3 = csv_empty.load_df(self.orig_base_path + file)
            else:
                df3 = csv_orig.load_df(file)

            # Write file locally
            if use_empty_base:
                csv_empty.save_df(df3, self.local_base_path +
                                  file + self.saved_suffix)
            else:
                csv_local.save_df(df3, file + self.saved_suffix)

            # Check DataFrames match
            if use_empty_base:
                df4 = csv_empty.load_df(
                    self.local_base_path + file + self.saved_suffix)
            else:
                df4 = csv_local.load_df(file + self.saved_suffix)
            pd.testing.assert_frame_equal(df3, df4)

            # Check strings match
            str3 = csv_orig.df_to_string(df3)
            str4 = csv_local.df_to_string(df4)
            self.assertMultiLineEqual(str3, str4)

            use_empty_base = not use_empty_base


class CSVOtherTests(unittest.TestCase):
    local_base_path = None

    @classmethod
    def setUpClass(cls):
        # Original test data location
        cls.orig_base_path = "{0}/test_data/csvhandler/".format(
            os.path.dirname(os.path.abspath(__file__)))

        cls.local_base_path = tempfile.mkdtemp() + '/'
        cls.s3_base_path = "s3://{}/".format(s3_bucket)

        cls.csv = CSVDoggo(base_path=cls.orig_base_path)
        cls.csv_windows = CSVDoggo(base_path=cls.orig_base_path, csv_encoding="Windows-1252")

    @classmethod
    def tearDownClass(cls):
        # Delete uploaded/created files
        shutil.rmtree(cls.local_base_path, ignore_errors=True)

    def test_encoding_error(self):
        with self.assertRaises(FpCSVEncodingError):
            csv = CSVDoggo(base_path=self.orig_base_path)
            csv.load_df("test_cities_reference1252.csv")

    def test_csv_parameter(self):
        csv = CSVDoggo(base_path=self.orig_base_path)
        csv.load_df("test_cities_reference1252.csv",
                    csv_encoding="Windows-1252")

    def test_gzip(self):
        csv = CSVDoggo(base_path=self.orig_base_path,
                       compression="gzip")
        df1 = csv.load_df("test.csv.gz")
        csv.save_df(df1, "test2.csv.gz")
        df2 = csv.load_df("test2.csv.gz")
        pd.testing.assert_frame_equal(df1, df2)

    def test_zip(self):
        with self.assertRaises(NotImplementedError):
            csv = CSVDoggo(base_path=self.orig_base_path, compression="zip")
            df1 = csv.load_df("test.csv.zip")
            csv.save_df(df1, "test2.csv.zip")
            df2 = csv.load_df("test2.csv.zip")
            pd.testing.assert_frame_equal(df1, df2)

    def test_forcing_dtype(self):
        csv = CSVDoggo(base_path=self.orig_base_path)
        df1 = csv.load_df("test_int_is_unique_clean.csv", force_dtype=str)
        self.assertEqual(str(df1['TotalEpisodes'].dtype), 'object')

    def test_no_header(self):
        csv = CSVDoggo(base_path=self.orig_base_path)
        df = csv.load_df("test_cities_reference1252.csv",
                         csv_encoding="Windows-1252",
                         header=-1,
                         force_dtype=str)

        csv2 = CSVDoggo(base_path=self.local_base_path,
                        header=-1)
        csv2.save_df(df, "banana.csv")
        df2 = csv2.load_df("banana.csv",
                           force_dtype=str)

        pd.testing.assert_frame_equal(df, df2, check_index_type=False)

    def test_sniffer(self):
        csv = CSVDoggo(base_path=self.orig_base_path)
        csv._sniff_parameters("email_test.csv")

    def test_sniffer_unable_to_decode(self):
        """
        cannot find encoding for encrypted file - need to decrypt first
        """
        with self.assertRaises(FpCSVEncodingError):
            self.csv._sniff_parameters("unable_to_decode.csv")

    def test_nan_values(self):
        """
        the test data should actually include nans to make this test better!
        """
        csv_nan = CSVDoggo(base_path=self.orig_base_path, nan_values=["1", "2"])
        temp_df = csv_nan.load_df("email_test.csv")
        csv_nan.save_df(temp_df, "temporary.csv")
        os.remove(os.path.join(self.orig_base_path, "temporary.csv"))

    def test_pd_kwargs_for_reading(self):
        """
        allows pass through of features not directly supported by CSVDoggo
        (test by making sure that blank entries are read in as blanks)
        """
        CSVDoggo(base_path=self.orig_base_path,
                 pd_kwargs=dict(keep_na_values=False, ))

    def test_basic_chunksize(self):
        with self.assertRaises(NotImplementedError):
            csv = CSVDoggo(base_path=self.orig_base_path)
            dfs = csv.load_df("test_cities_reference1252.csv",
                              csv_encoding="Windows-1252",
                              chunksize=10)

            self.assertEqual([len(df) for df in dfs], [10, 10, 10, 10, 9])

    def test_s3_chunks(self):
        with self.assertRaises(NotImplementedError):
            s3c = boto3.client("s3")
            csvh = CSVDoggo(base_path=self.orig_base_path)
            df_lt = csvh.load_df("email_test.csv", chunksize=5)
            df_init = self.csv.load_df("email_test.csv")
            pd.testing.assert_frame_equal(df_init.head(5), df_lt.get_chunk(5))

    def test_s3_nrows(self):
        csv = CSVDoggo(base_path=self.orig_base_path)
        df = csv.load_df("test_cities_reference1252.csv",
                         csv_encoding="Windows-1252",
                         nrows=10)

        self.assertEqual(len(df), 10)

    def test_usecols(self):
        csv = CSVDoggo(base_path=self.orig_base_path)
        df = csv.load_df("test_cities_dirty.csv", usecols=['city'])
        expected_df = csv.load_df("test_usecols_expected.csv")
        pd.testing.assert_frame_equal(expected_df, df)
