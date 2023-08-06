# (c) Deductive 2012-2020, all rights reserved
# This code is licensed under MIT license (see license.txt for details)

import sqlite3
import os
from time import time, sleep
import pandas as pd
from datetime import datetime, timedelta

from .base_test import BaseTest
from newtools import CachedPep249Query, CachedAthenaQuery, BaseCachedQuery, PandasDoggo, DoggoFileSystem, log_to_stdout

log_to_stdout("newtools")


class TestCachedQuery(BaseTest):
    region = "us-west-2"
    athena_db_name = "sampledb"

    @classmethod
    def setUpClass(cls):
        cls.s3_bucket = "s3://newtools-tests/query-results/{0}/".format(time())
        super(TestCachedQuery, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        dfs = DoggoFileSystem()
        for file in dfs.glob(cls.s3_bucket + "**"):
            dfs.rm(file)
        super(TestCachedQuery, cls).tearDownClass()

    def setUp(self):
        self.sqlite_db = sqlite3.connect(os.path.join(self.test_dir, "query_tests", "test.sqlite"))
        self.sql_path = os.path.join(self.test_dir, "query_tests")
        super(TestCachedQuery, self).setUp()

    @staticmethod
    def set_timeouts(q):
        q.wait_period = 0
        q.time_out_seconds = 1
        q.maximum_age = 120

    def test_bad_path_pep249(self):
        q = CachedPep249Query(self.sqlite_db,
                              cache_path=self.tempdir,
                              sql_paths=[self.sql_path],
                              gzip=False)
        self.set_timeouts(q)

        with self.assertRaises(ValueError):
            q.get_results(sql_file="bad_query.sql",
                          output_prefix="test_query",
                          )

    def test_log_pep249(self):
        q = CachedPep249Query(self.sqlite_db,
                              cache_path=self.tempdir,
                              sql_paths=[self.sql_path],
                              gzip=False)
        self.set_timeouts(q)

        with self.assertLogs("newtools.cached_query", level="INFO") as cm:
            q.get_results(sql_file="test_select.sql",
                          output_prefix="test_query_1_row",
                          params={
                              "secret": "my secret"
                          }
                          )

        self.assertIn('INFO:newtools.cached_query:secret = *********', cm.output)

    def test_log_pep249_string_path(self):
        q = CachedPep249Query(self.sqlite_db,
                              cache_path=self.tempdir,
                              sql_paths=self.sql_path,
                              gzip=False)
        self.set_timeouts(q)

        with self.assertLogs("newtools.cached_query", level="INFO") as cm:
            q.get_results(sql_file="test_select.sql",
                          output_prefix="test_query_1_row",
                          params={
                              "secret": "my secret"
                          }
                          )

        self.assertIn('INFO:newtools.cached_query:secret = *********', cm.output)

    def test_cache_pep249(self):
        q = CachedPep249Query(self.sqlite_db,
                              cache_path=self.tempdir,
                              sql_paths=[self.sql_path],
                              gzip=False)
        self.set_timeouts(q)

        a = q.get_results(sql_file="test_select.sql",
                          output_prefix="test_query",
                          )

        # rerun the get_results to get full coverage
        a1 = q.get_results(sql_file="test_select.sql",
                           output_prefix="test_query",
                          )
        self.assertEqual(a, a1)

        # Validate the results still work without a database connection
        q2 = BaseCachedQuery(cache_path=self.tempdir,
                             sql_paths=[self.sql_path],
                             gzip=False)
        self.set_timeouts(q2)

        b = q2.get_results(sql_file="test_select.sql",
                           output_prefix="test_query",
                           )

        # Now clear the cache and check it doesn't work
        q.clear_cache(sql_file="test_select.sql",
                      output_prefix="test_query")

        with self.assertRaisesRegex(NotImplementedError, "BaseCachedClass cannot execute queries"):
            q2.get_results(sql_file="test_select.sql",
                           output_prefix="test_query",
                           )

        self.assertEqual(a, b)

    def test_query_expiring_cache(self):
        q = CachedPep249Query(self.sqlite_db,
                              cache_path=self.tempdir,
                              sql_paths=[self.sql_path],
                              expiry_seconds=3,
                              gzip=False)
        self.set_timeouts(q)

        # get to the point where a new three-second period has started...
        if int(int(time())) % 3 == 1:
            sleep(1)

        path1 = q.get_results(sql_file="test_select.sql",
                              output_prefix="test_query",
                              )

        path2 = q.get_results(sql_file="test_select.sql",
                              output_prefix="test_query",
                              )
        sleep(3)

        path3 = q.get_results(sql_file="test_select.sql",
                              output_prefix="test_query",
                              )

        # Check the two queries run in the same period use the same path
        self.assertEqual(path1, path2)

        # Check the second query returns a different path
        self.assertNotEqual(path1, path3)

    def test_query_pep249(self):
        q = CachedPep249Query(self.sqlite_db,
                              cache_path=self.tempdir,
                              sql_paths=[self.sql_path],
                              gzip=False)
        self.set_timeouts(q)

        q.get_results(sql_file="test_select.sql",
                      output_prefix="test_query",
                      )

        q.get_results(sql_file="test_select_in.sql",
                      output_prefix="test_query_1_row",
                      params={
                          "test_value": 2
                      }
                      )

        q.get_results(sql_file="test_select_in.sql",
                      output_prefix="test_query_0_rows",
                      params={
                          "test_value": 1
                      }
                      )

        self.compare_files(os.path.join(self.test_dir, "query_tests", "output"))

    def test_query__new_archive_path_pep249(self):
        q = CachedPep249Query(self.sqlite_db,
                              cache_path=self.tempdir,
                              sql_paths=[self.sql_path],
                              params={"sql_archive_path": os.path.join(self.tempdir, "new")},
                              gzip=False)
        self.set_timeouts(q)

        q.get_results(sql_file="test_select.sql",
                      output_prefix="test_query"
                      )

    def test_1_row_as_param_to_obj_pep249(self):
        q = CachedPep249Query(self.sqlite_db,
                              params={
                                  "test_value": 2
                              },
                              cache_path=self.tempdir,
                              sql_paths=[self.sql_path],
                              gzip=False)
        self.set_timeouts(q)

        q.get_results(sql_file="test_select_in.sql",
                      output_prefix="test_query_1_row",
                      )

        self.compare_files(os.path.join(self.test_dir, "query_tests", "output"))

    def test_with_s3_path_pep249(self):
        # note we don't explicitly test using Redshift as we don't have one available for testing
        q = CachedPep249Query(self.sqlite_db,
                              cache_path=self.tempdir,
                              sql_paths=[self.sql_path],
                              gzip=False)
        self.set_timeouts(q)

        q.get_results(sql_file="test_select_s3_path.sql",
                      output_prefix="test_query_0_rows",
                      params={
                          "s3_path": 1
                      }
                      )

        self.compare_files(os.path.join(self.test_dir, "query_tests", "output"))

    def test_archive_queries_pep249(self):
        q = CachedPep249Query(self.sqlite_db,
                              cache_path=self.tempdir,
                              sql_paths=[self.sql_path],
                              sql_archive_path=self.tempdir,
                              gzip=False)
        self.set_timeouts(q)

        q.get_results(sql_file="test_select.sql",
                      output_prefix="test_query",
                      )

        query = open(os.path.join(self.tempdir, "test_select.sql")).read()

        self.assertIn("-- Ran query on:", query)
        self.assertIn("-- Parameters: {}", query)
        self.assertIn("SELECT * FROM test;", query)

    def test_athena(self):

        q = CachedAthenaQuery(params={"aws_region": self.region,
                                      "athena_db": self.athena_db_name},
                              cache_path=self.s3_bucket,
                              sql_paths=[self.sql_path],
                              sql_archive_path=self.tempdir)
        self.set_timeouts(q)

        days = [datetime.utcnow() - timedelta(days=1),
                datetime.utcnow(),
                datetime.utcnow() + timedelta(days=1)]

        # Get the results, refreshing the cache
        r = q.get_results(sql_file="athena_test.sql",
                          output_prefix="athena_test",
                          params={"day_list": ['{0:%Y-%m-%d}'.format(day) for day in days]},
                          refresh_cache=True)

        # Get the output
        output = PandasDoggo().load_csv(r, compression="gzip")

        # Clear the cache again
        q.clear_cache(sql_file="athena_test.sql",
                      output_prefix="athena_test",
                      params={"day_list": ['{0:%Y-%m-%d}'.format(day) for day in days]})
        self.assertFalse(q._exists(r))

        # check can still read in validation mode
        q.validation_mode = True
        s = q.get_results(sql_file="athena_test.sql",
                          output_prefix="athena_test",
                          params={"day_list": ['{0:%Y-%m-%d}'.format(day) for day in days]})
        self.assertEqual(s, r)

        # check the archive.
        file = DoggoFileSystem().glob(os.path.join(self.tempdir, "athena_test*.sql"))[0]
        query = open(file).read()

        self.assertIn("-- Ran query on:", query)
        self.assertIn("-- Parameters: {'aws_region': 'us-west-2'", query)
        self.assertIn("SELECT current_date as dt, CAST(current_date as varchar) as day)", query)

        # check the results
        self.assertEqual(output.to_csv(index=False),
                         'dt,day\n{0:%Y-%m-%d},{0:%Y-%m-%d}\n'.format(datetime.utcnow()))

    def test_athena_replacement_dict(self):

        q = CachedAthenaQuery(params={"aws_region": self.region,
                                      "athena_db": self.athena_db_name},
                              cache_path=self.s3_bucket,
                              sql_paths=[self.sql_path], )
        self.set_timeouts(q)

        days = [datetime.utcnow() - timedelta(days=1),
                datetime.utcnow(),
                datetime.utcnow() + timedelta(days=1)]

        r = q.get_results(sql_file="athena_test.sql",
                          output_prefix="athena_test",
                          replacement_dict={
                              "{day_list}": "(" + ",".join(["'{0:%Y-%m-%d}'".format(day) for day in days]) + ")"})

        # Get the output
        output = PandasDoggo().load_csv(r, compression="gzip")

        # check the results
        self.assertEqual(output.to_csv(index=False),
                         'dt,day\n{0:%Y-%m-%d},{0:%Y-%m-%d}\n'.format(datetime.utcnow()))

    def test_s3_archive(self):

        q = CachedAthenaQuery(params={"aws_region": self.region,
                                      "athena_db": self.athena_db_name},
                              cache_path=self.s3_bucket,
                              sql_paths=[self.sql_path],
                              sql_archive_path=self.s3_bucket)
        self.set_timeouts(q)

        # use a list of length one
        days = [datetime.utcnow()]

        q.clear_cache(sql_file="athena_test.sql",
                      output_prefix="athena_test",
                      params={"day_list": ['{0:%Y-%m-%d}'.format(day) for day in days]})
        try:
            DoggoFileSystem().rm(os.path.join(self.s3_bucket, "athena_test.sql"))
        except FileNotFoundError:
            pass

        q.get_results(sql_file="athena_test.sql",
                      output_prefix="athena_test",
                      params={"day_list": ['{0:%Y-%m-%d}'.format(day) for day in days]})

        # check the archive.
        file = DoggoFileSystem().glob(os.path.join(self.s3_bucket, "athena_test*.sql"))[0]
        with DoggoFileSystem().open(file, "rb") as f:
            query = f.read().decode("UTF-8")

        self.assertIn("-- Ran query on:", query)
        self.assertIn("-- Parameters: {'aws_region': 'us-west-2'", query)
        self.assertIn("SELECT current_date as dt, CAST(current_date as varchar) as day)", query)

    def test_renaming_output_file(self):
        class MimicRedshiftQuery(CachedAthenaQuery):
            """
            Create a class that mimic's redshift's annoying functionality of producing differently named files
            """
            _redshift_checks = True

            def _execute_query(self,
                               query_file,
                               output_file,
                               query_parameters,
                               replacement_dict):
                return super(MimicRedshiftQuery, self)._execute_query(
                    query_file=query_file,
                    output_file=output_file + "000.gz",
                    query_parameters=query_parameters,
                    replacement_dict=replacement_dict
                )

        q = MimicRedshiftQuery(params={"aws_region": self.region,
                                       "athena_db": self.athena_db_name},
                               cache_path=self.s3_bucket,
                               sql_paths=[self.sql_path], )
        self.set_timeouts(q)

        days = [datetime.utcnow() - timedelta(days=1),
                datetime.utcnow(),
                datetime.utcnow() + timedelta(days=1)]

        r = q.get_results(sql_file="athena_test.sql",
                          output_prefix="athena_test",
                          replacement_dict={
                              "{day_list}": "(" + ",".join(["'{0:%Y-%m-%d}'".format(day) for day in days]) + ")"},
                          refresh_cache=True)

        # Get the output
        output = PandasDoggo().load_csv(r, compression="gzip")

        # check the results
        self.assertEqual(output.to_csv(index=False),
                         'dt,day\n{0:%Y-%m-%d},{0:%Y-%m-%d}\n'.format(datetime.utcnow()))

    def test_multiple_output_file(self):
        class MimicRedshiftQueryMultiple(CachedAthenaQuery):
            """
            Create a class that mimic's redshift upload multiple files
            """
            _redshift_checks = True

            def _execute_query(self,
                               query_file,
                               output_file,
                               query_parameters,
                               replacement_dict):
                a = super(MimicRedshiftQueryMultiple, self)._execute_query(
                    query_file=query_file,
                    output_file=output_file + "000.gz",
                    query_parameters=query_parameters,
                    replacement_dict=replacement_dict
                )

                DoggoFileSystem().cp(output_file + "000.gz", output_file + "001.gz")

                return a

        q = MimicRedshiftQueryMultiple(params={"aws_region": self.region,
                                               "athena_db": self.athena_db_name, },
                                       cache_path=self.s3_bucket,
                                       sql_paths=[self.sql_path], )
        self.set_timeouts(q)

        days = [datetime.utcnow()]

        q.clear_cache(sql_file="athena_test.sql",
                      output_prefix="athena_test",
                      replacement_dict={
                          "{day_list}": "(" + ",".join(["'{0:%Y-%m-%d}'".format(day) for day in days]) + ")"})

        r = q.get_results(sql_file="athena_test.sql",
                          output_prefix="athena_test",
                          replacement_dict={
                              "{day_list}": "(" + ",".join(["'{0:%Y-%m-%d}'".format(day) for day in days]) + ")"})

        # Get the output
        output = PandasDoggo().load_csv(r, compression="gzip")

        # check the results (should have double results)
        self.assertEqual(output.to_csv(index=False),
                         'dt,day\n{0:%Y-%m-%d},{0:%Y-%m-%d}\n{0:%Y-%m-%d},{0:%Y-%m-%d}\n'.format(datetime.utcnow()))

    def test_no_output_file(self):
        class MimicRedshiftQueryNone(CachedAthenaQuery):
            """
            Create a class that mimic's redshift upload multiple files
            """
            _redshift_checks = True

            def _execute_query(self,
                               query_file,
                               output_file,
                               query_parameters,
                               replacement_dict):
                a = super(MimicRedshiftQueryNone, self)._execute_query(
                    query_file=query_file,
                    output_file=output_file,
                    query_parameters=query_parameters,
                    replacement_dict=replacement_dict
                )

                DoggoFileSystem().rm(output_file)

                return a

        q = MimicRedshiftQueryNone(params={"aws_region": self.region,
                                           "athena_db": self.athena_db_name},
                                   cache_path=self.s3_bucket,
                                   sql_paths=[self.sql_path], )
        self.set_timeouts(q)

        days = [datetime.utcnow()]

        q.clear_cache(sql_file="athena_test.sql",
                      output_prefix="athena_test",
                      replacement_dict={
                          "{day_list}": "(" + ",".join(["'{0:%Y-%m-%d}'".format(day) for day in days]) + ")"})
        with self.assertRaisesRegex(ValueError,
                                    "No file returned by the query. Does it contain an UNLOAD command?"):
            q.get_results(sql_file="athena_test.sql",
                          output_prefix="athena_test",
                          replacement_dict={
                              "{day_list}": "(" + ",".join(["'{0:%Y-%m-%d}'".format(day) for day in days]) + ")"})

    def test_unescaped_percent(self):
        q = CachedPep249Query(self.sqlite_db,
                              cache_path=self.tempdir,
                              sql_paths=[self.sql_path],
                              sql_archive_path=self.tempdir,
                              gzip=False)
        self.set_timeouts(q)

        with self.assertRaisesRegex(ValueError, "contains unescaped % signs that will not run"):
            q.get_results(sql_file="test_select_bad.sql",
                          output_prefix="test_query",
                          )

    def test_athena_queue(self):

        q = CachedAthenaQuery(params={"aws_region": self.region,
                                      "athena_db": self.athena_db_name},
                              cache_path=self.s3_bucket,
                              sql_paths=[self.sql_path],
                              sql_archive_path=self.tempdir,
                              queue_queries=True)
        self.set_timeouts(q)

        days = [datetime.utcnow() - timedelta(days=1),
                datetime.utcnow(),
                datetime.utcnow() + timedelta(days=1)]

        # Clear any previously cached file
        r1 = q.get_results(sql_file="athena_test.sql",
                           output_prefix="athena_test",
                           params={"day_list": ['{0:%Y-%m-%d}'.format(day) for day in days]},
                           refresh_cache=True)

        r2 = q.get_results(sql_file="athena_test.sql",
                           output_prefix="athena_test",
                           params={"day_list": ['{0:%Y-%m-%d}'.format(day) for day in days]})

        r3 = q.get_results(sql_file="athena_test.sql",
                           output_prefix="athena_test",
                           params={"day_list": ['{0:%Y-%m-%d}'.format(day) for day in days[:2]]})

        q.wait_for_completion()

        self.assertEqual(r1, r2)
        dfs = DoggoFileSystem()
        self.assertTrue(dfs.exists(r1))
        self.assertTrue(dfs.exists(r2))
        self.assertTrue(dfs.exists(r3))

    def test_concatenating_files(self):
        q2 = BaseCachedQuery(cache_path=self.tempdir,
                             sql_paths=[self.sql_path],
                             gzip=True)
        output_file = os.path.join(self.tempdir, 'part.csv.gz')
        files = [os.path.join(self.test_dir, 'concatenating_files', e) for e in ['part1.csv.gz', 'part2.csv.gz']]
        pg = PandasDoggo()
        # read raw data before being deleted
        df_raw = pd.concat([pg.load_csv(file, compression='gzip') for file in files])
        q2._concatenate_files(output_file=output_file,
                              files=files,
                              deleting_files=False)
        df_new = pg.load_csv(output_file)
        self.assertEqual(df_raw.col1.sum(), df_new.col1.sum())

