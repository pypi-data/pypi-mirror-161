from autoreduce_frontend.selenium_tests.pages.failed_jobs_page import FailedJobsPage

from autoreduce_frontend.selenium_tests.tests.base_tests import BaseTestCase


class TestFailedJobs(BaseTestCase):
    """
    Test cases for the error page
    """
    fixtures = BaseTestCase.fixtures + ["two_runs_failed"]

    def setUp(self) -> None:
        """
        Sets up the ErrorPage object
        """
        super().setUp()
        self.page = FailedJobsPage(self.driver)
        self.page.launch()

    def test_failed_runs_visible(self):
        """
        Test that the page error message matches the expected error

        This turns off development mode - this will attempt to use UOWS authentication
        but it's mocked out to raise the ICATConnectionException, so we test the error path.

        At the end it turns it back on or following tests will fail
        """
        assert len(self.page.get_failed_runs()) == 2

    def test_hide_run(self):
        """
        Test that the option to hide a run works
        """
        self.page.update_filter("runAction", "Hide")
        runs = self.page.get_failed_runs()
        original_run_count = len(runs)
        self.page.get_top_checkbox().click()
        self.page.click_apply_button()
        new_run_count = len(self.page.get_failed_runs())
        assert new_run_count == original_run_count - 1
