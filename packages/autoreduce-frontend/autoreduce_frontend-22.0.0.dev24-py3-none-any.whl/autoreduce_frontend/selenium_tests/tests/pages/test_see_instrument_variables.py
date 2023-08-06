# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #

from typing import List

from parameterized import parameterized
from selenium.webdriver.common.by import By
from autoreduce_qp.systemtests.utils.data_archive import DataArchive

from autoreduce_frontend.selenium_tests.pages.configure_new_runs_page import ConfigureNewRunsPage
from autoreduce_frontend.selenium_tests.pages.variables_summary_page import VariableSummaryPage
from autoreduce_frontend.selenium_tests.tests.base_tests import (BaseTestCase, FooterTestMixin, NavbarTestMixin,
                                                                 AccessibilityTestMixin)


class TestSeeInstrumentVariablesPage(BaseTestCase, AccessibilityTestMixin, FooterTestMixin, NavbarTestMixin):
    fixtures = BaseTestCase.fixtures + ["one_run_mixed_vars"]

    @classmethod
    def setUpClass(cls):
        """Sets up the data archive with a reduce and reduce_vars script to be shared between test cases"""
        super().setUpClass()
        cls.instrument_name = "TESTINSTRUMENT"
        cls.data_archive = DataArchive([cls.instrument_name], 21, 21)
        cls.data_archive.create()
        cls.data_archive.add_reduction_script(cls.instrument_name, """print('some text')""")
        # NOTE the value here must match the value of the last variable in the fixture
        # if it doesn't it's value will be updated once the previous range (100151-100199) is updated
        # this is expected, as the final variable (valid for 100200 onwards) should have the default script value!
        cls.data_archive.add_reduce_vars_script(cls.instrument_name, """standard_vars={"variable1":"value4"}""")

    @classmethod
    def tearDownClass(cls) -> None:
        """Destroys the created DataArchive"""
        cls.data_archive.delete()
        super().tearDownClass()

    def setUp(self) -> None:
        """Sets up the VariableSummaryPage before each test case"""
        super().setUp()
        self.page = VariableSummaryPage(self.driver, self.instrument_name)
        self.page.launch()

    @parameterized.expand([(100100, 100150, "value2", ["some new value", "value3", "value4"]),
                           (100151, 100199, "value3", ["value2", "some new value", "value4"]),
                           (100200, 0, "value4", ["value2", "value3", "some new value"])])
    def test_edit(self, start: int, end: int, value_to_modify: str, expected_strings: List[str]):
        """Test: That run variables can be edited for upcoming runs."""
        upcoming_panel = self.page.panels[1]
        # makes sure the value we are going to modify is present in the initial values
        assert value_to_modify in upcoming_panel.get_attribute("textContent")

        self.page.click_run_edit_button_for(start)

        new_runs_page = ConfigureNewRunsPage(self.driver, self.instrument_name, start, end)
        assert new_runs_page.run_start_val == str(start)

        assert new_runs_page.variable1_field_val == value_to_modify
        new_runs_page.variable1_field = "some new value"
        new_runs_page.submit_button.click()

        upcoming_panel = self.page.panels[1]
        # make sure the value we are modifying is no longer visible
        assert value_to_modify not in upcoming_panel.get_attribute("textContent")

        # checks that the newly edited value is present, but also that the unaffected ones are still there
        for expected in expected_strings:
            assert expected in upcoming_panel.get_attribute("textContent")

    @parameterized.expand([
        (100100, 100150, "value2", 100150),
        (100151, 100199, "value3", 100099),
        (100200, 0, "value4", 100099),
    ])
    def test_delete_variable_for_run(self, start: int, end: int, value_to_delete: str, end_run_for_current_vars: int):
        """Tests that variables can be deleted from upcoming runs"""
        upcoming_panel = self.page.panels[1]
        # makes sure the value we are going to modify is present in the initial values
        assert value_to_delete in upcoming_panel.get_attribute("textContent")

        incoming_run_numbers = upcoming_panel.find_elements(By.CLASS_NAME, "run-numbers")

        assert "100100" in incoming_run_numbers[0].text
        assert "100150" in incoming_run_numbers[0].text
        assert "100151" in incoming_run_numbers[1].text
        assert "100199" in incoming_run_numbers[1].text
        assert "100200" in incoming_run_numbers[2].text
        assert "Ongoing" in incoming_run_numbers[2].text

        self.page.click_run_delete_button_for(start, end)

        current_panel_runs = self.page.panels[0].find_element(By.CLASS_NAME, "run-numbers")
        # check that the current variables end at the correct run
        assert str(end_run_for_current_vars) in current_panel_runs.text
        upcoming_panel = self.page.panels[1]
        # make sure the value we are modifying is no longer visible
        assert value_to_delete not in upcoming_panel.get_attribute("textContent")

    @parameterized.expand([[1234567], [7654321]])
    def test_edit_experiment(self, experiment_reference):
        """Tests: Variables can be edited for upcoming runs for an experiment"""
        experiment_panel = self.page.panels[2]
        # makes sure the value we are going to modify is present in the initial values
        assert f"experiment {experiment_reference} var" in experiment_panel.get_attribute("textContent")

        self.page.click_experiment_edit_button_for(experiment_reference)
        new_runs_page = ConfigureNewRunsPage(self.driver,
                                             self.instrument_name,
                                             experiment_reference=experiment_reference)

        assert new_runs_page.variable1_field_val == f"experiment {experiment_reference} var"

        new_runs_page.variable1_field = "some new value"
        new_runs_page.submit_button.click()

        experiment_panel = self.page.panels[2]
        assert f"experiment {experiment_reference} var" not in experiment_panel.get_attribute("textContent")
        assert "some new value" in experiment_panel.get_attribute("textContent")

    @parameterized.expand([[1234567], [7654321]])
    def test_delete_variable_for_experiment(self, experiment_reference):
        """Tests: Variables can be deleted for an experiment"""
        experiment_panel = self.page.panels[2]
        # makes sure the value we are going to modify is present in the initial values
        assert f"experiment {experiment_reference} var" in experiment_panel.get_attribute("textContent")

        self.page.click_experiment_delete_button_for(experiment_reference)
        experiment_panel = self.page.panels[2]
        assert f"experiment {experiment_reference} var" not in experiment_panel.get_attribute("textContent")
