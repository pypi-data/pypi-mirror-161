# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
from typing import List
from django.urls.base import reverse
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from autoreduce_frontend.selenium_tests.pages.generate_token.delete_page import DeleteTokenFormPage
from autoreduce_frontend.selenium_tests.pages.component_mixins.footer_mixin import FooterMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.navbar_mixin import NavbarMixin
from autoreduce_frontend.selenium_tests.pages.page import Page
from autoreduce_frontend.selenium_tests.pages.generate_token.generate_page import GenerateTokenFormPage


class GenerateTokenListPage(Page, NavbarMixin, FooterMixin):
    """
    Page model class for help page
    """

    @staticmethod
    def url_path() -> str:
        """
        Return the current URL of the page.
        :return: (str) the url path
        """
        return reverse("token:list")

    def click_generate_token(self) -> GenerateTokenFormPage:
        """
        Get the contents of the sidenav.
        :return: (List) A list of <li> WebElements in #sidenav-contents
        """
        self.driver.find_element(By.ID, "generate-token").click()
        return GenerateTokenFormPage(self.driver)

    def token_usernames(self) -> List[WebElement]:
        """Return the usernames for all generated tokens"""
        return self.driver.find_elements(By.CLASS_NAME, "token-user")

    def token_values(self) -> List[WebElement]:
        """
        Return the values for all generated tokens

        Note: this doesn't return the literal token value, but the field which
        the user can click to reveal/copy the value
        """
        return self.driver.find_elements(By.CLASS_NAME, "token-value")

    def click_delete_first(self) -> DeleteTokenFormPage:
        """Clicks the delete on the first token"""
        token_deletes = self.driver.find_elements(By.CLASS_NAME, "token-delete")
        token_deletes[0].click()
        return DeleteTokenFormPage(self.driver)

    def token_eye_views(self) -> List[WebElement]:
        """Return all "eye" icons, that reveal the value of the token"""
        return self.driver.find_elements(By.CLASS_NAME, "fa-eye")

    def token_copy_clipboards(self) -> List[WebElement]:
        """Return all "clipboard" icons, that copy to clipboard"""
        return self.driver.find_elements(By.CLASS_NAME, "fa-clipboard")

    def paste_and_verify(self, expected: str):
        """
        Pastes the value of the clipboard and verifies that it matches the expected parameter

        Done by creating a new textarea element, pasting the value in it with CTRL+V, then
        comparing against the expected parameter.

        A bit of a workaround, but way easier & understandable than accessing the system clipboard!
        """
        self.driver.execute_script("""
        let obj = document.createElement("textarea");
        obj.id="selenium-test";
        document.body.appendChild(obj);
        """)
        obj = self.driver.find_element(By.ID, "selenium-test")
        obj.send_keys(Keys.CONTROL, "v")
        assert obj.get_attribute("value") == expected
