# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
from parameterized import parameterized
from selenium.webdriver.common.by import By

from autoreduce_db.reduction_viewer.models import ReductionArguments

from autoreduce_frontend.selenium_tests.pages.configure_new_runs_page import ConfigureNewRunsPage
from autoreduce_frontend.selenium_tests.pages.variables_summary_page import VariableSummaryPage
from autoreduce_frontend.selenium_tests.tests.base_tests import BaseIntegrationTestCase

REDUCE_VARS_DEFAULT_VALUE = "default value from reduce_vars"


# pylint:disable=no-member
class TestConfigureNewRunsPageIntegration(BaseIntegrationTestCase):
    fixtures = BaseIntegrationTestCase.fixtures + ["run_with_one_variable"]

    @classmethod
    def setUpClass(cls):
        """
        Sets up the Datarchive complete with scripts, the database client and checks the queue client and listerner
        are running for all testcases
        """
        super().setUpClass()
        cls.data_archive.add_reduction_script(cls.instrument_name,
                                              """def main(input_file, output_dir): print('some text')""")
        cls.data_archive.add_reduce_vars_script(cls.instrument_name,
                                                f"""standard_vars={{"variable1":"{REDUCE_VARS_DEFAULT_VALUE}"}}""")
        cls.rb_number = 1234567
        cls.run_number = 99999

    def setUp(self) -> None:
        """Sets up the ConfigureNewRunsPage before each test case"""
        super().setUp()
        self.page = ConfigureNewRunsPage(self.driver, self.instrument_name, run_start=self.run_number + 1)

    def _submit_args_value(self, value, start=None, experiment_number=None):
        self.page = ConfigureNewRunsPage(self.driver,
                                         self.instrument_name,
                                         run_start=start,
                                         experiment_reference=experiment_number)
        self.page.launch()
        self.page.variable1_field = value
        self.page.submit_button.click()

    @staticmethod
    def assert_expected_args(args, expected_run_number, expected_reference, expected_value):
        """
        Assert that a args has the expected values
        :param args: The args to check
        :param expected_run_number: The expected run_number
        :param expected_reference: The expected reference
        :param expected_value: The expected args value
        """
        assert args.as_dict()["standard_vars"]["variable1"] == expected_value
        if expected_run_number is not None:
            assert args.start_run == expected_run_number
        else:
            assert args.start_run is None
        if expected_reference is not None:
            assert args.experiment_reference == expected_reference
        else:
            assert args.experiment_reference is None

    def test_submit_submit_same_variables_does_not_add_new_variables(self):
        """
        Test: Just opening the submit page and clicking rerun
        Expected: The arguments get updated with the new value, and a new object is not made
        """
        self.page = ConfigureNewRunsPage(self.driver, self.instrument_name, run_start=self.run_number)
        self.page.launch()
        self.page.submit_button.click()

        assert ReductionArguments.objects.count() == 1

        summary = VariableSummaryPage(self.driver, self.instrument_name)
        assert summary.current_arguments_by_run.is_displayed()

        assert summary.upcoming_arguments_by_run.text == "No upcoming arguments found"
        assert summary.upcoming_arguments_by_experiment.text == "No arguments found"

    def test_submit_new_value_for_existing_start_run(self):
        """
        Test: Submitting a new variable configuration that starts from the next run number
        Expected: A ReductionArguments is created with the new value, and starting at the next run number
        """
        self._submit_args_value("new_value", self.run_number + 1)
        assert ReductionArguments.objects.count() == 2
        assert ReductionArguments.objects.last().start_run == self.run_number + 1

        summary = VariableSummaryPage(self.driver, self.instrument_name)
        assert summary.current_arguments_by_run.is_displayed()
        assert summary.upcoming_arguments_by_run.is_displayed()
        assert summary.upcoming_arguments_by_experiment.text == "No arguments found"

    def test_submit_experiment_var(self):
        """
        Test: Submitting a new variable for an experiment creates the configuration
        Expected: A ReductionArguments is created with the new value for the given experiment
        """
        self._submit_args_value("new_value", experiment_number=self.rb_number)

        assert ReductionArguments.objects.count() == 2
        new_args = ReductionArguments.objects.last()
        self.assert_expected_args(new_args, None, self.rb_number, "new_value")

        summary = VariableSummaryPage(self.driver, self.instrument_name)
        assert summary.current_arguments_by_run.is_displayed()
        assert summary.upcoming_arguments_by_experiment.is_displayed()
        assert summary.upcoming_arguments_by_run.text == "No upcoming arguments found"

    @parameterized.expand([[1, 101], [1, 201]])
    def test_submit_multiple_run_ranges(self, increment_one: int, increment_two: int):
        """
        Test: Submitting variables for multiple run ranges
        Expected: They are created with the correct ranges and
                  show up in the 'see instrument variables' page
        """
        self._submit_args_value("new_value", self.run_number + increment_one)
        self._submit_args_value("the newest value", self.run_number + increment_two)

        assert ReductionArguments.objects.count() == 3
        first_args, second_args, third_args = ReductionArguments.objects.all()
        self.assert_expected_args(first_args, self.run_number, None, "value1")
        self.assert_expected_args(second_args, self.run_number + increment_one, None, "new_value")
        self.assert_expected_args(third_args, self.run_number + increment_two, None, "the newest value")

        summary = VariableSummaryPage(self.driver, self.instrument_name)
        assert summary.current_arguments_by_run.is_displayed()
        assert summary.upcoming_arguments_by_run.is_displayed()
        assert summary.upcoming_arguments_by_experiment.text == "No arguments found"

    def test_submit_multiple_experiments(self):
        """Test submitting vars for multiple experiments"""
        self._submit_args_value("new_value", experiment_number=self.rb_number)
        self._submit_args_value("the newest value", experiment_number=self.rb_number + 100)

        assert ReductionArguments.objects.count() == 3
        first_args, second_args, third_args = ReductionArguments.objects.all()
        self.assert_expected_args(first_args, self.run_number, None, "value1")
        self.assert_expected_args(second_args, None, self.rb_number, "new_value")
        self.assert_expected_args(third_args, None, self.rb_number + 100, "the newest value")

        summary = VariableSummaryPage(self.driver, self.instrument_name)
        assert summary.current_arguments_by_run.is_displayed()
        assert summary.upcoming_arguments_by_experiment.is_displayed()

        summary.upcoming_arguments_by_run.is_displayed()

    def test_submit_multiple_run_ranges_and_then_experiment(self):
        """Test submitting both run range vars and experiment vars"""
        self._submit_args_value("new_value", self.run_number + 1)
        self._submit_args_value("the newest value", self.run_number + 201)
        self._submit_args_value("some value for experiment", experiment_number=self.rb_number)
        self._submit_args_value("some different value for experiment", experiment_number=self.rb_number + 100)

        assert ReductionArguments.objects.count() == 5
        first_args, second_args, fourth_args, exp_args1, exp_args2 = ReductionArguments.objects.all()

        self.assert_expected_args(first_args, self.run_number, None, "value1")
        self.assert_expected_args(second_args, self.run_number + 1, None, "new_value")
        self.assert_expected_args(fourth_args, self.run_number + 201, None, "the newest value")
        self.assert_expected_args(exp_args1, None, self.rb_number, "some value for experiment")
        self.assert_expected_args(exp_args2, None, self.rb_number + 100, "some different value for experiment")

        summary = VariableSummaryPage(self.driver, self.instrument_name)
        assert summary.current_arguments_by_run.is_displayed()
        assert summary.upcoming_arguments_by_experiment.is_displayed()
        assert summary.upcoming_arguments_by_run.is_displayed()

    def test_submit_then_edit_then_delete_run_args(self):
        """Test submitting new variables for run ranges, then editing them, then deleting them"""
        self._submit_args_value("new_value", self.run_number + 1)
        self._submit_args_value("the newest value", self.run_number + 101)
        self._submit_args_value("value for 201", self.run_number + 201)
        self._submit_args_value("value for 301", self.run_number + 301)

        summary = VariableSummaryPage(self.driver, self.instrument_name)

        summary.click_run_edit_button_for(self.run_number + 1)

        self.page.variable1_field = "a new test value 123"
        self.page.submit_button.click()

        upcoming_panel = summary.panels[1]

        assert "new_value" not in upcoming_panel.get_attribute("textContent")
        assert "a new test value 123" in upcoming_panel.get_attribute("textContent")

        summary.click_run_delete_button_for(self.run_number + 1, self.run_number + 100)

        upcoming_panel = summary.panels[1]
        assert "a new test value 123" not in upcoming_panel.get_attribute("textContent")

        incoming_run_numbers = upcoming_panel.find_elements(By.CLASS_NAME, "run-numbers")

        assert "100100" in incoming_run_numbers[0].text
        assert "100199" in incoming_run_numbers[0].text
        assert "100200" in incoming_run_numbers[1].text
        assert "100299" in incoming_run_numbers[1].text
        assert "100300" in incoming_run_numbers[2].text
        assert "Ongoing" in incoming_run_numbers[2].text

        # now for the 2nd variable we made
        summary.click_run_edit_button_for(self.run_number + 201)
        self.page.variable1_field = "another new test value 321"
        self.page.submit_button.click()

        upcoming_panel = summary.panels[1]

        assert "new_value" not in upcoming_panel.get_attribute("textContent")
        assert "another new test value 321" in upcoming_panel.get_attribute("textContent")

        summary.click_run_delete_button_for(self.run_number + 201, self.run_number + 300)

        upcoming_panel = summary.panels[1]
        assert "another new test value 321" not in upcoming_panel.get_attribute("textContent")

        incoming_run_numbers = upcoming_panel.find_elements(By.CLASS_NAME, "run-numbers")

        # there's a few leftover default variables, but that's OK because the user can remove them
        assert "100100" in incoming_run_numbers[0].text
        assert "100299" in incoming_run_numbers[0].text
        assert "100300" in incoming_run_numbers[1].text
        assert "Ongoing" in incoming_run_numbers[1].text

    def test_submit_then_edit_then_delete_experiment_vars(self):
        """Test submitting new variables for experiment reference, then editing them, then deleting them"""
        self._submit_args_value("new_value", experiment_number=1234567)
        self._submit_args_value("the newest value", experiment_number=2345678)
        summary = VariableSummaryPage(self.driver, self.instrument_name)
        summary.click_experiment_edit_button_for(1234567)

        self.page.variable1_field = "a new test value 123"
        self.page.submit_button.click()

        experiment_panel = summary.panels[1]

        assert "new_value" not in experiment_panel.get_attribute("textContent")
        assert "a new test value 123" in experiment_panel.get_attribute("textContent")

        summary.click_experiment_delete_button_for(1234567)

        experiment_panel = summary.panels[1]
        incoming_exp_numbers = experiment_panel.find_elements(By.CLASS_NAME, "run-numbers")

        assert "2345678" in incoming_exp_numbers[0].text

        summary.click_experiment_edit_button_for(2345678)

        self.page.variable1_field = "a new value for experiment 2345678"
        self.page.submit_button.click()

        experiment_panel = summary.panels[1]

        assert "the newest value" not in experiment_panel.get_attribute("textContent")
        assert "a new value for experiment 2345678" in experiment_panel.get_attribute("textContent")

        summary.click_experiment_delete_button_for(2345678)

        # only the current variables panel left
        assert len(summary.panels) == 1
        assert 'Runs\n99999\nOngoing\nstandard_vars\nvariable1: value1\nadvanced_vars' in summary.panels[0].text
