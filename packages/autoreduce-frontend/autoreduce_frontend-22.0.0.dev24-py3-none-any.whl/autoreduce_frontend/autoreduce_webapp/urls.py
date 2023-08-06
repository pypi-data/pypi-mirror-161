# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
# pylint: disable=invalid-name,redefined-builtin
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path, register_converter

from autoreduce_frontend.reduction_viewer.views import (accessibility_statement, experiment_summary, graph, help, index,
                                                        logout, overview, stats, search)


class NegativeIntConverter:
    regex = r'-?\d+'

    @staticmethod
    def to_python(value):
        """Return the value as a Python object."""
        return int(value)

    @staticmethod
    def to_url(value):
        """Return the value as a URL string."""
        return f'{value}'


register_converter(NegativeIntConverter, 'negint')

urlpatterns = [
    # ===========================MISC================================= #
    path('', index.index, name='index'),
    path('admin/', admin.site.urls),
    path('logout/', logout.logout, name='logout'),
    path('help/', help.help, name='help'),
    path('accessibility_statement/', accessibility_statement.accessibility_statement, name='accessibility_statement'),

    # ===========================RUNS================================= #
    path('overview/', overview.overview, name='overview'),
    path('runs/', include('reduction_viewer.urls')),

    # ===========================EXPERIMENT========================== #
    path('experiment/<negint:reference_number>/', experiment_summary.experiment_summary, name='experiment_summary'),

    # ===========================SCRIPTS============================= #
    path('graph/', graph.graph_home, name="graph"),
    path('graph/<str:instrument_name>', graph.graph_instrument, name="graph_instrument"),
    path('stats/', stats.stats, name="stats"),

    # =======================GENERATE TOKEN========================== #
    path('tokens/', include('generate_token.urls')),
    path('search/', search.search, name='search'),
]

if settings.DEBUG_TOOLBAR_AVAILABLE:
    urlpatterns = [
        path('__debug__/', include("debug_toolbar.urls")),
    ] + urlpatterns
