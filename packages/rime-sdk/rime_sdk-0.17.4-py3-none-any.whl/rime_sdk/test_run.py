"""Library defining the interface to a test run object."""

from typing import Iterator

import pandas as pd

from rime_sdk.internal.backend import RIMEBackend
from rime_sdk.internal.protobuf_parser import (
    parse_test_case_result,
    parse_test_run_metadata,
)
from rime_sdk.internal.test_helpers import get_batch_result_response
from rime_sdk.protos.test_run_results.test_run_results_pb2 import (
    GetTestRunRequest,
    GetTestRunResponse,
    ListBatchResultsRequest,
    ListBatchResultsResponse,
    ListTestCasesRequest,
    ListTestCasesResponse,
)
from rime_sdk.tests import TestBatch


class TestRun:
    """An interface for a RIME test run.

    Attributes:
        backend: RIMEBackend
            The RIME backend used to query about the test run.
        test_run_id: str
            The string identifier for the successfully completed test run.
    """

    def __init__(self, backend: RIMEBackend, test_run_id: str) -> None:
        """Create a new TestRun object.

        Arguments:
            backend: RIMEBackend
                The RIME backend used to query about the test run.
            test_run_id: str
                The string identifier for the successfully completed test run.
        """
        self._test_run_id = test_run_id
        self._backend = backend

    @property
    def test_run_id(self) -> str:
        """Return the test run id."""
        return self._test_run_id

    def get_link(self) -> str:
        """Get the web app URL for a successful stress test run.

        This link directs to your organization's deployment of RIME.
        You can view more detailed information about the results of your stress test\
        in the web app, including helpful visualiziations, key insights, and\
        explanations of test results.

        Note: this is a string that should be copy-pasted into a browser.
        """
        # Fetch test run metadata and return a dataframe of the single row.
        req = GetTestRunRequest(test_run_id=self.test_run_id)
        with self._backend.GRPCErrorHandler():
            with self._backend.get_test_run_results_stub() as results_reader:
                res: GetTestRunResponse = results_reader.GetTestRun(req)
        return res.test_run.web_app_url.url

    def get_result_df(self) -> pd.DataFrame:
        """Retrieve high level summary information for a complete stress test run in a\
        single-row dataframe.

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

            test_run = client.get_test_run(some_test_run_id)
            test_run_result_df = test_run.get_result_df()
        """
        with self._backend.get_test_run_results_stub() as results_reader:
            # Fetch test run metadata and return a dataframe of the single row.
            req = GetTestRunRequest(test_run_id=self._test_run_id)
            with self._backend.GRPCErrorHandler():
                res: GetTestRunResponse = results_reader.GetTestRun(req)
        # Use utility function for converting Protobuf to a dataframe.
        return parse_test_run_metadata(res.test_run)

    def get_test_cases_df(self, show_test_case_metrics: bool = False) -> pd.DataFrame:
        """Retrieve all the test cases for a completed stress test run in a dataframe.

        This gives you the ability to perform granular queries on test cases.
        For example, if you only care about subset performance tests and want to see
        the results on each feature, you can fetch all the test cases in a dataframe,
        then query on that dataframe by test type. This only works on stress test jobs
        that have succeeded.

        Note: this will not work for test runs run on RIME versions <0.14.0.

        Arguments:
            show_test_case_metrics: bool = False
                Whether to show test case specific metrics. This could result in a
                sparse dataframe that is returned, since test cases return different
                metrics. Defaults to False.

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
            # Get the test run result.
            test_run = job.get_test_run()
            # Dump the test cases in dataframe ``df``.
            df = test_run.get_test_cases_df()
        """
        with self._backend.get_test_run_results_stub() as results_reader:
            all_test_cases = []
            # Iterate through the pages of test cases and break at the last page.
            page_token = ""
            while True:
                tc_req = ListTestCasesRequest(page_size=20)
                if page_token == "":
                    tc_req.list_test_cases_query.test_run_id = self._test_run_id
                else:
                    tc_req.page_token = page_token
                with self._backend.GRPCErrorHandler():
                    res: ListTestCasesResponse = results_reader.ListTestCases(tc_req)
                tc_dicts = [
                    parse_test_case_result(tc, unpack_metrics=show_test_case_metrics)
                    for tc in res.test_cases
                ]
                # Concatenate the list of test case dictionaries.
                all_test_cases += tc_dicts
                # Advance to the next page of test cases.
                page_token = res.next_page_token
                # we've reached the last page of test cases.
                if not res.has_more:
                    break

            return pd.DataFrame(all_test_cases)

    def get_test_batch(self, test_type: str) -> TestBatch:
        """Obtain the corresponding test batch.

        A ``TestBatch`` object allows a user to query the results
        for the corresponding test. For example, the ``TestBatch``
        object representing ``unseen_categorical`` allows a user
        to understand the results of the ``unseen_categorical``
        test to varying levels of granularity.

        Args:
            test_type: str
                Name of the test.

        Returns:
            A ``TestBatch`` representing ``test_type``.

        Example:

        .. code-block:: python

            batch = test_run.get_test_batch("unseen_categorical")
        """
        test_batch_obj = TestBatch(self._backend, self._test_run_id, test_type)
        # check that test batch exists by sending a request
        get_batch_result_response(self._backend, self._test_run_id, test_type)
        return test_batch_obj

    def get_test_batches(self) -> Iterator[TestBatch]:
        """Get all test batches for a given project.

        Returns:
            An iterator across TestBatch objects.
        """
        with self._backend.get_test_run_results_stub() as results_reader:
            # Iterate through the pages of test cases and break at the last page.
            page_token = ""
            while True:
                tb_req = ListBatchResultsRequest(page_size=20)
                if page_token == "":
                    tb_req.test_run_id = self._test_run_id
                else:
                    tb_req.page_token = page_token
                with self._backend.GRPCErrorHandler():
                    res: ListBatchResultsResponse = results_reader.ListBatchResults(
                        tb_req
                    )
                for test_batch in res.test_batches:
                    yield TestBatch(
                        self._backend, self._test_run_id, test_batch.test_type
                    )
                # Advance to the next page of test cases.
                page_token = res.next_page_token
                # we've reached the last page of test cases.
                if not res.has_more:
                    break
