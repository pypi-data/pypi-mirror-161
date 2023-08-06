import unittest
from newtools.aws import LoadPartitions, S3List
from newtools.db import AthenaClient


class TestLoadPartitions(unittest.TestCase):
    bucket = "newtools-tests"
    tablename = "load_partition_test_data"
    region = "us-west-2"
    prefix = "load_partition_test_data/"
    database = "test_db"
    output_location = "s3://newtools-tests/query_results/"
    source_file = "s3://newtools-tests/load_partition_test_data/"
    athena_client = None

    @classmethod
    def setUpClass(cls):
        cls.s3_list_folders = S3List(cls.bucket)
        cls.load_partitions = LoadPartitions(cls.bucket)
        cls.athena_client = AthenaClient(region=cls.region, db=cls.database, max_retries=2)

        cls.athena_client.add_query(
            f"""
            CREATE EXTERNAL TABLE IF NOT EXISTS {cls.tablename}(
                col1 string,
                col2 string,
                col3 string)
            PARTITIONED BY (year string, month string)
            ROW FORMAT SERDE
                'org.apache.hadoop.hive.serde2.OpenCSVSerde'
            STORED AS INPUTFORMAT
                'org.apache.hadoop.mapred.TextInputFormat'
            OUTPUTFORMAT
                'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
            LOCATION
                '{cls.source_file}'
            TBLPROPERTIES ('skip.header.line.count'='1')
            ;""", output_location=cls.output_location)

        cls.athena_client.add_query(
            f"""
            ALTER TABLE {cls.tablename} ADD IF NOT EXISTS 
                PARTITION (year='2019', month='02') LOCATION '{cls.source_file}year=2019/month=02/'
                PARTITION (year='2019', month='0:2') LOCATION '{cls.source_file}year=2019/month=0:2/'
                PARTITION (year='2020', month='01') LOCATION '{cls.source_file}year=2020/month=01/'

            ;""", output_location=cls.output_location)

        cls.athena_client.wait_for_completion()

    @classmethod
    def tearDownClass(cls):
        cls.athena_client.add_query(f"DROP TABLE {cls.tablename}", output_location=cls.output_location)
        cls.athena_client.wait_for_completion()

    def test_list_folder(self):
        folders = {'load_partition_test_data/year=2019/', 'load_partition_test_data/year=2020/'}
        test_folders = self.s3_list_folders.list_folders(self.prefix)
        self.assertCountEqual(folders, test_folders)

    def test_list_partitions(self):
        partitions_list = {'load_partition_test_data/year=2019/month=02/some_more_directory/',
                           'load_partition_test_data/year=2019/month=0:2/some_more_directory/',
                           'load_partition_test_data/year=2020/month=01/some_more_directory/',
                           'load_partition_test_data/year=2020/month=01/some_more_directory_1/',
                           'load_partition_test_data/year=2020/month=02/some_more_directory/'}
        test_partitions_list = self.load_partitions.list_partitions('load_partition_test_data')
        self.assertCountEqual(partitions_list, test_partitions_list)

    def test_list_partitions_error(self):
        with self.assertRaises(ValueError):
            self.load_partitions.list_partitions()

    def test_list_partiton_empty(self):
        s3_path = 'never_exist_folder'
        self.assertEqual(self.load_partitions.list_partitions(s3_path=s3_path), set())

    def test_get_sql(self):
        sql_query_list = [
            "ALTER TABLE load_partition_test_data ADD IF NOT EXISTS PARTITION(year='2019',month='02') LOCATION 's3://newtools-tests/load_partition_test_data/year=2019/month=02/some_more_directory/' PARTITION(year='2019',month='0:2') LOCATION 's3://newtools-tests/load_partition_test_data/year=2019/month=0:2/some_more_directory/' PARTITION(year='2020',month='01') LOCATION 's3://newtools-tests/load_partition_test_data/year=2020/month=01/some_more_directory/' PARTITION(year='2020',month='01') LOCATION 's3://newtools-tests/load_partition_test_data/year=2020/month=01/some_more_directory_1/' PARTITION(year='2020',month='02') LOCATION 's3://newtools-tests/load_partition_test_data/year=2020/month=02/some_more_directory/'"]
        test_sql_query_list = self.load_partitions.get_sql('load_partition_test_data')
        self.assertCountEqual([x.strip() for x in sql_query_list[0].split('PARTITION')],
                              [x.strip() for x in test_sql_query_list[0].split('PARTITION')])

    def test_get_sql_full_file_names(self):
        sql_query_list = [
            "ALTER TABLE load_partition_test_data ADD IF NOT EXISTS PARTITION(year='2019',month='02') LOCATION 's3://newtools-tests/load_partition_test_data/year=2019/month=02/some_more_directory' PARTITION(year='2019',month='0:2') LOCATION 's3://newtools-tests/load_partition_test_data/year=2019/month=0:2/some_more_directory' PARTITION(year='2020',month='01') LOCATION 's3://newtools-tests/load_partition_test_data/year=2020/month=01/some_more_directory' PARTITION(year='2020',month='01') LOCATION 's3://newtools-tests/load_partition_test_data/year=2020/month=01/some_more_directory_1' PARTITION(year='2020',month='02') LOCATION 's3://newtools-tests/load_partition_test_data/year=2020/month=02/some_more_directory'"]
        file_names = ['s3://newtools-tests/load_partition_test_data/year=2019/month=02/some_more_directory/file1.parquet.sz',
                      's3://newtools-tests/load_partition_test_data/year=2019/month=0:2/some_more_directory/file2.parquet.sz',
                      's3://newtools-tests/load_partition_test_data/year=2020/month=01/some_more_directory/file3.parquet.sz',
                      's3://newtools-tests/load_partition_test_data/year=2020/month=01/some_more_directory_1/file4.parquet.sz',
                      's3://newtools-tests/load_partition_test_data/year=2020/month=02/some_more_directory/file5.parquet.sz']
        test_sql_query_list = self.load_partitions.get_sql_from_file_names('load_partition_test_data', file_names)
        self.assertCountEqual([x.strip() for x in sql_query_list[0].split('PARTITION')],
                              [x.strip() for x in test_sql_query_list[0].split('PARTITION')])

    def test_generate_sql(self):
        partitions_list = {'load_partition_test_data/year=2019/month=02/some_more_directory/',
                           'load_partition_test_data/year=2019/month=0:2/some_more_directory/',
                           'load_partition_test_data/year=2020/month=01/some_more_directory/'}

        sql_query_list = [
            "ALTER TABLE load_partition_test_data ADD IF NOT EXISTS PARTITION(year='2019',month='02') LOCATION 's3://newtools-tests/load_partition_test_data/year=2019/month=02/some_more_directory/' PARTITION(year='2019',month='0:2') LOCATION 's3://newtools-tests/load_partition_test_data/year=2019/month=0:2/some_more_directory/' PARTITION(year='2020',month='01') LOCATION 's3://newtools-tests/load_partition_test_data/year=2020/month=01/some_more_directory/'"]

        sql_query_list_test = self.load_partitions.generate_sql('load_partition_test_data', partitions_list)
        self.assertCountEqual([x.strip() for x in sql_query_list[0].split('PARTITION')],
                              [x.strip() for x in sql_query_list_test[0].split('PARTITION')])

    def test_generate_sql_with_client(self):
        partitions_list = {'load_partition_test_data/year=2019/month=02/',
                           'load_partition_test_data/year=2019/month=0:2/',
                           'load_partition_test_data/year=2020/month=01/',
                           'load_partition_test_data/year=2020/month=02/'}

        sql_query_list = [
            "ALTER TABLE load_partition_test_data ADD IF NOT EXISTS PARTITION(year='2020',month='02') LOCATION 's3://newtools-tests/load_partition_test_data/year=2020/month=02/'"]

        sql_query_list_test = self.load_partitions.generate_sql('load_partition_test_data', partitions_list,
                                                                athena_client=self.athena_client,
                                                                output_location=self.output_location)
        self.assertCountEqual(sql_query_list, sql_query_list_test)

    def test_generate_sql_with_client_error(self):
        partitions_list = {'load_partition_test_data/year=2019/month=02/',
                           'load_partition_test_data/year=2019/month=0:2/',
                           'load_partition_test_data/year=2020/month=01/'}

        with self.assertRaises(ValueError):
            self.load_partitions.generate_sql('load_partition_test_data', partitions_list,
                                              athena_client=self.athena_client)
