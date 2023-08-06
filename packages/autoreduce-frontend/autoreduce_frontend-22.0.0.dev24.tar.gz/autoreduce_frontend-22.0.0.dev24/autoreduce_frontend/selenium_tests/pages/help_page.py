# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Module for the help summary page model
"""
from typing import List

from django.urls.base import reverse
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from autoreduce_frontend.selenium_tests.pages.component_mixins.footer_mixin import FooterMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.navbar_mixin import NavbarMixin
from autoreduce_frontend.selenium_tests.pages.page import Page


class HelpPage(Page, NavbarMixin, FooterMixin):
    """
    Page model class for help page
    """

    @staticmethod
    def url_path() -> str:
        """
        Return the current URL of the page.
        :return: (str) the url path
        """
        return reverse("help")

    def get_sidenav_contents_elements(self) -> List[WebElement]:
        """
        Get the contents of the sidenav.
        :return: (List) A list of <li> WebElements in #sidenav-contents
        """
        return self.driver.find_elements(By.XPATH, "//ul[@id='sidenav-contents']/li")

    def get_sidenav_contents(self) -> List[str]:
        """
        Get the contents of the sidenav as a list of strings.
        :return: (List) A list of strings inside of each <a> element
        """
        return [x.find_element(By.TAG_NAME, "a").text.strip() for x in self.get_sidenav_contents_elements()]

    def get_help_topic_elements(self) -> List[WebElement]:
        """
        Get the help topics
        :return: (List) A list of <section> WebElements of class .help-topic
        """
        return self.driver.find_elements(By.CLASS_NAME, "help-topic")

    def get_each_help_topic_category(self) -> List[str]:
        """
        Get each data-category value from each help topic
        :return: (List) A list of categories from each help topic
        """
        return [x.get_attribute("data-category") for x in self.get_help_topic_elements()]

    def get_each_help_topic_content(self) -> List[str]:
        """
        Get each content text for each help topic
        :return: (List) A list of topic contents
        """
        return [x.find_element(By.CLASS_NAME, "card-body").text for x in self.get_help_topic_elements()]

    def get_help_topic_header_elements(self) -> List[WebElement]:
        """
        Get the help topic headers
        :return: (List) A list of <div> WebElements of class .card-header
        """
        return [x.find_element(By.XPATH, "./div[@class='card-header']") for x in self.get_help_topic_elements()]

    def get_help_topic_header_link_elements(self) -> List[WebElement]:
        """
        Get the help topic headers link elements
        :return: (List) A list of WebElement links found in the headers of help topics
        """
        return [x.find_element(By.XPATH, "./h3/a") for x in self.get_help_topic_header_elements()]

    def get_each_help_topic_header(self) -> List[str]:
        """
        Get the headers of the help topics.
        :return (List) A list of help topic headers
        """
        return [x.find_element(By.XPATH, "./h3/a").text.strip() for x in self.get_help_topic_header_elements()]

    def get_category_filter_elements(self) -> List[WebElement]:
        """
        Get the category filter elements in #category-filter
        :return: (List) A list of filter elements
        """
        return self.driver.find_elements(By.XPATH, "//div[@id='category-filter']/label")

    def get_help_topic_filters(self) -> List[str]:
        """
        Get the help topic filters from the category filter
        :return: (List) A list of categories
        """
        return [x.get_attribute("data-category").strip() for x in self.get_category_filter_elements()]

    def get_available_help_topic_categories(self) -> List[str]:
        """
        Get the available categories for topics on the page
        :return: (List) A list of categories
        """
        filters = self.get_help_topic_filters()
        filters.remove("all")
        return filters

    def click_category_filter(self, category):
        """
        Click a category filter button
        :param category: (str) The category name to select
        """
        filter_button = next(
            (x for x in self.get_category_filter_elements() if x.get_attribute("data-category") == category), None)

        if filter_button is None:
            raise Exception(f"Category {category} does not exist.")

        filter_button.click()

    def filter_help_topics_by_search_term(self, text):
        """
        Filter help topics by a search term using fuzzy search
        :param text: The search term to enter into #help-search
        """
        help_search = self.driver.find_element(By.ID, "help-search")
        help_search.clear()
        help_search.send_keys(text)

    def clear_search_box(self):
        """
        Clear the text in the search box
        """
        help_search = self.driver.find_element(By.ID, "help-search")
        help_search.clear()
        help_search.send_keys(Keys.BACKSPACE)  # Send onKeyUp event to #help-search

    def get_visible_help_topic_elements(self) -> List[WebElement]:
        """
        Get the visible help topics on the page
        :return: (List) A list of help topics that are not display:none
        """
        return [x for x in self.get_help_topic_elements() if x.is_displayed()]
