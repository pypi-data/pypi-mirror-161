# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Module for the accessibility statement page model
"""
from django.urls.base import reverse
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from autoreduce_frontend.selenium_tests.pages.component_mixins.footer_mixin import FooterMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.navbar_mixin import NavbarMixin
from autoreduce_frontend.selenium_tests.pages.page import Page


class AccessibilityStatementPage(Page, NavbarMixin, FooterMixin):
    """
    Page model class for accessibility statement page
    """

    @staticmethod
    def url_path() -> str:
        """
        Return the current URL of the page.
        :return: (str) the url path
        """
        return reverse("accessibility_statement")

    def _get_accessibility_statement_contents_element(self) -> WebElement:
        """
        Get the <div> #accessibility-statement-contents
        :return: (WebElement) The element #accessibility-statement-contents
        """
        return self.driver.find_element(By.ID, "accessibility-statement-contents")

    def is_accessibility_statement_visible(self) -> bool:
        """
        Is #accessibility-statement-contents visible
        :return: (str) True if #accessibility-statement-contents is visible else False
        """
        return self._get_accessibility_statement_contents_element().is_displayed()

    def get_accessibility_statement_contents_text(self) -> str:
        """
        Get the contents of #accessibility-statement-contents
        :return: (str) The text in #accessibility-statement-contents
        """
        return self._get_accessibility_statement_contents_element().text
