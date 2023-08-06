# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Module for the error page model
"""
from django.urls.base import reverse
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By

from autoreduce_frontend.selenium_tests.pages.component_mixins.footer_mixin import FooterMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.navbar_mixin import NavbarMixin
from autoreduce_frontend.selenium_tests.pages.page import Page


class FailedJobsPage(Page, NavbarMixin, FooterMixin):

    @staticmethod
    def url_path() -> str:
        """
        This needs to be overriden because the basemethod is abstract, but it isn't used
        because the launch method is overriden here too.

        :return: (str) the url path
        """
        return reverse("runs:failed")

    def get_failed_runs(self) -> list:
        """
        Gets the failed runs from the page

        :return: (list) a list of failed run objects
        """
        return self.driver.find_elements(By.CLASS_NAME, "failed-run-link")

    def get_top_checkbox(self) -> WebElement:
        """
        Gets the checkboxes for the top failed runs
        """
        return self.driver.find_element(By.XPATH, "//table/tbody/tr[1]/td[1]/input")

    def update_filter(self, filter_name, value):
        """
        Select a valid filter option.

        Args:
            filter_name: The name of the filter type being updated.

            value: The new value of the given filter.
        """
        Select(self.driver.find_element(By.ID, filter_name)).select_by_visible_text(value)

    def click_apply_button(self) -> None:
        """Click the `Apply` button."""
        btn = self.driver.find_element(By.ID, "runActionButton")
        btn.click()
