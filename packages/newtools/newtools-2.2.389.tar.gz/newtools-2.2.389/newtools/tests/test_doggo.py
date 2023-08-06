# (c) 2012-2018 Deductive, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)

import gzip
import logging
import multiprocessing
import os
import shutil
import unittest
from random import random
from time import sleep

import pyarrow as pa
from pandas.testing import assert_frame_equal
from s3fs import S3FileSystem

from newtools import CSVDoggo, log_to_stdout
from newtools import PandasDoggo, FileDoggo, S3Location, DoggoFileSystem, DoggoLock, DoggoWait, DynamoDogLock
from newtools.optional_imports import boto3
from newtools.optional_imports import numpy as np
from newtools.optional_imports import pandas as pd
from .base_test import BaseTest

s3_bucket = "newtools-tests"

log_to_stdout("newtools", level=logging.DEBUG)


class TestDoggos(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data', 'pandas_doggo_tests')

        # Upload test data to s3
        cls.s3_base_path = f"s3://{s3_bucket}/generic/"
        cls.s3 = S3FileSystem()
        for file in cls.s3.glob(f"{cls.s3_base_path}*"):
            cls.s3.rm(file)

        cls.s3.put(lpath=os.path.join(cls.base_path, "csv", "generic"),
                   rpath=cls.s3_base_path,
                   recursive=True)

    @classmethod
    def tearDownClass(cls):
        for file in cls.s3.glob(f"{cls.s3_base_path}*"):
            cls.s3.rm(file)

    def test_read_csv_local(self):
        """read a local csv"""

        expected_df = pd.DataFrame({'e-mail': {0: 'n@gmail.com', 1: 'p@gmail.com', 2: 'h@gmail.com', 3: 's@gmail.com',
                                               4: 'l@gmail.com', 5: 'v@gmail.com', 6: None},
                                    'number': {0: 0, 1: 1, 2: 0, 3: 0, 4: 1, 5: 0, 6: 0}})
        pth = os.path.join(self.base_path, 'csv', 'generic', 'email_test.csv')
        session = boto3.Session()
        fh = PandasDoggo(boto_session=session)
        df = fh.load(pth)
        pd.testing.assert_frame_equal(df, expected_df)

    def test_read_csv_local_gzip(self):
        pth = os.path.join(self.base_path, 'csv', 'gzip', 'test.csv.gz')

        fh = PandasDoggo()
        df = fh.load_csv(pth, compression='gzip')
        print(df.to_csv(index=0))

    def test_write_csv_local_gzip(self):
        pth_in = os.path.join(self.base_path, 'csv', 'gzip', 'uncompressed.csv')
        pth_out = os.path.join(self.base_path, 'csv', 'gzip', 'write.csv.gzip')
        pth_exp = os.path.join(self.base_path, 'csv', 'gzip', 'write_target.csv.gzip')
        fh = PandasDoggo()
        df = fh.load_csv(pth_in)

        fh.save_csv(df, pth_out, compression='gzip', index=0)
        with gzip.open(pth_out) as r, gzip.open(pth_exp) as exp:
            self.assertEqual(r.read().decode('utf-8'), exp.read().decode('utf-8'))

        os.remove(pth_out)

    def test_write_csv_local_gzip_infer(self):
        pth_in = os.path.join(self.base_path, 'csv', 'gzip', 'uncompressed.csv')
        pth_out = os.path.join(self.base_path, 'csv', 'gzip', 'write.csv.gzip')
        pth_exp = os.path.join(self.base_path, 'csv', 'gzip', 'write_target.csv.gzip')
        fh = PandasDoggo()
        df = fh.load_csv(pth_in)

        fh.save(df, pth_out, index=0)
        with gzip.open(pth_out) as r, gzip.open(pth_exp) as exp:
            self.assertEqual(r.read().decode('utf-8'), exp.read().decode('utf-8'))

        os.remove(pth_out)

    def test_read_csv_local_gzip_infer(self):
        pth = os.path.join(self.base_path, 'csv', 'gzip', 'test.csv.gz')

        fh = PandasDoggo()
        df = fh.load(pth)

    def test_read_csv_local_zip_infer(self):
        with self.assertRaises(NotImplementedError):
            pth = os.path.join(self.base_path, 'csv', 'gzip', 'test.csv.zip')
            fh = PandasDoggo()
            df = fh.load(pth)

    def test_write_csv_local(self):
        df = pd.DataFrame({'e-mail': {0: 'n@gmail.com', 1: 'p@gmail.com', 2: 'h@gmail.com', 3: 's@gmail.com',
                                      4: 'l@gmail.com', 5: 'v@gmail.com', 6: None},
                           'number': {0: 0, 1: 1, 2: 0, 3: 0, 4: 1, 5: 0, 6: 0}})
        pth = os.path.join(self.base_path, 'csv', 'generic', 'email_test_copy.csv')
        expected_pth = os.path.join(self.base_path, 'csv', 'generic', 'email_test.csv')
        fh = PandasDoggo()
        fh.save(df, pth, index=None)
        with FileDoggo(pth) as p, FileDoggo(expected_pth) as p2:
            self.assertEqual(p.read().strip(), p2.read().strip())

        os.remove(pth)

    def test_read_pq_local(self):
        """read a local parquet"""
        fh = PandasDoggo()
        pth = os.path.join(self.base_path, 'parquet', 'data.parquet')
        df = fh.load(pth)

    def test_read_pq_local_snappy(self):
        pth = os.path.join(self.base_path, 'parquet', 'snappy', 'compressed.snappy.parquet')

        fh = PandasDoggo()
        df = fh.load_parquet(pth)
        print(df.to_parquet(pth, index=0))

    def test_write_pq_local(self):
        fh = PandasDoggo()
        df = pd.read_csv(os.path.join(self.base_path, 'parquet', 'emails.csv'))
        fh.save_parquet(df, os.path.join(self.base_path, 'parquet', 'emails.parquet'))
        os.remove(os.path.join(self.base_path, 'parquet', 'emails.parquet'))

    def test_write_pq_snappy(self):
        pth_in = os.path.join(self.base_path, 'parquet', 'snappy', 'uncompressed.parquet')
        pth_out = os.path.join(self.base_path, 'parquet', 'snappy', 'compressed.snappy.parquet')
        pth_exp = os.path.join(self.base_path, 'parquet', 'snappy', 'writing_target.snappy.parquet')
        fh = PandasDoggo()
        df = pd.read_parquet(pth_in)
        fh.save_parquet(df, pth_out)
        r = pd.read_parquet(pth_out, engine='pyarrow')
        exp = pd.read_parquet(pth_exp, engine='pyarrow')

        pd.testing.assert_frame_equal(r, exp)

    def test_read_pq_local_with_args(self):
        fh = PandasDoggo()
        pth = os.path.join(self.base_path, 'parquet', 'data.parquet')
        df = fh.load_parquet(pth, columns=['country', 'birthdate', 'salary', 'title'])
        self.assertEqual(sorted(list(df.columns)), sorted(['country', 'birthdate', 'salary', 'title']))

    def test_pq_schema_int64(self):
        new_file_path = os.path.join(self.base_path,
                                     'parquet',
                                     'new_data.parquet')
        test_df = pd.DataFrame(
            {"col1": [1, 2, 3, 4, 5], "col2": ["a", "s", "6", "7", "t"]})
        fields = [
            pa.field("col1", pa.int64()),
            pa.field("col2", pa.string())
        ]
        my_schema = pa.schema(fields)
        fh = PandasDoggo()

        fh.save_parquet(test_df, new_file_path, schema=my_schema)

        pd.testing.assert_frame_equal(test_df, fh.load_parquet(new_file_path))
        os.remove(new_file_path)

    def test_pq_schema_int32(self):
        # Tests the down casting of int64 to int32 without explicit conversion
        new_file_path = os.path.join(self.base_path,
                                     'parquet',
                                     'new_data.parquet')
        test_df = pd.DataFrame(
            {"col1": [1, 2, 3, 4, 128], "col2": ["a", "s", "6", "7", "t"]})
        fields = [
            pa.field("col1", pa.int32()),
            pa.field("col2", pa.string())
        ]
        test_df = test_df.astype({"col1": 'Int32'})
        my_schema = pa.schema(fields)
        fh = PandasDoggo()

        fh.save_parquet(test_df, new_file_path, schema=my_schema)

        pd.testing.assert_frame_equal(test_df, fh.load_parquet(new_file_path))
        os.remove(new_file_path)

    def test_pq_schema_int32_nulls(self):
        new_file_path = os.path.join(self.base_path,
                                     'parquet',
                                     'new_data_nulls.parquet')
        test_df = pd.DataFrame(
            {"col1": pd.Series([1, 2, 3, 4, 128, pd.NA, None], dtype='Int32'),
             "col2": ["a", "s", "6", "7", "t", 'pd.NA', 'None']})
        fields = [
            pa.field("col1", pa.int32()),
            pa.field("col2", pa.string())
        ]

        my_schema = pa.schema(fields)
        fh = PandasDoggo()

        fh.save_parquet(test_df, new_file_path, schema=my_schema)

        pd.testing.assert_frame_equal(test_df, fh.load_parquet(new_file_path))
        os.remove(new_file_path)

    def test_pq_schema_int64_nulls(self):
        new_file_path = os.path.join(self.base_path,
                                     'parquet',
                                     'new_data_nulls.parquet')
        test_df = pd.DataFrame(
            {"col1": pd.Series([1, 2, 3, 4, 128, pd.NA, None], dtype='Int64'),
             "col2": ["a", "s", "6", "7", "t", 'pd.NA', 'None']})
        fields = [
            pa.field("col1", pa.int64()),
            pa.field("col2", pa.string())
        ]

        my_schema = pa.schema(fields)
        fh = PandasDoggo()

        fh.save_parquet(test_df, new_file_path, schema=my_schema)

        pd.testing.assert_frame_equal(test_df, fh.load_parquet(new_file_path))
        os.remove(new_file_path)

    def test_pq_schema_datetime(self):
        new_file_path = os.path.join(self.base_path,
                                     'parquet',
                                     'new_data.parquet')
        rng = pd.date_range('2015-02-24', periods=5, freq='23H')
        test_df = pd.DataFrame({'Date': rng, 'Val': np.random.randn(len(rng))})

        test_df['Date'] = pd.to_datetime(test_df['Date'], unit='D')
        fields = [
            pa.field("Date", pa.timestamp('ms')),
            pa.field("Val", pa.float64())
        ]
        my_schema = pa.schema(fields)
        fh = PandasDoggo()

        fh.save_parquet(test_df, new_file_path, schema=my_schema)

        pd.testing.assert_frame_equal(test_df, fh.load_parquet(new_file_path))
        os.remove(new_file_path)

    def test_read_csv_s3(self):
        """read a csv from s3"""
        expected_df = pd.DataFrame({'e-mail': {0: 'n@gmail.com', 1: 'p@gmail.com', 2: 'h@gmail.com', 3: 's@gmail.com',
                                               4: 'l@gmail.com', 5: 'v@gmail.com', 6: None},
                                    'number': {0: 0, 1: 1, 2: 0, 3: 0, 4: 1, 5: 0, 6: 0}})
        pth = S3Location('newtools-tests').join('generic', 'email_test.csv')
        session = boto3.Session()
        fh = PandasDoggo(boto_session=session)
        df = fh.load(pth)
        pd.testing.assert_frame_equal(df, expected_df)

    def test_read_csv_s3_request_payer_fail(self):
        """try to read a csv from s3 with request_payer permissions on the bucket and 'requester' not set"""
        pth = S3Location('newtools-test-request-payer').join('generic', 'email_test.csv')
        session = boto3.Session()
        fh = PandasDoggo(boto_session=session)

        with self.assertRaises(Exception) as err:
            fh.load(pth)

        self.assertEqual(err.exception.args[0], 'An error occurred (403) when calling the HeadObject operation: Forbidden')

    def test_read_csv_s3_request_payer(self):
        """try to read a csv from s3 with request_payer permissions on the bucket and 'requester' set in Doggo"""
        expected_df = pd.DataFrame({'e-mail': {0: 'n@gmail.com', 1: 'p@gmail.com', 2: 'h@gmail.com', 3: 's@gmail.com',
                                               4: 'l@gmail.com', 5: 'v@gmail.com', 6: None},
                                    'number': {0: 0, 1: 1, 2: 0, 3: 0, 4: 1, 5: 0, 6: 0}})
        pth = S3Location('newtools-test-request-payer').join('generic', 'email_test.csv')
        session = boto3.Session()
        fh = PandasDoggo(boto_session=session)

        df = fh.load(pth, request_payer='requester')
        pd.testing.assert_frame_equal(df, expected_df)

    def test_write_csv_s3(self):
        df = pd.DataFrame({'e-mail': {0: 'n@gmail.com', 1: 'p@gmail.com', 2: 'h@gmail.com', 3: 's@gmail.com',
                                      4: 'l@gmail.com', 5: 'v@gmail.com', 6: None},
                           'number': {0: 0, 1: 1, 2: 0, 3: 0, 4: 1, 5: 0, 6: 0}})
        pth = S3Location('newtools-tests').join('generic', 'email_test_copy.csv')
        expected_pth = S3Location('newtools-tests').join('generic', 'email_test.csv')
        fh = PandasDoggo()
        fh.save(df, pth, index=None)
        with FileDoggo(pth) as p, FileDoggo(expected_pth) as p2:
            self.assertEqual(p.read().strip(), p2.read().strip())

        s3 = boto3.resource('s3')
        obj = s3.Object(pth.bucket, pth.key)
        obj.delete()

    def test_write_csv_s3_gzip(self):
        df = pd.DataFrame({'e-mail': {0: 'n@gmail.com', 1: 'p@gmail.com', 2: 'h@gmail.com', 3: 's@gmail.com',
                                      4: 'l@gmail.com', 5: 'v@gmail.com', 6: None},
                           'number': {0: 0, 1: 1, 2: 0, 3: 0, 4: 1, 5: 0, 6: 0}})
        pth = S3Location('newtools-tests').join('generic', 'email_test_copy.csv.gz')

        fh = PandasDoggo()

        fh.save(df, pth, index=None, compression="gzip")

        pd.testing.assert_frame_equal(fh.load_csv(pth), df)

        s3 = boto3.resource('s3')
        obj = s3.Object(pth.bucket, pth.key)
        obj.delete()

    def test_read_pq_s3(self):
        """read a parquet from s3"""
        fh = PandasDoggo()

        df_s3 = fh.load_parquet('s3://newtools-tests/07092018pqtest/data.parquet')

        pth_local = os.path.join(self.base_path, 'parquet', 'data.parquet')
        df_l = fh.load_parquet(pth_local)

        pd.testing.assert_frame_equal(df_s3, df_l)

    def test_write_pq_s3(self):
        fh = PandasDoggo()
        pth_local = os.path.join(self.base_path, 'parquet', 'data.parquet')
        df_l = fh.load_parquet(pth_local)
        s3 = boto3.resource('s3')
        obj = s3.Object('newtools-tests', '07092018pqtest/write.parquet')
        obj.delete()  # just in case
        fh.save(df_l, 's3://newtools-tests/07092018pqtest/write.parquet')

        obj.load()  # checks that it was written
        obj.delete()

    def test_write_pq_s3_snappy(self):
        df = pd.DataFrame({'e-mail': {0: 'n@gmail.com', 1: 'p@gmail.com', 2: 'h@gmail.com', 3: 's@gmail.com',
                                      4: 'l@gmail.com', 5: 'v@gmail.com', 6: None},
                           'number': {0: 0, 1: 1, 2: 0, 3: 0, 4: 1, 5: 0, 6: 0}})
        pth = S3Location('newtools-tests').join('generic', 'email_test_copy.parquet')

        fh = PandasDoggo()

        fh.save(df, pth, index=None, compression="snappy")

        pd.testing.assert_frame_equal(fh.load_parquet(pth), df)

        s3 = boto3.resource('s3')
        obj = s3.Object(pth.bucket, pth.key)
        obj.delete()

    def test_cant_guess_format(self):
        fh = PandasDoggo()
        with self.assertRaises(ValueError):
            fh.load('some_text_file')

    def test_invalid_format_detected(self):
        fh = PandasDoggo()
        with self.assertRaises(ValueError):
            fh.load('some_text_file.dat')
        with self.assertRaises(ValueError):
            fh.save(pd.DataFrame(), 'some_text_file.dat')

    def test_invalid_format_passed(self):
        fh = PandasDoggo()
        with self.assertRaises(ValueError):
            fh.load('some_text_file.dat', file_format='bees?')

    def test_whos_a_good_boi_den(self):
        with self.assertRaises(ValueError):
            with FileDoggo('some_path_to_a_file', mode='justusewb', is_s3=True) as f:
                f.write('should have read the docs')


class TestCSVDoggo(unittest.TestCase):
    pass


class TestDoggoFileSystem(BaseTest):

    def _test(self, root):
        dfs = DoggoFileSystem()

        testdir = dfs.join(root, str(random()))

        file_1 = dfs.join(testdir, "temp_1.txt")
        file_2 = dfs.join(testdir, "tests", "temp_2.txt")

        self.assertEqual(dfs.split(file_1), (testdir, "temp_1.txt"))

        self.assertFalse(dfs.exists(file_1))
        self.assertFalse(dfs.exists(file_2))

        with dfs.open(file_1, "wb") as f:
            f.write(b"woof")

        self.assertTrue(dfs.exists(file_1))
        self.assertFalse(dfs.exists(file_2))

        dfs.cp(file_1, file_2)
        self.assertTrue(dfs.exists(file_1))
        self.assertTrue(dfs.exists(file_2))

        paths = dfs.glob(dfs.join(testdir, "**"))
        self.assertIn(file_1, paths)
        self.assertIn(file_2, paths)

        dfs.rm(file_2)
        self.assertTrue(dfs.exists(file_1))
        self.assertFalse(dfs.exists(file_2))

        dfs.mv(file_1, file_2)
        self.assertFalse(dfs.exists(file_1))
        self.assertTrue(dfs.exists(file_2))

        self.assertEqual(dfs.size(file_2), 4)

    def test_ls(self):
        dfs = DoggoFileSystem()
        root = self.test_dir
        testdir = dfs.join(root, str(random()))
        file_1 = dfs.join(testdir, "temp_1.txt")
        dir_local_1 = testdir + '/'
        dir_s3 = S3Location('newtools-tests').join('dfs/')
        if dfs.exists(dir_s3):
            dfs.rm(dir_s3, recursive=True)
        with dfs.open(file_1, "wb") as f:
            f.write(b"woof")

        dfs.cp(dir_local_1, dir_s3)

        contents = dfs.ls(os.path.join(root, 'pandas_doggo_tests/csv'), recursive=True)
        self.assertEqual(len(contents), 4)
        self.assertTrue(any('write_target.csv.gzip' in item for item in contents))
        self.assertTrue(any('test.csv.gz' in item for item in contents))
        self.assertTrue(any('uncompressed.csv' in item for item in contents))
        self.assertTrue(any('email_test.csv' in item for item in contents))

        self.assertEqual(len(dfs.ls(dir_local_1)), 1)
        self.assertTrue('temp_1.txt' in dfs.ls(dir_local_1)[0])

        self.assertEqual(len(dfs.ls('s3://totallyfakelocation')), 0)
        self.assertEqual(len(dfs.ls('s3://totallyfakelocation', recursive=True)), 0)
        self.assertEqual(len(dfs.ls(os.path.join(dir_local_1, 'totallyfakefolder'))), 0)
        self.assertEqual(len(dfs.ls(os.path.join(dir_local_1, 'totallyfakefolder'), recursive=True)), 0)

        self.assertEqual(dfs.ls(dir_s3), [S3Location('s3://newtools-tests/dfs/temp_1.txt')])

        self.assertEqual(dfs.ls(S3Location(dir_s3), recursive=True),
                         [S3Location('s3://newtools-tests/dfs/temp_1.txt')])

    def test_mixed_local_s3(self):
        dfs = DoggoFileSystem()
        root = self.tempdir
        testdir = dfs.join(root, str(random()))

        file_1 = dfs.join(testdir, "temp_1.txt")
        file_2 = dfs.join(testdir, "tests", "temp_2.txt")
        dir_local_1 = testdir + '/'
        dir_local_2 = dfs.join(root, str(random())) + '/'
        dir_s3 = S3Location('newtools-tests').join('dfs2')
        file_3 = dfs.join(dir_local_2, "temp_1.txt")
        file_4 = dfs.join(dir_local_2, "tests", "temp_2.txt")
        s3_loc_1 = S3Location('newtools-tests').join('dfs2', 'temp_1.txt')
        s3_loc_2 = S3Location('newtools-tests').join('dfs2', 'temp_2.txt')
        if dfs.exists(s3_loc_1):
            dfs.rm(s3_loc_1)
        if dfs.exists(s3_loc_2):
            dfs.rm(s3_loc_2)

        with self.assertRaises(FileNotFoundError):
            dfs.cp(s3_loc_1, s3_loc_2)

        with self.assertRaises(FileNotFoundError):
            dfs.mv(s3_loc_1, s3_loc_2)

        self.assertEqual(dfs.split(file_1), (testdir, "temp_1.txt"))

        self.assertFalse(dfs.exists(file_1))
        self.assertFalse(dfs.exists(file_2))

        with dfs.open(file_1, "wb") as f:
            f.write(b"woof")

        self.assertTrue(dfs.exists(file_1))
        self.assertFalse(dfs.exists(file_2))
        self.assertFalse(dfs.exists(file_3))
        self.assertFalse(dfs.exists(file_4))

        dfs.cp(file_1, file_2)
        self.assertTrue(dfs.exists(file_1))
        self.assertTrue(dfs.exists(file_2))
        dfs.cp(dir_local_1, dir_local_2)
        self.assertTrue(dfs.exists(file_1))
        self.assertTrue(dfs.exists(file_2))
        self.assertTrue(dfs.exists(file_3))
        self.assertTrue(dfs.exists(file_4))
        shutil.rmtree(dir_local_2)
        dfs.cp(file_1, s3_loc_1)
        self.assertTrue(dfs.exists(s3_loc_1))
        dfs.cp(s3_loc_1, s3_loc_2)
        self.assertTrue(dfs.exists(s3_loc_2))

        paths = dfs.glob(dfs.join(testdir, "**"))
        self.assertIn(file_1, paths)
        self.assertIn(file_2, paths)

        dfs.rm(file_2)
        self.assertTrue(dfs.exists(file_1))
        self.assertFalse(dfs.exists(file_2))
        dfs.cp(s3_loc_2, file_2)
        self.assertTrue(dfs.exists(file_2))
        dfs.rm(file_2)

        dfs.mv(file_1, file_2)
        self.assertFalse(dfs.exists(file_1))
        self.assertTrue(dfs.exists(file_2))
        dfs.mv(file_2, s3_loc_1)
        self.assertFalse(dfs.exists(file_2))
        self.assertTrue(dfs.exists(s3_loc_1))
        dfs.mv(s3_loc_1, s3_loc_2)
        self.assertFalse(dfs.exists(s3_loc_1))
        self.assertTrue(dfs.exists(s3_loc_2))
        dfs.mv(s3_loc_2, file_1)
        self.assertFalse(dfs.exists(s3_loc_2))
        self.assertTrue(dfs.exists(file_1))

        dfs.mv(dir_local_1, dir_local_2)
        self.assertFalse(dfs.exists(file_1))
        self.assertTrue(dfs.exists(file_3))

        dfs.mv(dir_local_2, dir_s3)
        self.assertFalse(dfs.exists(file_3))
        self.assertTrue(dfs.exists(s3_loc_1))

        if dfs.exists(s3_loc_1):
            dfs.rm(s3_loc_1)
        if dfs.exists(s3_loc_2):
            dfs.rm(s3_loc_2)

    def test_s3(self):
        self._test(S3Location("s3://newtools-tests/07092018pqtest/fs/"))

        dfs = DoggoFileSystem()
        self.assertEqual(dfs.split("s3://newtools-tests/07092018pqtest/temp.txt"),
                         ("s3://newtools-tests/07092018pqtest", "temp.txt"))
        # for full coverage
        self.assertEqual(dfs.split("s3://newtools-tests/temp.txt"),
                         ("s3://newtools-tests/", "temp.txt"))

    def test_file(self):
        self._test(self.tempdir)


class TestDoggoWait(unittest.TestCase):
    def test_basic(self):
        dw = DoggoWait(wait_period=1, time_out_seconds=2)

        with self.assertRaises(ValueError):
            dw.timed_out()

        dw.start_timeout()
        self.assertEqual(dw.timed_out(), False)
        dw.check_timeout()
        dw.wait()
        with self.assertRaises(TimeoutError):
            dw.check_timeout()


def check_lock(file):
    test_str = str(random())
    with DoggoLock(file, wait_period=0.1, time_out_seconds=20, maximum_age=30):
        with FileDoggo(file, "wb") as f:
            f.write(test_str.encode('UTF-8'))

        with FileDoggo(file, "rb") as f:
            assert f.read().decode('UTF-8') == test_str

        sleep(0.1)

    return True

class BaseLockTest(BaseTest):
    LockClass = None

    def test_lock_timeout(self):
        if self.LockClass is not None:
            file = os.path.join(self.tempdir, f'test_lock_timeout.{random()}tmp')
            with self.LockClass(file, wait_period=1, time_out_seconds=5, maximum_age=20):
                sleep(0.1)
                with self.assertRaises(TimeoutError):
                    with self.LockClass(file, wait_period=1, time_out_seconds=2, maximum_age=20):
                        pass

    def test_basic(self):
        if self.LockClass is not None:
            file = os.path.join(self.tempdir, f'test_basic.{random()}.tmp')
            check_lock(file)
            check_lock(file)

    def test_lock_ages(self):
        if self.LockClass is not None:
            file = os.path.join(self.tempdir, f'test_lock_ages.{random()}.tmp')
            lock_1 = self.LockClass(file, wait_period=1, time_out_seconds=2, maximum_age=10)
            lock_2 = self.LockClass(file, wait_period=1, time_out_seconds=2, maximum_age=10)

            lock_1.acquire()
            sleep(0.1)

            with self.assertRaises(TimeoutError):
                lock_2.acquire()

            sleep(10)

            lock_2.acquire()

            lock_1.release()
            lock_2.release()


class TestDoggoLockS3(BaseLockTest):
    tempdir = 's3://newtools-tests/locks/'
    LockClass = DoggoLock


class TestDoggoLockLocal(BaseLockTest):
    LockClass = DoggoLock

    def test_lock_multiprocess(self):
        if self.LockClass is not None:
            file = os.path.join(self.tempdir, f'test_lock_multiprocess.{random()}.tmp')

            processes=list()
            pool = multiprocessing.Pool()
            for _ in range(0, min(10, multiprocessing.cpu_count() -1)):
                processes.append(
                    pool.apply_async(check_lock,
                                     (file,))
                )

            pool.close()
            pool.join()

            self.assertTrue(all([x.get() for x in processes]))


class TestDynamoDogLock(BaseLockTest):
    LockClass = DynamoDogLock

    def test_lock_create_dynamo_table(self):
        boto3.resource("dynamodb", region_name="us-east-1").Table(DynamoDogLock._table_name).delete()
        waiter = boto3.client("dynamodb", region_name="us-east-1").get_waiter('table_not_exists')
        waiter.wait(TableName=DynamoDogLock._table_name,
                    WaiterConfig={'Delay': 2, 'MaxAttempts': 120})

        file = os.path.join(self.tempdir, 'test_lock_ages.tmp')
        with self.LockClass(file, wait_period=1, time_out_seconds=2, maximum_age=5):
            pass


class TestPartitionDoggo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pd.DataFrame({"col1": [1, 2, 3, 4, 5, 1, "4", 3, 4, "4", "4", 4, 2, 3, "4"],
                               "col2": [6, 7, 8, 9, 10, 5, 6, 7, 5, "10", 7, 6, 8, 7, 6],
                               "col3": [11, 12, 13, 14, 15, "a", "b", "y", 1, 3, 15, 66, 77, 13, 16],
                               "col4": ["sda", "", 16, "17", 18, "14", 12, 13, 14, 5, 6, 45, 34, 76, 87]}).astype(
            {"col4": str, "col2": int, "col3": str})
        try:
            os.mkdir(os.path.join(os.path.dirname(__file__), "test_data/athena_partition/output"))
        except FileExistsError:
            pass
        cls.base_path = os.path.join(os.path.dirname(__file__), "test_data/athena_partition/output")

    def test_csv_out(self):
        expected_data = os.path.join(os.path.dirname(__file__), "test_data/athena_partition/expected_csv.csv")
        for file in os.listdir(self.base_path):
            if not file.startswith('.'):
                file_path = os.path.join(self.base_path, file)
                shutil.rmtree(file_path)

        partition_cat = ["col1"]
        cols_keep = ["col2", "col4"]
        output_data_path = os.path.join(self.base_path, "col1=4")
        PandasDoggo().save_partitioned(df=self.df[partition_cat + cols_keep].astype(dict(zip(partition_cat, [int]))),
                                       partition_columns=partition_cat,
                                       base_path=self.base_path,
                                       name="/test_name_",
                                       suffix=".csv",
                                       index=False)
        self.assertEqual(1, len([name for name in os.listdir(output_data_path)]))
        csv = CSVDoggo()
        expected = csv.load_df(expected_data)
        output = csv.load_df(os.path.join(output_data_path, *os.listdir(output_data_path)))

        assert_frame_equal(expected, output, check_like=True)

        for file in os.listdir(self.base_path):
            if not file.startswith('.'):
                file_path = os.path.join(self.base_path, file)
                shutil.rmtree(file_path)

    def test_pq_out(self):
        expected_data = os.path.join(os.path.dirname(__file__), "test_data/athena_partition/expected_parquet.parquet")
        for file in os.listdir(self.base_path):
            if not file.startswith('.'):
                file_path = os.path.join(self.base_path, file)
                shutil.rmtree(file_path)

        partition_cat = ["col1"]
        cols_keep = ["col2", "col4"]
        output_data_path = os.path.join(self.base_path, "col1=4")
        PandasDoggo().save_partitioned(df=self.df[partition_cat + cols_keep].astype(dict(zip(partition_cat, [int]))),
                                       partition_columns=partition_cat,
                                       base_path=self.base_path,
                                       name="/test_name_",
                                       suffix=".parquet",
                                       index=False)

        dog = PandasDoggo()
        expected = dog.load_parquet(expected_data)
        output = dog.load_parquet(os.path.join(output_data_path, *os.listdir(output_data_path)))
        assert_frame_equal(expected, output, check_like=True)

        for file in os.listdir(self.base_path):
            if not file.startswith('.'):
                file_path = os.path.join(self.base_path, file)
                shutil.rmtree(file_path)

    def test_multi_part(self):
        expected_data = os.path.join(os.path.dirname(__file__), "test_data/athena_partition/expected_multi_csv.csv")
        for file in os.listdir(self.base_path):
            if not file.startswith('.'):
                file_path = os.path.join(self.base_path, file)
                shutil.rmtree(file_path)

        csv = CSVDoggo(base_path=self.base_path)
        partition_cat = ["col1", "col2"]
        output_data_path = os.path.join(self.base_path, "col1=4/col2=6")
        PandasDoggo().save_partitioned(df=self.df.astype(dict(zip(partition_cat, [int, int]))),
                                       partition_columns=partition_cat,
                                       base_path=self.base_path,
                                       name="/test_name_",
                                       suffix=".parquet",
                                       index=False)

        self.assertEqual(5, len([name for name in os.listdir(os.path.join(self.base_path, "col1=4"))]))
        dog = PandasDoggo()
        expected = dog.load(expected_data, dtype=object)
        output = dog.load(os.path.join(output_data_path, *os.listdir(output_data_path)))

        assert_frame_equal(expected, output, check_like=True)

        for file in os.listdir(self.base_path):
            if not file.startswith('.'):
                file_path = os.path.join(self.base_path, file)
                shutil.rmtree(file_path)

    def test_expected_errors(self):

        with self.assertRaises(ValueError):
            PandasDoggo().save_partitioned(df=self.df.astype(dict(zip(["col4"], [int, int]))),
                                           partition_columns=["col4"],
                                           base_path=self.base_path,
                                           name="/test_name_",
                                           suffix=".parquet",
                                           index=False)

        with self.assertRaises(KeyError):
            PandasDoggo().save_partitioned(df=self.df.astype(dict(zip(["col1", "col7"], [int, int]))),
                                           partition_columns=["col1"],
                                           base_path=self.base_path,
                                           name="/test_name_",
                                           suffix=".parquet",
                                           index=False)

        with self.assertRaises(ValueError):
            PandasDoggo().save_partitioned(df=self.df.astype(dict(zip(["col3"], [int, int]))),
                                           partition_columns=["col3"],
                                           base_path=self.base_path,
                                           name="/test_name_",
                                           suffix=".parquet",
                                           index=False)


class TestDoggoFileSystem_2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data', 'doggofilesystem_tests')
        cls.bucket = "newtools-tests"
        cls.prefix = 'doggofilesystem_tests'
        cls.path = S3Location(bucket=cls.bucket, key=cls.prefix)
        cls.dfs = DoggoFileSystem()
        cls.file_list = [
            'doggofilesystem_tests/limit_test/test1.txt',
            'doggofilesystem_tests/pixel/source_partition=pix.pub/date=2019-01-01/l_tag=dativa-health-check/2019-01-01_094118.631787.parquet',
            'doggofilesystem_tests/pixel/source_partition=pix.pub/date=2019-01-01/l_tag=food-network-kitchen-app-across-channel/2019-01-01_094117.723581.parquet',
            'doggofilesystem_tests/pixel/source_partition=pixels.dativa.com/date=2021-01-01/l_tag=dativa-health-check/2021-01-01_094118.631787.parquet',
            'doggofilesystem_tests/pixel/source_partition=pixels.dativa.com/date=2021-01-01/l_tag=food-network-kitchen-app-across-channel/2021-01-01_094117.723581.parquet',
            'doggofilesystem_tests/test1.txt']

    @classmethod
    def tearDownClass(cls):
        cls.dfs._delete_files(bucket=cls.bucket, prefix=cls.prefix)

    def test_list(self):
        self.dfs._put_folder(source=self.base_path, bucket=self.bucket, destination=self.prefix)
        self.assertListEqual(self.file_list, self.dfs._list(self.path))
        self.assertEqual(len(self.file_list), len(self.dfs._list(self.path)))
        assert self.file_list[1] + f'{random()}' not in self.dfs._list(self.path)

    def test_file_in_list_files(self):
        self.dfs._put_folder(source=self.base_path, bucket=self.bucket, destination=self.prefix)
        self.assertEqual(self.file_list, self.dfs._list_files(bucket=self.bucket, prefix=self.prefix))

    def test_list_dict(self):
        self.dfs._put_folder(source=self.base_path, bucket=self.bucket, destination=self.prefix)
        self.files_on_s3 = [file['key'] for file in self.dfs._list_dict(path=self.path)]
        self.assertEqual(self.file_list, self.files_on_s3)

    def test_put_folder(self):
        with self.assertRaises(ValueError):
            self.dfs._put_folder(source=self.base_path + f'{random()}', bucket=self.bucket, destination=self.prefix)

    def test_delete_one_file(self):
        self.dfs._put_folder(source=self.base_path, bucket=self.bucket, destination=self.prefix)
        self.dfs._delete_files(bucket=self.bucket, prefix=self.file_list[0])
        self.assertEqual(self.file_list[1:], self.dfs._list_files(bucket=self.bucket, prefix=self.prefix))
        with self.assertRaises(Exception):
            self.dfs._delete_files(bucket=self.bucket + f'{random()}', prefix=self.file_list[1])

    def test_delete_folders(self):
        self.dfs._put_folder(source=self.base_path, bucket=self.bucket, destination=self.prefix)
        self.dfs._delete(path=self.path)
        self.assertEqual([], self.dfs._list_files(bucket=self.bucket, prefix=self.prefix))

    def test_upper_limit(self):
        for item in range(1002):
            source = self.base_path + '/limit_test/'
            prefix = self.prefix + f'/{item}/'
            self.dfs._put_folder(source=source, bucket=self.bucket, destination=prefix)
        self.assertEqual(self.dfs._list(path=self.path), self.dfs._list_files(bucket=self.bucket, prefix=self.prefix))
        self.dfs._delete(path=self.path)
        self.assertEqual([], self.dfs._list(path=self.path))

    def test_ls(self):
        all_files_in_bucket = self.dfs.ls(location=S3Location(bucket=self.bucket, key=None), recursive=True)
        files_no_key_bucket = self.dfs.ls(location=S3Location(bucket=self.bucket), recursive=True)
        self.assertEqual(all_files_in_bucket, files_no_key_bucket)

        self.assertEqual(self.dfs.ls(location=f's3://{random()}/'), [])
        self.assertEqual(self.dfs.ls(location=f's3://{self.bucket}/{random()}/'), [])

        self.assertEqual(len(self.dfs.ls(self.base_path, recursive=True)), len(self.file_list))
        self.assertEqual(self.dfs.ls(self.base_path + f'/{random()}/', recursive=True), [])

        self.assertEqual(len(self.dfs.ls(self.base_path)), 3)
        self.assertEqual(len(self.dfs.ls(self.base_path + f"{random()}")), 0)

