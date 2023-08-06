# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Module for the run summary page model
"""
from django.urls.base import reverse
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from autoreduce_frontend.selenium_tests.pages.component_mixins.footer_mixin import FooterMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.navbar_mixin import NavbarMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.rerun_form_mixin import RerunFormMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.tour_mixin import TourMixin
from autoreduce_frontend.selenium_tests.pages.page import Page


class RerunJobsPage(Page, RerunFormMixin, NavbarMixin, FooterMixin, TourMixin):
    """
    Page model class for run summary page
    """

    def __init__(self, driver, instrument):
        super().__init__(driver)
        self.instrument = instrument

    def url_path(self) -> str:
        """
        Return the current URL of the page.
        :return: (str) the url path
        """
        return reverse("runs:rerun_jobs", kwargs={
            "instrument": self.instrument,
        })

    @property
    def form_validation_message(self) -> WebElement:
        """Finds and returns the form validation message"""
        return self.driver.find_element(By.ID, "form_validation_message")

    @property
    def form(self) -> WebElement:
        """Finds and returns the rerun form on the page"""
        return self.driver.find_element(By.ID, "submit_jobs")

    @property
    def reuse_script_radio(self) -> WebElement:
        """Finds and returns the reuse script radio button on the page"""
        return self.driver.find_element(By.XPATH, "//label[@for='id_script_choice_0']")

    @property
    def use_reducepy_file_radio(self) -> WebElement:
        """Finds and returns the use reduce.py file radio button on the page"""
        return self.driver.find_element(By.XPATH, "//label[@for='id_script_choice_1']")

    @property
    def run_range_field(self) -> WebElement:
        """
        Finds and returns the back button for toggling the form on the page.
        """
        return self.driver.find_element(By.ID, "runs")

    @run_range_field.setter
    def run_range_field(self, value) -> None:
        """
        Finds and returns the back button for toggling the form on the page.
        """
        self._set_field(self.run_range_field, value)

    @property
    def reset_to_current_values(self) -> WebElement:
        """
        Finds and returns the "Reset to values in the current reduce_vars script" button
        """
        return self.driver.find_element(By.ID, "currentScript")

    @property
    def error_container(self) -> WebElement:
        """
        Returns the container of the error message
        """
        return self.driver.find_element(By.ID, "error_container")

    def error_message_text(self) -> str:
        """
        Returns the text shown in the error message
        """
        return self.driver.find_element(By.ID, "error_message").text
