# coding=utf-8
"""Styles used for pretty printing
"""

from modelscript.libs.termcolor import colored

__all__ = (
    'Style',
    'Styles'
)


class Style(object):
    """Style made of a color, a background and some attributes."""

    def __init__(self, c=None, b=None, a=None):
        self.color = c
        self.background = b
        self.attributes = a

    def do(self, text, styled=True):
        if styled:
            return colored(text,
                           color=self.color,
                           on_color=self.background,
                           attrs=self.attributes)
        else:
            return text


class Styles(object):
    """Libraru of predefined styles."""

    bigIssue = Style('red', a=['bold'])
    mediumIssue = Style('magenta', a=['bold'])
    smallIssue = Style('green')
    bigIssueSummary = Style('red', a=['reverse','bold'])
    smallIssueSummary = Style('magenta', a=['reverse','bold'])

    keyword = Style('blue')
    comment = Style('white')
    highlight = Style('red')
    blue = Style('blue', a=['reverse'])
    annotate = Style('yellow')
    s2 = Style('green')
    bold = Style(a=['bold'])
    no = Style()
    ko = Style('red')
    ok = Style('green')
