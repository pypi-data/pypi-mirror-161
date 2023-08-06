# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Node for handling replacing
"""
from django.template import Library, Node, Variable, TemplateSyntaxError

from autoreduce_frontend.autoreduce_webapp.templatetags.common_helpers import get_var

register = Library()


class ReplaceNode(Node):
    """
    Node for replacing text
    """

    def __init__(self, text, old, new):
        self.text = Variable(text)
        self.old = Variable(old)
        self.new = Variable(new)

    def render(self, context):
        """
        Render the replace text Node
        """
        text = str(get_var(self.text, context))
        old = str(get_var(self.old, context))
        new = str(get_var(self.new, context))
        return text.replace(old, new)


@register.tag
def replace(_, token):
    """
    Return the ReplaceNode
    """
    args = token.split_contents()[1:]
    if len(args) != 3:
        raise TemplateSyntaxError(f'{token.contents.split()[0]} tag requires a string, an old value, and a new value.')
    return ReplaceNode(*args)
