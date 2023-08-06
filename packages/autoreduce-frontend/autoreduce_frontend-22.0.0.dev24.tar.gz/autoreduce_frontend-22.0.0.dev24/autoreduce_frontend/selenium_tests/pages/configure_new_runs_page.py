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


class ConfigureNewRunsPage(Page, RerunFormMixin, NavbarMixin, FooterMixin, TourMixin):
    """
    Page model class for run summary page
    """

    def __init__(self, driver, instrument, run_start=None, experiment_reference=None):
        super().__init__(driver)
        self.instrument = instrument
        self._run_start_number = run_start
        self._experiment_reference = experiment_reference

    def url_path(self) -> str:
        """
        Return the current URL of the page.
        :return: (str) the url path
        """
        kwargs = {
            "instrument": self.instrument,
        }
        if self._experiment_reference:
            kwargs["experiment_reference"] = self._experiment_reference
            return reverse("runs:variables_by_experiment", kwargs=kwargs)
        else:
            if self._run_start_number:
                kwargs["start"] = self._run_start_number
            return reverse("runs:variables", kwargs=kwargs)

    @property
    def run_start(self) -> WebElement:
        """
        Return the run start input WebElement
        """
        return self.driver.find_element(By.ID, "run_start")

    @property
    def run_start_val(self) -> WebElement:
        """Return the value of the run start WebElement"""
        return self.run_start.get_attribute("value")

    @property
    def reset_to_current_values(self) -> WebElement:
        """
        Finds and returns the "Reset to values in the current reduce_vars script" button
        """
        return self.driver.find_element(By.ID, "currentScript")

    @property
    def go_to_other(self) -> WebElement:
        """Return the link to toggle between by run range or by reference"""
        return self.driver.find_element(By.ID, "go_to_other")
