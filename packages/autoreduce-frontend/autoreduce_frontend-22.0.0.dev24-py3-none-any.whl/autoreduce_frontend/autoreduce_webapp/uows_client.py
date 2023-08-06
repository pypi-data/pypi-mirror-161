# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Client for accessing the user office logon."""
import logging

import suds
from suds.client import Client

# Below is a template on the repository
from autoreduce_frontend.autoreduce_webapp.settings import UOWS_URL

LOGGER = logging.getLogger(__package__)


class UOWSClient:
    """A client for interacting with the User Office Web Service."""

    def __init__(self, **kwargs):
        url = kwargs.get("URL", UOWS_URL)
        self.client = Client(url)

    # Add the ability to use 'with'
    def __enter__(self):
        return self

    def __exit__(self, _, value, traceback):
        pass

    def check_session(self, session_id):
        """Check if a session ID is still active and valid."""
        try:
            return self.client.service.isTokenValid(session_id)
        except suds.WebFault:
            LOGGER.warning("Session ID is not valid: %s", session_id)
            return False

    def get_person(self, session_id):
        """
        Return a dictionary containing basic person details for the user
        associated with the session id. Values include, first name, last name,
        email and unique usernumber. If session_id isn't valid, None is
        returned.
        """
        try:
            person = self.client.service.getPersonDetailsFromSessionId(session_id)
            if person:
                first_name = person.givenName
                if not first_name:
                    first_name = person.firstNameKnownAs
                trimmed_person = {
                    'first_name': first_name,
                    'last_name': person.familyName,
                    'email': person.email,
                    'usernumber': person.userNumber
                }
                return trimmed_person
        except suds.WebFault:
            LOGGER.warning("Session ID is not valid: %s", session_id)
        return None

    def logout(self, session_id):
        """
        End the session within the User Office Web Service.

        Note:
            This doesn't kill the local session.
        """
        try:
            self.client.service.logout(session_id)
        except suds.WebFault:
            LOGGER.warning("Failed to logout Session ID %s", session_id)
