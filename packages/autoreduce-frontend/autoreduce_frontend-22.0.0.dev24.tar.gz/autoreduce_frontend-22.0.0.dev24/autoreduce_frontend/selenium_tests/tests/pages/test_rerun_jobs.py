from django.urls import reverse
from autoreduce_qp.systemtests.utils.data_archive import DataArchive

from autoreduce_frontend.selenium_tests.pages.rerun_jobs_page import RerunJobsPage
from autoreduce_frontend.selenium_tests.tests.base_tests import (NavbarTestMixin, BaseTestCase, FooterTestMixin,
                                                                 AccessibilityTestMixin)


# pylint:disable=no-member
class TestRerunJobsPage(BaseTestCase, NavbarTestMixin, FooterTestMixin, AccessibilityTestMixin):
    """
    Test cases for the InstrumentSummary page when the Rerun form is NOT visible
    """

    fixtures = BaseTestCase.fixtures + ["run_with_multiple_variables"]

    @classmethod
    def setUpClass(cls):
        """Sets up DataArchive for all tests and sets instrument for all tests"""
        super().setUpClass()
        cls.instrument_name = "TESTINSTRUMENT"
        cls.data_archive = DataArchive([cls.instrument_name], 21, 21)
        cls.data_archive.create()
        cls.data_archive.add_reduction_script(cls.instrument_name, """print('some text')""")
        cls.data_archive.add_reduce_vars_script(
            cls.instrument_name, """standard_vars={"variable_str":"value1","variable_int":123,"variable_float":123.321,
            "variable_listint":[1,2,3],"variable_liststr":["a","b","c"],"variable_none":None,
            "variable_empty":"","variable_bool":True}""")

    @classmethod
    def tearDownClass(cls) -> None:
        """Destroys created DataArchive"""
        cls.data_archive.delete()
        super().tearDownClass()

    def setUp(self) -> None:
        """Set up RerunJobsPage before each test case"""
        super().setUp()
        self.page = RerunJobsPage(self.driver, self.instrument_name)
        self.page.launch()

    def test_cancel_goes_back_to_runs_list(self):
        """Tests: Clicking canel button returns the runs list page"""
        self.page.cancel_button.click()
        assert reverse("runs:list", kwargs={"instrument": self.instrument_name}) in self.driver.current_url

    def test_reset_values_does_reset_the_values(self):
        """Test that the button to reset the variables to the values from the reduce_vars script works"""
        self.page.variable_str_field = "the new value in the field"
        self.page.reset_to_current_values.click()

        # need to re-query the driver because resetting replaces the elements
        var_field = self.page.variable_str_field
        assert var_field.get_attribute("value") == "value1"

    def test_variables_appear_as_expected(self):
        """
        Test: Just opening the submit page and clicking rerun
        """
        assert self.page.variable_str_field_val == "value1"
        assert self.page.variable_int_field_val == "123"
        assert self.page.variable_float_field_val == "123.321"
        assert self.page.variable_listint_field_val == "[1, 2, 3]"
        assert self.page.variable_liststr_field_val == "['a', 'b', 'c']"
        assert self.page.variable_none_field_val == "None"
        assert self.page.variable_bool_field_val == "True"
