# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Module for the help summary page model
"""

from django.urls.base import reverse
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

from autoreduce_frontend.selenium_tests.pages.component_mixins.footer_mixin import FooterMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.navbar_mixin import NavbarMixin
from autoreduce_frontend.selenium_tests.pages.page import Page


class GenerateTokenFormPage(Page, NavbarMixin, FooterMixin):
    """
    Page model class for help page
    """

    @staticmethod
    def url_path() -> str:
        """
        Return the current URL of the page.
        :return: (str) the url path
        """
        return reverse("token:generate")

    def click_generate_token(self) -> WebElement:
        """Clicks generate in the token generation page"""
        return self.driver.find_element(By.ID, "generate-token-submit").click()

    def generate_form_users(self) -> Select:
        """Grabs the users Select field in the generate new token form"""
        return Select(self.driver.find_element(By.ID, "id_user"))
