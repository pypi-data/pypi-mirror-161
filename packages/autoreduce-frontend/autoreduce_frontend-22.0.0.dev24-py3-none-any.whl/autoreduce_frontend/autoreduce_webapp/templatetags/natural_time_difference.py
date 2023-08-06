# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Render the time difference between two given times."""
# pylint:disable=invalid-name
from django.template import Library, Node, Variable, TemplateSyntaxError
from django.template.defaultfilters import pluralize

from autoreduce_frontend.autoreduce_webapp.templatetags.common_helpers import get_var

register = Library()


class NaturalTimeDifferenceNode(Node):
    """Class for computing and rendering time differences."""

    def __init__(self, start, end):
        self.start = Variable(start)
        self.end = Variable(end)

    @staticmethod
    def get_duration(start, end):
        """Return the time difference as a string."""
        delta = end - start
        days = delta.days
        hours = delta.seconds // 3600
        minutes = delta.seconds // 60 % 60
        seconds = delta.seconds % 60

        if not any((days, hours, minutes, seconds)):
            return "0 seconds"

        duration = ''
        for time, unit in ((days, "day"), (hours, "hour"), (minutes, "minute"), (seconds, "second")):
            if time > 0:
                if duration:
                    duration += ', '
                duration += f"{time} {unit}{pluralize(time)}"

        return duration

    def render(self, context):
        """Render the response."""
        start = get_var(self.start, context)
        end = get_var(self.end, context)
        return self.get_duration(start, end)


def natural_time_difference(_, token):
    """Return NaturalTimeDifference Node."""
    args = token.split_contents()[1:]
    if len(args) != 2:
        raise TemplateSyntaxError(f'{token.contents.split()[0]} tag requires two datetimes.')
    return NaturalTimeDifferenceNode(*args)


register.tag('natural_time_difference', natural_time_difference)
