# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Selenium tests for the runs summary page."""
import time

from autoreduce_qp.systemtests.utils.data_archive import DataArchive
from autoreduce_frontend.selenium_tests.pages.runs_list_page import RunsListPage
from autoreduce_frontend.selenium_tests.tests.base_tests import (AccessibilityTestMixin, BaseTestCase, FooterTestMixin,
                                                                 NavbarTestMixin)


class TestRunsList(BaseTestCase, AccessibilityTestMixin, FooterTestMixin, NavbarTestMixin):
    """Test cases for the InstrumentSummary page."""

    fixtures = BaseTestCase.fixtures + ["eleven_runs"]

    def setUp(self) -> None:
        """Sets up the InstrumentSummaryPage object."""
        super().setUp()
        self.instrument_name = "TESTINSTRUMENT"
        self.page = RunsListPage(self.driver, self.instrument_name)

    def test_tables_loaded(self):
        """
        Test that the Runs Tabel and Experiment Table are loaded correctly.
        """
        for filter_selection in ("Run Number", "Experiment Reference (RB)", "Batch Run"):
            self.page.launch()
            self.page.update_filter("filter_select", filter_selection)
            self.page.click_apply_filters()
            if filter_selection == "Run Number":
                runs = self.page.get_run_numbers_from_table()
                assert len(runs) > 0
            elif filter_selection == "Experiment Reference (RB)":
                experiments = self.page.get_experiments_from_table()
                assert len(experiments) > 0

    def test_table_column_attributes(self):
        """Test that the attributes (class name etc.) to the status column are being added."""
        self.page.launch()
        status_list = self.page.get_status_from_table()
        assert len(status_list) > 0

    def test_alert_message_when_missing_reduce_vars(self):
        """
        Test that the correct message is shown when the reduce_vars.py file is
        missing.
        """
        self.page.launch()
        expected = "The buttons above have been disabled because reduce_vars.py is missing for this instrument."
        assert self.page.variables_alert_message_text() == expected

    def test_alert_message_when_reduce_vars_has_error(self):
        """
        Test that the correct message is shown when the reduce_vars.py has an
        error in it.
        """
        data_archive = DataArchive([self.instrument_name], 21, 21)
        data_archive.create()

        # Add a reduce_vars script with a syntax error -> missing " after value1
        data_archive.add_reduce_vars_script(self.instrument_name, """standard_vars={"variable1":"value1}""")

        self.page.launch()
        expected = "The buttons above have been disabled because reduce_vars.py has an import or syntax error."
        assert self.page.variables_alert_message_text() == expected

        data_archive.delete()


class TestRunsListQueries(BaseTestCase, AccessibilityTestMixin, FooterTestMixin, NavbarTestMixin):
    """Test cases for the InstrumentSummary page queries."""

    fixtures = BaseTestCase.fixtures + ["eleven_runs"]

    def setUp(self) -> None:
        """Sets up the InstrumentSummaryPage object."""
        super().setUp()
        self.instrument_name = "TESTINSTRUMENT"
        self.page = RunsListPage(self.driver, self.instrument_name)

    def _test_page_query(self, query):
        """
        Test that the given query is in a run's URL after clicking a run and
        then clicking the `Back to <InstrumentName> runs` button.
        """
        assert query in self.page.get_top_run().get_attribute('href')

        # Check query after clicking the top run
        runs = self.page.get_run_numbers_from_table()
        top_run_num = runs[0]
        run_summary_page = self.page.click_run(top_run_num)
        assert query in run_summary_page.driver.current_url
        assert query in run_summary_page.cancel_button.get_attribute('href')

        # Check query after returning to runs list
        runs_list_page = run_summary_page.click_cancel_btn()
        runs = runs_list_page.get_run_numbers_from_table()
        assert query in runs_list_page.get_top_run().get_attribute('href')
        assert query in runs_list_page.driver.current_url

    def test_each_query(self):
        """Test that each potential query is maintained."""
        for query in ("sort=-run_number", "per_page=10", "filter=run", "page="):
            self.page.launch()
            self._test_page_query(query + ("1" if query == "page=" else ""))

            self.page.click_next_page_button()
            self._test_page_query(query + ("2" if query == "page=" else ""))

    def test_pagination_filter(self):
        """Test that changing the pagination filter also updates the URL query."""
        for pagination in (10, 25, 50, 100, 250, 500):
            self.page.launch()
            self.page.update_filter("pagination_select", str(pagination))
            self.page.click_apply_filters()
            self._test_page_query(f"per_page={pagination}")

    def test_run_navigation_btns(self):
        """
        Test that the run navigation buttons work. Begin from the fifth run in
        the fixture.
        """
        for nav in ("newest", "next", "previous"):
            self.page.launch()
            runs = self.page.get_run_numbers_from_table()
            fifth_run = runs[4]
            run_summary_page = self.page.click_run(fifth_run)
            assert run_summary_page.title_text() == "Reduction Job #100005"
            time.sleep(3)
            run_summary_page.click_btn_by_id(nav)
            time.sleep(3)
            if nav == "next":
                assert run_summary_page.title_text() == "Reduction Job #100006"
            elif nav == "previous":
                assert run_summary_page.title_text() == "Reduction Job #100004"
            elif nav == "newest":
                assert run_summary_page.title_text() == "Reduction Job #100009"

    def test_disabled_btns(self):
        """
        Test that the run summary navigation buttons are disabled depending on a
        runs' recency.

        The latest run should have the `Newest` and `Next` buttons disabled.

        The oldest run should have the `Previous` button disabled.

        Note:
            This test assumes that the runs are being sorted by number.
        """
        for btn_id, run_number in (("newest", 100009), ("next", 100009), ("previous", 99999)):
            self.page.launch()

            # The first run is on the second page so need to navigate to it
            if run_number == 99999:
                self.page.click_next_page_button()

            run_summary_page = self.page.click_run(run_number)
            assert run_summary_page.is_disabled(btn_id)
