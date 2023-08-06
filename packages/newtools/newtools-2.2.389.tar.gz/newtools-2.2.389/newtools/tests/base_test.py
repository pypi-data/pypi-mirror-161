# (c) Deductive 2012-2020, all rights reserved
# This code is licensed under MIT license (see license.txt for details)
import os
import shutil
import glob
from unittest import TestCase
from newtools.optional_imports import pandas as pd
from newtools.optional_imports import s3fs
from newtools import optional_imports, DoggoFileSystem, S3Location


class BaseTest(TestCase):
    """
    A basic test class that compares the existence of files in different locations
    """
    create_test_data = False
    test_dir = os.path.join(os.path.dirname(__file__), "test_data")
    tempdir = os.path.join(test_dir, "temp")

    def setUp(self):
        try:
            pd.set_option("display.max_rows", 100, "display.max_columns", 100)
        except ImportError:
            pass

        try:
            if not self.tempdir.startswith("s3://"):
                os.makedirs(self.tempdir)
        except FileExistsError:
            self.tearDown()
            self.setUp()

    def tearDown(self):
        if not self.tempdir.startswith("s3://"):
            shutil.rmtree(self.tempdir, )

    def compare_file(self, actual, expected):
        print(actual)
        if self.create_test_data:
            shutil.copyfile(actual, expected)

        with open(expected) as expected_file:
            with open(actual, "r") as actual_file:
                self.assertEqual(expected_file.readlines(),
                                 actual_file.readlines(),
                                 "actual file(right) is not as expected (left)")

    def compare_files(self, expected_path):
        for file in glob.glob(os.path.join(self.tempdir, "*")):

            if file.endswith(".gz"):
                old_file = file
                file = file.replace(".gz", "")
                import gzip
                with gzip.open(old_file, "rb") as f_in:
                    with open(file, "wb") as f_out:
                        f_out.write(f_in.read())

            self.compare_file(file, os.path.join(expected_path, os.path.split(file)[1]))


class TestBase(BaseTest):
    """
    Get full coverage by testing the error cases on the optional imports. The actual tests themselves wouldn't run
    if these didn't work

    """

    def test_import_retry(self):
        @optional_imports.AWSRetry.backoff()
        def banana():
            pass

        banana()

    def test_dummy_awsretry(self):
        @optional_imports.DummyAWSRetry.backoff()
        def apple():
            pass

        apple()

    def test_never_imports(self):
        optional_imports.NEVER_IMPORT = True

        my_s3fs = optional_imports.get_s3fs()
        with self.assertRaisesRegex(ImportError, "s3fs is not installed. Failed getting S3FileSystem()"):
            my_s3fs.S3FileSystem.read_timeout = 600

        with self.assertRaisesRegex(ImportError, "s3fs is not installed. Failed calling s3fs()"):
            my_s3fs()(1, 2, 3)

        optional_imports.NEVER_IMPORT = False

        self.assertEqual(optional_imports.get_s3fs(), s3fs)
