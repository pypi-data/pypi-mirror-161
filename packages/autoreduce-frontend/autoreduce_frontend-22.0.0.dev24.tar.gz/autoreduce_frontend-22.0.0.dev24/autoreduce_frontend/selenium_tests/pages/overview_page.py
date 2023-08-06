# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Module for the overview page model
"""
from django.urls.base import reverse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.wait import WebDriverWait

from autoreduce_frontend.selenium_tests import configuration
from autoreduce_frontend.selenium_tests.pages.component_mixins.footer_mixin import FooterMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.navbar_mixin import NavbarMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.tour_mixin import TourMixin
from autoreduce_frontend.selenium_tests.pages.runs_list_page import RunsListPage
from autoreduce_frontend.selenium_tests.pages.page import Page


class OverviewPage(Page, NavbarMixin, FooterMixin, TourMixin):
    """
    Overview page model class
    """

    def __init__(self, driver):
        super().__init__(driver)
        self.step = 0

    def launch(self):
        """
        This is a bit of a hack to get around the fact that you will only be logged in when
        connecting to / and not /overview. Once we have a better way to simulate logging in on the
        dev/local environments we can remove this method and add proper logging in methods and tests
        """
        self.driver.get(configuration.get_url())
        self.driver.get(self.url())
        WebDriverWait(self.driver, 10).until(presence_of_element_located((By.CLASS_NAME, "instrument-btn")))
        return self

    @staticmethod
    def url_path():
        """
        Return the path section of the overview page url
        :return: (str) Path section of the page url
        """
        return reverse("overview")

    def _get_instrument_buttons(self):
        return self.driver.find_elements(By.CLASS_NAME, "instrument-btn")

    def get_instruments_from_buttons(self):
        """
        Gets the names of the instruments which have buttons on the overview page
        :return: (List) The instrument names which have buttons on the overview page
        """
        return [instrument_btn.get_attribute("id").split("-")[0] for instrument_btn in self._get_instrument_buttons()]

    def click_instrument(self, instrument: str) -> RunsListPage:
        """
        Clicks the instrument button for the given instrument
        :param instrument: (str) instrument name
        :return: (InstrumentSummaryPage) The overview page object
        """
        self.driver.find_element(By.ID, f"{instrument}-instrument-btn").click()
        return RunsListPage(self.driver, instrument)
