# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #

from collections import namedtuple

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

from autoreduce_frontend.autoreduce_webapp.templatetags.encode_b64 import encode_b64

ResetButtons = namedtuple('ResetButtons', ["to_initial", "to_script"])


class RerunFormMixin:

    @staticmethod
    def _set_field(field, value):
        field.clear()
        new_value = value
        field.send_keys(new_value)

    @property
    def cancel_button(self) -> WebElement:
        """
        Finds and returns the back button for toggling the form on the page.
        """
        return self.driver.find_element(By.ID, "cancel")

    @property
    def submit_button(self) -> WebElement:
        """
        Finds and returns the back button for toggling the form on the page.
        """
        return self.driver.find_element(By.ID, "variableSubmit")

    @property
    def variable1_field(self) -> WebElement:
        """
        Finds and returns the variable1 field
        """
        return self.driver.find_element(By.ID, f"var-standard-{encode_b64('variable1')}")

    @property
    def variable1_field_val(self) -> WebElement:
        """
        Finds and returns the variable1 field value
        """
        return self.variable1_field.get_attribute("value")

    @property
    def variable1_field_reset_buttons(self) -> ResetButtons:
        """
        Finds and returns the inline reset buttons for the variable1 field
        """
        buttons = self.driver.find_elements(By.CSS_SELECTOR, f"[data-for=var-standard-{encode_b64('variable1')}]")
        assert len(
            buttons
        ) == 2, "Found more elements with that selector that expected, further test assertions will not work properly"
        return ResetButtons(*buttons)

    @variable1_field.setter
    def variable1_field(self, value) -> None:
        """
        Clears the field and sends the keys to the input field.

        Selenium requires that we clear the field first!
        """
        self._set_field(self.variable1_field, value)

    @property
    def variable_str_field(self) -> WebElement:
        """
        Finds and returns the variable string field
        """
        return self.driver.find_element(By.ID, f"var-standard-{encode_b64('variable_str')}")

    @property
    def variable_str_field_val(self) -> WebElement:
        """
        Finds and returns the variable string field value
        """
        return self.variable_str_field.get_attribute("value")

    @variable_str_field.setter
    def variable_str_field(self, value) -> None:
        """
        Clears the field and sends the keys to the input field.

        Selenium requires that we clear the field first!
        """
        self._set_field(self.variable_str_field, value)

    @property
    def variable_int_field(self) -> WebElement:
        """
        Finds and returns the variable int field
        """
        return self.driver.find_element(By.ID, f"var-standard-{encode_b64('variable_int')}")

    @property
    def variable_int_field_val(self) -> WebElement:
        """
        Finds and returns the variable int field value
        """
        return self.variable_int_field.get_attribute("value")

    @variable_int_field.setter
    def variable_int_field(self, value) -> None:
        """
        Clears the field and sends the keys to the input field.

        Selenium requires that we clear the field first!
        """
        self._set_field(self.variable_int_field, value)

    @property
    def variable_float_field(self) -> WebElement:
        """
        Finds and returns the variable float field
        """
        return self.driver.find_element(By.ID, f"var-standard-{encode_b64('variable_float')}")

    @property
    def variable_float_field_val(self) -> WebElement:
        """
        Finds and returns the variable float field value
        """
        return self.variable_float_field.get_attribute("value")

    @variable_float_field.setter
    def variable_float_field(self, value) -> None:
        """
        Clears the field and sends the keys to the input field.

        Selenium requires that we clear the field first!
        """
        self._set_field(self.variable_float_field, value)

    @property
    def variable_listfloat_field(self) -> WebElement:
        """
        Finds and returns the variable list of ints field
        """
        return self.driver.find_element(By.ID, f"var-standard-{encode_b64('variable_listfloat')}")

    @property
    def variable_listfloat_field_val(self) -> WebElement:
        """
        Finds and returns the variable list of ints field value
        """
        return self.variable_listfloat_field.get_attribute("value")

    @variable_listfloat_field.setter
    def variable_listfloat_field(self, value) -> None:
        """
        Clears the field and sends the keys to the input field.

        Selenium requires that we clear the field first!
        """
        self._set_field(self.variable_listfloat_field, value)

    @property
    def variable_listint_field(self) -> WebElement:
        """
        Finds and returns the variable list of ints field
        """
        return self.driver.find_element(By.ID, f"var-standard-{encode_b64('variable_listint')}")

    @property
    def variable_listint_field_val(self) -> WebElement:
        """
        Finds and returns the variable list of ints field value
        """
        return self.variable_listint_field.get_attribute("value")

    @variable_listint_field.setter
    def variable_listint_field(self, value) -> None:
        """
        Clears the field and sends the keys to the input field.

        Selenium requires that we clear the field first!
        """
        self._set_field(self.variable_listint_field, value)

    @property
    def variable_liststr_field(self) -> WebElement:
        """
        Finds and returns the variable list of str field
        """
        return self.driver.find_element(By.ID, f"var-standard-{encode_b64('variable_liststr')}")

    @property
    def variable_liststr_field_val(self) -> WebElement:
        """
        Finds and returns the variable list of str field value
        """
        return self.variable_liststr_field.get_attribute("value")

    @variable_liststr_field.setter
    def variable_liststr_field(self, value) -> None:
        """
        Clears the field and sends the keys to the input field.

        Selenium requires that we clear the field first!
        """
        self._set_field(self.variable_liststr_field, value)

    @property
    def variable_none_field(self) -> WebElement:
        """
        Finds and returns the variable None field
        """
        return self.driver.find_element(By.ID, f"var-standard-{encode_b64('variable_none')}")

    @property
    def variable_none_field_val(self) -> WebElement:
        """
        Finds and returns the variable None field value
        """
        return self.variable_none_field.get_attribute("value")

    @variable_none_field.setter
    def variable_none_field(self, value) -> None:
        """
        Clears the field and sends the keys to the input field.

        Selenium requires that we clear the field first!
        """
        self._set_field(self.variable_none_field, value)

    @property
    def variable_empty_field(self) -> WebElement:
        """
        Finds and returns the variable empty field
        """
        return self.driver.find_element(By.ID, f"var-standard-{encode_b64('variable_empty')}")

    @property
    def variable_empty_field_val(self) -> WebElement:
        """
        Finds and returns the variable empty field value
        """
        return self.variable_empty_field.get_attribute("value")

    @variable_empty_field.setter
    def variable_empty_field(self, value) -> None:
        """
        Clears the field and sends the keys to the input field.

        Selenium requires that we clear the field first!
        """
        self._set_field(self.variable_empty_field, value)

    @property
    def variable_bool_field(self) -> Select:
        """
        Finds and returns the variable bool field
        """
        return Select(self.driver.find_element(By.ID, f"var-standard-{encode_b64('variable_bool')}"))

    @property
    def variable_bool_field_val(self) -> Select:
        """
        Finds and returns the variable bool field value
        """
        return self.variable_bool_field.first_selected_option.text

    @variable_bool_field.setter
    def variable_bool_field(self, value: str) -> None:
        """
        Clears the field and sends the keys to the input field.

        Selenium requires that we clear the field first!
        """
        self.variable_bool_field.select_by_visible_text(value)

    @property
    def variable_list_no_brackets_field(self) -> WebElement:
        """
        Finds and returns the variable list of str field
        """
        return self.driver.find_element(By.ID, f"var-standard-{encode_b64('variable_list_no_brackets')}")

    @property
    def variable_list_no_brackets_field_val(self) -> WebElement:
        """
        Finds and returns the variable list of str field value
        """
        return self.variable_list_no_brackets_field.get_attribute("value")

    @variable_list_no_brackets_field.setter
    def variable_list_no_brackets_field(self, value) -> None:
        """
        Clears the field and sends the keys to the input field.

        Selenium requires that we clear the field first!
        """
        self._set_field(self.variable_list_no_brackets_field, value)
