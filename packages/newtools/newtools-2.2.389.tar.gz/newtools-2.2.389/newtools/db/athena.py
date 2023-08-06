# (c) 2012-2018 Deductive, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)
import logging
import os

from newtools.queue import TaskQueue
from newtools.doggo import CSVDoggo
from newtools.aws import S3Location

from newtools.optional_imports import boto3, AWSRetry


class AthenaClient(TaskQueue):
    """
    A client for AWS Athena that runs queries against Athena. Includes queuing functionality to run multiple
    queries and wait until they have completed
    """

    def __init__(self, region, db, max_queries=3, max_retries=3, query_terminating=True,
                 df_handler=None, workgroup=None, logger=logging.getLogger("newtools.athena")):
        """
        Create an AthenaClient

        :param region: the AWS region to create the object, e.g. us-east-2
        :param max_queries: the maximum number of queries to run at any one time, defaults to three
        :type max_queries: int
        :param max_retries: the maximum number of times execution of the query will be retried on failure
        :type max_retries: int
        :param query_terminating: whether to terminate all queries when deleting the class
        :type query_terminating bool
        :param workgroup: optional workgroup for AWS Athena
        :type workgroup string
        :param logger: the logger to use for this class and any newtools classes created by this class
        """
        self.df_handler = CSVDoggo() if df_handler is None else df_handler
        self.athena = boto3.client(service_name='athena', region_name=region)
        self.db_name = db
        self.aws_region = region
        self.query_terminating = query_terminating
        self._workgroup = workgroup
        self._logger = logger

        super(AthenaClient, self).__init__(max_queries, max_retries)

    def __del__(self):
        """
        when deleting the instance, ensure that all associated tasks are stopped and do not enter the queue
        """
        if self.query_terminating:
            self.stop_and_delete_all_tasks()

    @AWSRetry.backoff(added_exceptions=["ThrottlingException"])
    def _update_task_status(self, task):
        """
        Gets the status of the query, and updates its status in the queue.
        Any queries that fail are reset to pending so they will be run a second time
        """

        if task.id is not None:
            self._logger.debug(
                "...checking status of query {0} to {1}".format(task.name, task.arguments["output_location"]))
            status = self.athena.get_query_execution(QueryExecutionId=task.id)["QueryExecution"]["Status"]

            if status["State"] in ("RUNNING", "QUEUED"):
                task.is_complete = False
            elif status["State"] == "SUCCEEDED":
                task.is_complete = True
            else:
                task.error = status.get("StateChangeReason", status["State"])
        else:
            task.is_complete = True

    def _trigger_task(self, task):
        """
        Runs a query in Athena
        """

        self._logger.info("Starting query {0}, remaining {2}, output to to {1},".format(
            task.name,
            task.arguments["output_location"],
            self.time_remaining))

        # Set up the kwargs, excluding any None values
        kwargs = {k: v for (k, v) in {
            "QueryString": task.arguments["sql"],
            "QueryExecutionContext": {'Database': self.db_name},
            "ResultConfiguration": {'OutputLocation': task.arguments["output_location"]},
            "WorkGroup": self._workgroup
        }.items() if v is not None}

        task.id = self.athena.start_query_execution(**kwargs)["QueryExecutionId"]

    def add_query(self, sql, name=None, output_location=None):
        """
        Adds a query to Athena. Respects the maximum number of queries specified when the module was created.
        Retries queries when they fail so only use when you are sure your syntax is correct!
        Returns a query object
        :param sql: the SQL query to run
        :param name: an optional name which will be logged when running this query
        :param output_location: the S3 prefix where you want the results stored (required if workgroup is not specified)
        :return: a unique identified for this query
        """
        return self.add_task(
            name=sql[:255] if name is None else name,
            args={"sql": sql,
                  "output_location": None if output_location is None else S3Location(output_location).s3_url})

    def wait_for_completion(self):
        """
        Check if jobs have failed, if so trigger deletion event for AthenaClient,
        else wait for completion of any queries .
        Will automatically remove all pending and stop all active queries upon completion.
        """
        try:
            super(AthenaClient, self).wait_for_completion()
        except Exception as e:
            raise e
        finally:
            self.stop_and_delete_all_tasks()

    def get_query_result(self, query):
        """
        Returns Pandas DataFrame containing query result if query has completed
        :param query: the query ID returned from add_query()
        """
        self._update_task_status(query)

        if query.is_complete:
            filepath = os.path.join(query.arguments["output_location"], "{}.csv".format(query.id))
            self._logger.info("Fetching results from {}".format(filepath))
            df = self.df_handler.load_df(filepath)
            return df
        else:
            raise ValueError("Cannot fetch results since query hasn't completed")

    def _stop_all_active_tasks(self):
        """
        iterates through active queue and stops all queries from executing
        :return: None
        """
        while self.active_queue:
            task = self.active_queue.pop()
            if task.id is not None:
                self._logger.info("Response while stop_query_execution with following QueryExecutionId {}; {}"
                                  .format(task.id, self.athena.stop_query_execution(QueryExecutionId=task.id)))

    def stop_and_delete_all_tasks(self):
        """
        stops active tasks and removes pending tasks for a given client
        :return: None
        """
        self._empty_pending_queue()
        self._stop_all_active_tasks()
