# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #

from django.urls import reverse
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from autoreduce_frontend.selenium_tests.pages.component_mixins.footer_mixin import FooterMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.navbar_mixin import NavbarMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.tour_mixin import TourMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.rerun_form_mixin import RerunFormMixin
from autoreduce_frontend.selenium_tests.pages.page import Page


class ConfigureNewBatchRunsPage(Page, RerunFormMixin, NavbarMixin, FooterMixin, TourMixin):
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
        return reverse("runs:configure_batch_run", kwargs={
            "instrument": self.instrument,
        })

    @property
    def runs(self) -> WebElement:
        """
        Return the run start input WebElement
        """
        return self.driver.find_element(By.ID, "runs")

    @runs.setter
    def runs(self, value) -> None:
        """
        Finds and returns the back button for toggling the form on the page.
        """
        self._set_field(self.runs, value)

    @property
    def runs_val(self) -> WebElement:
        """Return the value of the run start WebElement"""
        return self.runs.get_attribute("value")  # pylint:disable=no-member

    @property
    def reset_to_current_values(self) -> WebElement:
        """
        Finds and returns the "Reset to values in the current reduce_vars script" button
        """
        return self.driver.find_element(By.ID, "currentScript")

    @property
    def error_text(self) -> WebElement:
        """Returns the value of the error field"""
        return self.driver.find_element(By.ID, "error").text
