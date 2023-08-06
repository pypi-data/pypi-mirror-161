# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Selenium tests for the runs summary page."""
from django.urls import reverse

from autoreduce_frontend.selenium_tests.pages.run_summary_page import RunSummaryPage
from autoreduce_frontend.selenium_tests.tests.base_tests import BaseIntegrationTestCase
from autoreduce_frontend.selenium_tests.utils import submit_and_wait_for_result


class TestBatchRunSummaryPageIntegration(BaseIntegrationTestCase):

    fixtures = BaseIntegrationTestCase.fixtures + ["test_batch_run_summary_integration"]

    @classmethod
    def setUpClass(cls):
        """Start all external services."""
        super().setUpClass()
        cls.rb_number = 1234567
        cls.run_number = [123, 124, 125]
        cls.batch_run_test = True
        cls.data_archive.add_reduction_script(cls.instrument_name,
                                              """def main(input_file, output_dir): print('some text')""")
        cls.data_archive.add_reduce_vars_script(cls.instrument_name,
                                                """standard_vars={"variable1":"test_variable_value_123"}""")

    def setUp(self) -> None:
        """
        Set up the RunSummaryPage and show the rerun panel before each test
        case.
        """
        super().setUp()
        self.page = RunSummaryPage(self.driver, self.instrument_name, 1, 0, batch_run=True)
        self.page.launch()
        # Click the toggle to show the rerun panel, otherwise the buttons in the
        # form are non interactive
        self.page.toggle_button.click()

    def test_submit_rerun_same_variables(self):
        """Test opening the submit page and clicking rerun."""
        result = submit_and_wait_for_result(self,
                                            after_submit_url=reverse("runs:configure_batch_run",
                                                                     kwargs={"instrument": self.instrument_name}))
        assert len(result) == 2

        assert result[0].run_version == 0
        assert result[1].run_version == 1

        assert result[0].arguments == result[1].arguments

    def test_submit_rerun_changed_variable_arbitrary_value(self):
        """
        Test opening a submit page, changing a variable, and then submitting the
        run.
        """
        # Change the value of the variable field
        self.page.variable1_field = "the new value in the field"

        result = submit_and_wait_for_result(self,
                                            after_submit_url=reverse("runs:configure_batch_run",
                                                                     kwargs={"instrument": self.instrument_name}))
        assert len(result) == 2

        assert result[0].run_version == 0
        assert result[1].run_version == 1

        assert result[0].arguments != result[1].arguments
        assert result[1].arguments.as_dict()["standard_vars"]["variable1"] == "the new value in the field"

    def test_submit_rerun_after_clicking_reset_initial(self):
        """
        Test that submitting a run after changing the value and then clicking
        reset to initial values will correctly use the initial values.
        """
        # Change the value of the variable field
        self.page.variable1_field = "the new value in the field"

        self.page.reset_to_initial_values.click()
        result = submit_and_wait_for_result(self,
                                            after_submit_url=reverse("runs:configure_batch_run",
                                                                     kwargs={"instrument": self.instrument_name}))
        assert len(result) == 2

        assert result[0].run_version == 0
        assert result[1].run_version == 1

        assert result[0].arguments == result[1].arguments
        assert result[1].arguments.as_dict()["standard_vars"]["variable1"] == "value1"

    def test_submit_rerun_after_clicking_reset_current_script(self):
        """
        Test that submitting a run after clicking the reset to current script
        uses the values saved in the current script.
        """
        self.page.reset_to_current_values.click()
        result = submit_and_wait_for_result(self,
                                            after_submit_url=reverse("runs:configure_batch_run",
                                                                     kwargs={"instrument": self.instrument_name}))

        assert len(result) == 2

        assert result[0].run_version == 0
        assert result[1].run_version == 1

        assert result[0].arguments != result[1].arguments
        assert result[1].arguments.as_dict()["standard_vars"]["variable1"] == "test_variable_value_123"
