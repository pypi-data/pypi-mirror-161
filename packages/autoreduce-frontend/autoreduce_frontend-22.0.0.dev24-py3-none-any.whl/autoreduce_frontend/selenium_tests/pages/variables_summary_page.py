# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #

from typing import List
from functools import partial

from django.urls import reverse
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from autoreduce_frontend.selenium_tests.pages.component_mixins.footer_mixin import FooterMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.navbar_mixin import NavbarMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.tour_mixin import TourMixin
from autoreduce_frontend.selenium_tests.pages.page import Page


class VariableSummaryPage(Page, NavbarMixin, FooterMixin, TourMixin):
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
        return reverse("runs:variables_summary", kwargs={
            "instrument": self.instrument,
        })

    @property
    def current_arguments_by_run(self) -> WebElement:
        """Return the current_arguments_by_run panel"""
        return self.driver.find_element(By.ID, "current_arguments_by_run")

    @property
    def upcoming_arguments_by_run(self) -> WebElement:
        """Return the upcoming_arguments_by_run panel"""
        return self.driver.find_element(By.ID, "upcoming_arguments_by_run")

    @property
    def upcoming_arguments_by_experiment(self) -> WebElement:
        """Return the upcoming_arguments_by_experiment panel"""
        return self.driver.find_element(By.ID, "upcoming_arguments_by_experiment")

    def _do_run_button(self, url):

        def run_button_clicked_successfully(button, url, driver):
            button.click()
            return url in driver.current_url

        button = self.driver.find_element(By.CSS_SELECTOR, f'[href*="{url}"]')
        WebDriverWait(self.driver, 10).until(partial(run_button_clicked_successfully, button, url))

    def _do_delete_button(self, url):

        def delete_button_clicked_successfully(button, _):
            try:
                button.click()
                return False
            except StaleElementReferenceException:
                return True

        button = self.driver.find_element(By.CSS_SELECTOR, f'[href*="{url}"]')
        WebDriverWait(self.driver, 10).until(partial(delete_button_clicked_successfully, button))

    def click_run_edit_button_for(self, start: int):
        """
        Click the edit button for the given run start and end
        :param start: The start run
        :param end: The end run
        :return: The edit button
        """
        url = reverse("runs:variables", kwargs={"instrument": self.instrument, "start": start})
        self._do_run_button(url)

    def click_run_delete_button_for(self, start: int, end: int):
        """
        Click the delete button for the given run start and run end
        :param start: The start run
        :param end: The end run
        :return: The delete button
        """
        url = reverse("runs:delete_variables", kwargs={"instrument": self.instrument, "start": start, "end": end})
        self._do_delete_button(url)

    def click_experiment_edit_button_for(self, experiment_reference: int):
        """
        Get the edit button for the given experiment reference
        :param experiment_reference: The experiment reference
        :return: The edit button
        """
        url = reverse("runs:variables_by_experiment",
                      kwargs={
                          "instrument": self.instrument,
                          "experiment_reference": experiment_reference
                      })
        self._do_run_button(url)

    def click_experiment_delete_button_for(self, experiment_reference: int):
        """
        Get the delete button for the given experiment reference
        :param experiment_reference: The experiment refence
        :return: The delete button
        """
        url = reverse("runs:delete_variables_by_experiment",
                      kwargs={
                          "instrument": self.instrument,
                          "experiment_reference": experiment_reference
                      })
        self._do_delete_button(url)

    @property
    def panels(self) -> List[WebElement]:
        """Return the variable summary panels"""
        return self.driver.find_elements(By.CLASS_NAME, "card-body")
