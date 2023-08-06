"""Library defining the interface to stress test jobs."""

import logging
import time
from typing import Any, Dict, Optional

import grpc
import pandas as pd
from deprecated import deprecated
from google.protobuf.json_format import MessageToDict

from rime_sdk.internal.backend import RIMEBackend
from rime_sdk.protos.jobs.jobs_pb2 import (
    GetJobRequest,
    JobMetadata,
    JobStatus,
    JobType,
    JobView,
    TestRunProgress,
    TestTaskStatus,
)
from rime_sdk.protos.model_testing.model_testing_pb2 import GetLatestLogsRequest
from rime_sdk.test_run import TestRun

default_csv_header = ["test_name", "feature(s)", "status"]

logger = logging.getLogger()


class Job:
    """An interface to a RIME job.

    This object provides an interface for monitoring the status of a
    job in the RIME backend.
    """

    def __init__(
        self, backend: RIMEBackend, job_id: str, job_type: "JobType.V"
    ) -> None:
        """Create a new RIME Job.

        Args:
            backend: RIMEBackend
                The RIME backend used to query about the status of the job.
            job_id: str
                The identifier for the RIME job that this object monitors.
            job_type: JobType.V
                The type of the RIME job that this object monitors.
        """
        self._backend = backend
        self._job_id = job_id
        self._job_type = job_type

    @property
    def job_id(self) -> str:
        """Return the id of the job."""
        return self._job_id

    @property
    def job_type(self) -> "JobType.V":
        """Return the type of the job."""
        return self._job_type

    def __str__(self) -> str:
        """Pretty-print the object."""
        # Ping the backend for the status of the job and detailed info only for
        # succeeded jobs.
        status = self.get_status()
        ret = {
            "job_id": self._job_id,
            "job_type": self._job_type,
            "status": status.get("status"),
            "termination_reason": status.get("terminationReason"),
        }
        if status["status"] == JobStatus.Name(JobStatus.JOB_STATUS_SUCCEEDED):
            test_run_obj = self.get_test_run()
            test_run_res = test_run_obj.get_result_df()
            for k, v in test_run_res.iloc[0].to_dict().items():
                # Omit metrics from the output dictionary.
                if not str(k).startswith("metrics"):
                    ret[k] = v
        return f"StressTestJob {ret}"

    def __eq__(self, obj: Any) -> bool:
        """Check if this job is equivalent to 'obj'."""
        return isinstance(obj, Job) and self._job_id == obj._job_id

    @staticmethod
    def _get_test_run_progress(test_run: TestRunProgress) -> Optional[str]:
        test_batches = test_run.test_batches
        if len(test_batches) == 0:
            return None
        n = sum(
            batch.status == TestTaskStatus.TEST_TASK_STATUS_COMPLETED
            for batch in test_batches
        )
        return "{:<2} / {:>2} tests completed".format(n, len(test_batches))

    def _get_progress(self, job: JobMetadata) -> Optional[str]:
        """Pretty print the progress of the test run."""
        if self._job_type == JobType.JOB_TYPE_MODEL_STRESS_TEST:
            return self._get_test_run_progress(job.job_data.stress.progress.test_run)
        elif self._job_type == JobType.JOB_TYPE_FIREWALL_BATCH_TEST:
            test_runs = job.job_data.continuous_inc.progress.test_runs
            total_ct_runs = len(job.job_data.continuous_inc.ct_test_run_ids)
            if total_ct_runs == 0:
                return None
            finished_test_runs = len(
                [
                    test_run
                    for test_run in test_runs
                    if test_run.test_run.status
                    == TestTaskStatus.TEST_TASK_STATUS_COMPLETED
                ]
            )
            run_progress = "{:<2} / {:>2} time bins completed".format(
                finished_test_runs, total_ct_runs
            )
            for test_run in test_runs:
                if (
                    test_run.test_run.status
                    != TestTaskStatus.TEST_TASK_STATUS_COMPLETED
                ):
                    batch_progress = self._get_test_run_progress(test_run.test_run)
                    if batch_progress is not None:
                        return f"{run_progress}, {batch_progress}"
            return run_progress
        else:
            return None

    @deprecated("Use TestRun.get_link()")
    def get_link(self) -> str:  # noqa: D401
        """Deprecated.

        Get the web app URL for a successful stress test job.

        This link directs to your organization's deployment of RIME.
        You can view more detailed information about the results of your stress test\
        in the web app, including helpful visualiziations, key insights, and\
        explanations of test results.

        Note: this is a string that should be copy-pasted into a browser.

        :meta private:
        """
        test_run = self.get_test_run()
        return test_run.get_link()

    def get_test_run_id(self) -> str:
        """Get the test run ID for a successful job.

        Raises:
            ValueError if the job does not have state 'SUCCEEDED.'
        """
        if self._job_type != JobType.JOB_TYPE_MODEL_STRESS_TEST:
            raise ValueError(
                "Currently, it is only supported to get test run id for job of type: "
                f"`{JobType.Name(JobType.JOB_TYPE_MODEL_STRESS_TEST)}`, "
                f"this job is of type: `{JobType.Name(self._job_type)}`."
            )
        with self._backend.get_job_reader_stub() as job_reader:
            # This first step only prevents a rare case where the RIME engine has
            # signaled the test suite has completed but before the upload has completed.
            job_req = GetJobRequest(job_id=self._job_id)
            with self._backend.GRPCErrorHandler():
                job: JobMetadata = job_reader.GetJob(job_req).job
            if job.status != JobStatus.JOB_STATUS_SUCCEEDED:
                raise ValueError(
                    "Job has status {}; it must have status {} to get results".format(
                        JobStatus.Name(job.status),
                        JobStatus.Name(JobStatus.JOB_STATUS_SUCCEEDED),
                    )
                )
            return job.job_data.stress.test_run_id

    def get_test_run(self) -> TestRun:
        """Get the test run object.

        Raises:
            ValueError if the job does not have state 'SUCCEEDED.'
        """
        test_run_id = self.get_test_run_id()
        return TestRun(self._backend, test_run_id)

    def get_status(
        self,
        verbose: bool = False,
        wait_until_finish: bool = False,
        poll_rate_sec: float = 5.0,
    ) -> Dict:
        """Query the ModelTest service for the job's status.

        This includes flags for blocking until the job is complete and printing
        information to ``stdout``. This method can help with monitoring the
        progress of stress test jobs, because it prints out helpful information
        such as running time and the progress of the test run.

        If the job has failed, the logs of the testing engine will be dumped
        to ``stdout`` to help with debuggability.

        Arguments:
            verbose: bool
                whether or not to print diagnostic information such as progress.
                Note that these logs have no strict form and will be subject to
                significant change in future versions.
            wait_until_finish: bool
                whether or not to block until the job has succeeded or failed.
                If `verbose` is enabled too, information about the job including
                running time and progress will be printed to ``stdout`` every
                ``poll_rate_sec``.
            poll_rate_sec: float
               the frequency with which to poll the job's status. Units are in seconds.

        Returns:
            A dictionary representing the job's state.

            .. code-block:: python

                {
                "id": str
                "type": str
                "status": str
                "start_time_secs": int64
                "running_time_secs": double
                }

        Example:

        .. code-block:: python

            # Block until this job is finished and dump monitoring info to stdout.
            job_status = job.get_status(verbose=True, wait_until_finish=True)
        """
        # Create backend client stubs to use for the remainder of this session.
        with self._backend.get_job_reader_stub() as job_reader, self._backend.get_model_testing_stub() as model_tester:  # pylint: disable=line-too-long
            job_req = GetJobRequest(job_id=self._job_id, view=JobView.JOB_VIEW_FULL)
            with self._backend.GRPCErrorHandler():
                job: JobMetadata = job_reader.GetJob(job_req).job
            if verbose:
                print(
                    "Job '{}' started at {}".format(
                        job.id, job.creation_time.ToDatetime().astimezone(),
                    )
                )

            # Do not repeat if the job is finished or blocking is disabled.
            while wait_until_finish and not job.status in (
                JobStatus.JOB_STATUS_SUCCEEDED,
                JobStatus.JOB_STATUS_FAILED,
            ):
                time.sleep(poll_rate_sec)
                try:
                    job = job_reader.GetJob(job_req).job
                    progress = self._get_progress(job)
                except grpc.RpcError as e:
                    if e.code() == grpc.StatusCode.UNAVAILABLE:
                        if verbose:
                            print("reconnecting to the RIME backend...")
                        continue
                    raise ValueError(e.details()) from None
                if verbose:
                    minute, second = divmod(job.running_time_secs, 60)
                    hour, minute = divmod(minute, 60)
                    progress_str = " ({})".format(progress) if progress else ""
                    print(
                        "Status: {}, Running Time: {:02}:{:02}:{:05.2f}{}".format(
                            JobStatus.Name(job.status),
                            int(hour),
                            int(minute),
                            second,
                            progress_str,
                        )
                    )

            # Only get the logs if the job has failed, as the
            # primary purpose is debuggability during development.
            if job.status == JobStatus.JOB_STATUS_FAILED:
                log_req = GetLatestLogsRequest(job_id=self._job_id)
                try:
                    for log_res in model_tester.GetLatestLogs(request=log_req):
                        print(log_res.chunk, end="")
                except grpc.RpcError as e:
                    if e.code() == grpc.StatusCode.NOT_FOUND:
                        logger.error("Unable to retrieve logs for failed job")
                    else:
                        raise ValueError(e.details()) from None

        job_dict = MessageToDict(job)
        # Hide job data in the return value because it can get ugly.
        if "jobData" in job_dict:
            del job_dict["jobData"]
        return job_dict

    @deprecated("Use TestRun.get_test_cases_result()")
    def get_test_cases_result(self) -> pd.DataFrame:  # noqa: D401
        """Deprecated.

        Retrieve all the test cases in a dataframe.
        This gives you the ability to perform granular queries on
        test cases. For example, if you only care about subset performance tests and
        want to see the results on each feature, you can fetch all the test cases in
        a dataframe, then query on that dataframe by test type. This only works on
        stress test jobs that have succeeded.
        Note: this will not work for test runs run on RIME versions <0.14.0.

        Returns:
            A ``pandas.DataFrame`` object containing the test case results.
            Here is a selected list of columns in the output:
            1. ``test_run_id``: ID of the parent test run.
            2. ``features``: List of features that the test case ran on.
            3. ``test_batch_type``: Type of test that was run (e.g. Subset AUC,\
                Must be Int, etc.).
            4. ``status``: Status of the test case (e.g. Pass, Fail, Skip, etc.).
            5. ``severity``: Metric that denotes the severity of the failure of\
                the test.

        Example:
        .. code-block:: python
            # Wait until the job has finished, since this method only works on
            # SUCCEEDED jobs.
            job.get_status(verbose=True, wait_until_finish=True)
            # Dump the test cases in dataframe ``df``.
            # Print out the column names and types.
            print(df.columns)

        :meta private:
        """
        test_run_obj = self.get_test_run()
        return test_run_obj.get_test_cases_df()

    @deprecated("Use TestRun.get_test_run_result()")
    def get_test_run_result(self) -> pd.DataFrame:  # noqa: D401
        """Deprecated.

        Retrieve high level summary information.
        This dataframe includes information such as model metrics on the reference and\
        evaluation datasets, overall RIME results such as severity across tests,\
        and high level metadata such as the project ID and model task.
        By concatenating these rows together, this allows you to build a table of test
        run results for sake of comparison. This only works on stress test jobs that
        have succeeded.
        Note: this does not work on <0.14.0 RIME test runs.

        Returns:
            A `pandas.DataFrame` object containing the test run result.
            There are a lot of columns, so it is worth viewing them with the `.columns`
            method to see what they are. Generally, these columns have information
            about the model and datasets as well as summary statistics like the number
            of failing test cases or number of high severity test cases.

        Example:
        .. code-block:: python
            # Wait until the job has finished, since this method only works on
            # succeeded jobs.
            job.get_status(verbose=True, wait_until_finish=True)
            # Dump the test cases in dataframe ``df``.
            # Print out the column names and types.
            print(df.columns)

        :meta private:
        """
        test_run_obj = self.get_test_run()
        return test_run_obj.get_result_df()
