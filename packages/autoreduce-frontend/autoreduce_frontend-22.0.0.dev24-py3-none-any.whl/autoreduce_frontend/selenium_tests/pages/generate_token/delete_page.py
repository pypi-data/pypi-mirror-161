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
from selenium.webdriver.common.by import By

from autoreduce_frontend.selenium_tests.pages.component_mixins.footer_mixin import FooterMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.navbar_mixin import NavbarMixin
from autoreduce_frontend.selenium_tests.pages.page import Page


class DeleteTokenFormPage(Page, NavbarMixin, FooterMixin):
    """
    Page model class for help page
    """

    @staticmethod
    def url_path() -> str:
        """
        Return the current URL of the page.
        :return: (str) the url path
        """
        return reverse("token:delete")

    def click_delete_token(self) -> WebElement:
        """Clicks the delete token in the delete confirmation page"""
        return self.driver.find_element(By.ID, "generate-token-delete").click()
