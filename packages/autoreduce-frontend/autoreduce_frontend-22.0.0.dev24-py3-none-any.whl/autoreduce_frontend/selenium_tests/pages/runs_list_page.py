# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Module for the instrument summary page model."""
from typing import List

from django.urls import reverse
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

from autoreduce_frontend.selenium_tests.pages.component_mixins.footer_mixin import FooterMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.navbar_mixin import NavbarMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.tour_mixin import TourMixin
from autoreduce_frontend.selenium_tests.pages.page import Page
from autoreduce_frontend.selenium_tests.pages.run_summary_page import RunSummaryPage


class RunsListPage(Page, NavbarMixin, FooterMixin, TourMixin):
    """Page model class for instrument summary page."""

    def __init__(self, driver, instrument):
        super().__init__(driver)
        self.instrument = instrument

    def url_path(self):
        """Return the path section of the instrument url."""
        return reverse("runs:list", kwargs={"instrument": self.instrument})

    def get_run_numbers_from_table(self) -> List[str]:
        """
        Return the list of run numbers visible on the current table of the
        instrument summary page.
        """
        return [run.text.split(" - ")[0] for run in self.driver.find_elements(By.CLASS_NAME, "run-num-links")]

    def get_experiments_from_table(self) -> List[str]:
        """
        Return the list of run numbers visible on the current table of the
        instrument summary page.
        """
        return [run.text.split(" - ")[0] for run in self.driver.find_elements(By.CLASS_NAME, "experiment-num-links")]

    def get_created_from_table(self) -> List[str]:
        """
        Return the list of created dates visible on the current table of the
        instrument summary page.
        """
        return [run.text.split(" - ")[0] for run in self.driver.find_elements(By.CLASS_NAME, "created-dates")]

    def get_status_from_table(self) -> List[str]:
        """
        Return the list of status' visible on the current table of the
        instrument summary page.
        """
        return [run.text.split(" - ")[0] for run in self.driver.find_elements(By.CLASS_NAME, "run-status")]

    def click_run(self, run_number: int, version: int = 0) -> RunSummaryPage:
        """
        Click a run and return the page object of its run summary.

        Args:
            run_number: Run number of the link to click.

            version: Version of the run to click.

        Returns:
            The page object of the opened run summary.
        """
        runs = self.driver.find_elements(By.XPATH, "//div[@class='table-container']/table/tbody/tr/td/a")
        run_string = f"{run_number} - {version}" if version else f"{run_number}"
        for run in runs:
            if run.text == run_string:
                run.click()
                return RunSummaryPage(self.driver, self.instrument, run_number, version)

        raise NoSuchElementException

    def variables_alert_message_text(self) -> str:
        """
        Return the text of the alert message element with the id
        'variable_alert_message'.
        """
        return self.driver.find_element(By.ID, "variables_alert_message").text.strip()

    def get_top_run(self) -> WebElement:
        """Return the element with the id 'top-run-number'."""
        return self.driver.find_element(By.XPATH, "//div[@class='table-container']/table/tbody/tr[1]/td[1]/a")

    def click_btn_by_title(self, title: str) -> None:
        """
        Click the button matching the given title.

        Note:
            This method is being used to navigate instrument summary pages as
            there is no `find_element_by_title` method and the instrument
            summary navigation buttons have no id attributes.
        """
        btns = self.driver.find_elements(By.TAG_NAME, "button")

        for btn in btns:
            if btn.get_attribute("title") == title:
                btn.click()
                break
        else:
            raise NoSuchElementException

    def click_next_page_button(self) -> None:
        """
        Click next page pagination button
        """
        btn = self.driver.find_element(By.XPATH, "//li[@class='next page-item']/a")
        btn.click()

    def click_prev_page_button(self) -> None:
        """
        Click previous page pagination button
        """
        btn = self.driver.find_element(By.XPATH, "//li[@class='prev page-item']/a")
        btn.click()

    def update_filter(self, filter_name, value):
        """
        Select a valid filter option.

        Args:
            filter_name: The name of the filter type being updated.

            value: The new value of the given filter.
        """
        Select(self.driver.find_element(By.ID, filter_name)).select_by_visible_text(value)

    def click_apply_filters(self) -> None:
        """Click the `Apply filters` button."""
        btn = self.driver.find_element(By.ID, "apply_filters")
        btn.click()

    @property
    def top_alert_message_text(self):
        """Finds and returns the alert message shown at the top of the runs list page"""
        return self.driver.find_element(By.ID, "top-alert-message").text
