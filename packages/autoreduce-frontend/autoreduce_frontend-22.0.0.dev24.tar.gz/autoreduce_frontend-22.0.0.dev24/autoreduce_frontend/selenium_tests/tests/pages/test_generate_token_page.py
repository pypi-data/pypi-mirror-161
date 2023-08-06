from rest_framework.authtoken.models import Token

from autoreduce_frontend.selenium_tests.tests.base_tests import (BaseTestCase, FooterTestMixin, NavbarTestMixin,
                                                                 AccessibilityTestMixin)
from autoreduce_frontend.selenium_tests.pages.generate_token.list_page import GenerateTokenListPage


class TestGenerateTokenPage(BaseTestCase, NavbarTestMixin, FooterTestMixin, AccessibilityTestMixin):
    """
    Test cases for the error page
    """
    fixtures = BaseTestCase.fixtures + ["additional_users"]

    def setUp(self) -> None:
        """
        Sets up the ErrorPage object
        """
        super().setUp()
        self.page = GenerateTokenListPage(self.driver)
        self.page.launch()
        self._action_generate_token()

    def _action_generate_token(self):
        form_page = self.page.click_generate_token()
        form_page.generate_form_users().select_by_visible_text("(super)")
        form_page.click_generate_token()

    def test_generate_token_for_user(self):
        """
        Generate token for user with the expected name
        """
        usernames = self.page.token_usernames()
        assert len(usernames) == 1
        assert usernames[0].text == "(super)"

    def test_generate_and_view(self):
        """
        Generate a token and click the eye to reveal it
        """
        token_values = self.page.token_values()
        assert len(token_values) == 1
        assert "Click eye to reveal" in token_values[0].text
        assert "or copy to clipboard" in token_values[0].text

        eye_views = self.page.token_eye_views()
        token_values = self.page.token_values()
        assert len(eye_views) == 1
        eye_views[0].click()

        token_values = self.page.token_values()
        assert len(token_values) == 1
        assert str(Token.objects.first()) in token_values[0].text

    def test_generate_and_delete(self):
        """Generate a token and delete it"""
        delete_page = self.page.click_delete_first()
        delete_page.click_delete_token()

        token_values = self.page.token_values()
        assert len(token_values) == 0
        assert Token.objects.count() == 0

    def test_generate_and_copy(self):
        """
        Generate a token, copy it to the clipboard, then paste it and verify the value.

        The pasting appends a new element in the window, calls CTRL+V on it, then compares its value to the token value.
        """
        token_values = self.page.token_values()
        assert len(token_values) == 1
        assert "Click eye to reveal" in token_values[0].text
        assert "or copy to clipboard" in token_values[0].text

        clipboards = self.page.token_copy_clipboards()
        token_values = self.page.token_values()
        assert len(clipboards) == 1
        clipboards[0].click()

        self.page.paste_and_verify(str(Token.objects.first()))

    def test_users_label_correct(self):
        """
        Test that users with first_name and last_name are displayed correctly
        """
        # clear all premade tokens
        Token.objects.all().delete()
        form_page = self.page.click_generate_token()
        # 3 because top option is ------, and then the 2 users from the fixture
        assert len(form_page.generate_form_users().options) == 3
        assert form_page.generate_form_users().options[0].text == "---------"
        assert form_page.generate_form_users().options[1].text == "(super)"
        assert form_page.generate_form_users().options[2].text == "Test User (123456)"
