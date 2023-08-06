# # ############################################################################### #
# # Autoreduction Repository : https://github.com/autoreduction/autoreduce
# #
# # Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# # SPDX - License - Identifier: GPL-3.0-or-later
# # ############################################################################### #
"""
Unit tests for the script which determines the natural time difference between
the start and end of a run.
"""
import datetime
import unittest

from parameterized import parameterized

from autoreduce_frontend.autoreduce_webapp.templatetags.natural_time_difference import NaturalTimeDifferenceNode


class TestNaturalTimeDifference(unittest.TestCase):
    START_DATETIME = datetime.datetime.strptime('Jun 1 2021  8:33AM', '%b %d %Y %I:%M%p')

    def _test_time_difference(self, end, expected):
        """Helper function for asserting a condition."""
        natural_time_difference = NaturalTimeDifferenceNode("run.started", "run.finished")
        duration = natural_time_difference.get_duration(TestNaturalTimeDifference.START_DATETIME, end)
        self.assertEqual(duration, expected)

    def test_difference_none(self):
        """Test that no time difference returns an empty string."""
        self._test_time_difference(TestNaturalTimeDifference.START_DATETIME, "0 seconds")

    @parameterized.expand([
        [START_DATETIME + datetime.timedelta(seconds=1), "1 second"],
        [START_DATETIME + datetime.timedelta(seconds=2), "2 seconds"],
        [START_DATETIME + datetime.timedelta(seconds=5), "5 seconds"],
        [START_DATETIME + datetime.timedelta(seconds=59), "59 seconds"],
    ])
    def test_difference_seconds(self, end, expected):
        """
        Test that a time difference of fewer than 60 seconds returns a string
        only containing seconds.
        """
        self._test_time_difference(end, expected)

    @parameterized.expand([
        [START_DATETIME + datetime.timedelta(minutes=1, seconds=0), "1 minute"],
        [START_DATETIME + datetime.timedelta(minutes=2, seconds=0), "2 minutes"],
        [START_DATETIME + datetime.timedelta(minutes=1, seconds=1), "1 minute, 1 second"],
        [START_DATETIME + datetime.timedelta(minutes=1, seconds=2), "1 minute, 2 seconds"],
        [START_DATETIME + datetime.timedelta(minutes=2, seconds=1), "2 minutes, 1 second"],
        [START_DATETIME + datetime.timedelta(minutes=59, seconds=59), "59 minutes, 59 seconds"],
    ])
    def test_difference_minutes(self, end, expected):
        """
        Test that a time difference of fewer than 60 minutes returns a string
        only containing minutes and possibly seconds.
        """
        self._test_time_difference(end, expected)

    @parameterized.expand([
        [START_DATETIME + datetime.timedelta(hours=1, minutes=0, seconds=0), "1 hour"],
        [START_DATETIME + datetime.timedelta(hours=2, minutes=0, seconds=0), "2 hours"],
        [START_DATETIME + datetime.timedelta(hours=1, minutes=0, seconds=1), "1 hour, 1 second"],
        [START_DATETIME + datetime.timedelta(hours=1, minutes=0, seconds=1), "1 hour, 1 second"],
        [START_DATETIME + datetime.timedelta(hours=2, minutes=1, seconds=1), "2 hours, 1 minute, 1 second"],
        [START_DATETIME + datetime.timedelta(hours=23, minutes=1, seconds=1), "23 hours, 1 minute, 1 second"],
        [START_DATETIME + datetime.timedelta(hours=23, minutes=59, seconds=59), "23 hours, 59 minutes, 59 seconds"],
    ])
    def test_difference_hours(self, end, expected):
        """
        Test that a time difference of fewer than 24 hours returns a string
        only containing hours and possibly minutes and seconds.
        """
        self._test_time_difference(end, expected)

    @parameterized.expand([
        [START_DATETIME + datetime.timedelta(days=1, hours=0, minutes=0, seconds=0), "1 day"],
        [START_DATETIME + datetime.timedelta(days=2, hours=0, minutes=0, seconds=0), "2 days"],
        [START_DATETIME + datetime.timedelta(days=1, hours=0, minutes=0, seconds=1), "1 day, 1 second"],
        [START_DATETIME + datetime.timedelta(days=1, hours=0, minutes=1, seconds=0), "1 day, 1 minute"],
        [START_DATETIME + datetime.timedelta(days=1, hours=1, minutes=0, seconds=0), "1 day, 1 hour"],
        [START_DATETIME + datetime.timedelta(days=1, hours=1, minutes=0, seconds=1), "1 day, 1 hour, 1 second"],
        [START_DATETIME + datetime.timedelta(days=1, hours=0, minutes=1, seconds=1), "1 day, 1 minute, 1 second"],
        [START_DATETIME + datetime.timedelta(days=1, hours=1, minutes=1, seconds=0), "1 day, 1 hour, 1 minute"],
        [
            START_DATETIME + datetime.timedelta(days=1, hours=1, minutes=1, seconds=1),
            "1 day, 1 hour, 1 minute, 1 second"
        ],
        [
            START_DATETIME + datetime.timedelta(days=200, hours=23, minutes=59, seconds=59),
            "200 days, 23 hours, 59 minutes, 59 seconds"
        ],
    ])
    def test_difference_days(self, end, expected):
        """
        Test that a time difference over or equal to 24 hours returns a string
        only containing days and possibly hours, minutes, and seconds.
        """
        self._test_time_difference(end, expected)
