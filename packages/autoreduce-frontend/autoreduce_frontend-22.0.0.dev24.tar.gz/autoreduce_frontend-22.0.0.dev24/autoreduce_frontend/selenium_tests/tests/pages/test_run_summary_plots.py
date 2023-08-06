# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Selenium tests for the runs summary page
"""

import os
import tempfile

from autoreduce_db.reduction_viewer.models import ReductionRun

from autoreduce_frontend.selenium_tests.pages.run_summary_page import RunSummaryPage
from autoreduce_frontend.selenium_tests.tests.base_tests import BaseTestCase


# pylint:disable=no-member,consider-using-with
class TestRunSummaryPagePlots(BaseTestCase):
    """
    Test cases for the InstrumentSummary page when the Rerun form is NOT visible
    """

    fixtures = BaseTestCase.fixtures + ["one_run_plot"]

    def setUp(self) -> None:
        """
        Set up the instrument name and page
        """
        super().setUp()
        self.instrument_name = "TESTINSTRUMENT"

        self.page = RunSummaryPage(self.driver, self.instrument_name, 99999, 0)
        self.run = ReductionRun.objects.first()

    def test_plot_files_png(self):
        """
        Test: PNG plot files are fetched and shown
        """
        # the plot files are expected to be in the reduction location, so we write them there for the test to work
        plot_files = [
            tempfile.NamedTemporaryFile(prefix="data_",
                                        suffix=".png",
                                        dir=self.run.reduction_location.first().file_path),
            tempfile.NamedTemporaryFile(prefix="data_",
                                        suffix=".png",
                                        dir=self.run.reduction_location.first().file_path)
        ]
        self.page.launch()

        # 1 is the logo, the other 2 are the plots
        images = self.page.images()
        assert len(images) == 3
        for img in images[1:]:
            alt_text = img.get_attribute("alt")
            assert "Plot image stored at" in alt_text
            assert any(os.path.basename(f.name) in alt_text for f in plot_files)

    def test_plot_files_json(self):
        """
        Test: JSON plot files are fetched and rendered by plotly
        """
        # the plot files are expected to be in the reduction location, so we write them there for the test to work
        plot_files = []

        for _ in range(2):
            # pylint:disable=consider-using-with
            tfile = tempfile.NamedTemporaryFile('w',
                                                prefix="data_",
                                                suffix=".json",
                                                dir=self.run.reduction_location.first().file_path)
            tfile.write("""{"data": [{"type": "bar","x": [1,2,3],"y": [1,3,2]}]}""")
            tfile.flush()
            plot_files.append(tfile)

        self.page.launch()

        plots = self.page.plotly_plots()
        assert len(plots) == 2
        for plot in plots:
            assert any(plot.get_attribute("id") in file.name for file in plot_files)

    def test_plot_files_mix(self):
        """Test that both static and interactive plots are rendered"""
        plot_files = [
            tempfile.NamedTemporaryFile(prefix="data_",
                                        suffix=".png",
                                        dir=self.run.reduction_location.first().file_path),
            tempfile.NamedTemporaryFile('w',
                                        prefix="data_",
                                        suffix=".json",
                                        dir=self.run.reduction_location.first().file_path)
        ]
        # write the interactive plot data
        plot_files[1].write("""{"data": [{"type": "bar","x": [1,2,3],"y": [1,3,2]}]}""")
        plot_files[1].flush()

        self.page.launch()

        images = self.page.images()
        # 1 is the logo, the other is the static plot
        assert len(images) == 2

        img = images[1]
        alt_text = img.get_attribute("alt")
        assert "Plot image stored at" in alt_text
        assert any(os.path.basename(f.name) in alt_text for f in plot_files)

        plots = self.page.plotly_plots()
        assert len(plots) == 1
        assert plots[0].get_attribute("id") in plot_files[1].name
