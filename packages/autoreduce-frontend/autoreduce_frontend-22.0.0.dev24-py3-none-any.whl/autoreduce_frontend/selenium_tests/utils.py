# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
from typing import Optional, Tuple
import time
from autoreduce_db.reduction_viewer.models import ReductionRun, Status

from django.urls.base import reverse
from django.db.models import Q

from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.wait import WebDriverWait

from autoreduce_utils.clients.connection_exception import ConnectionException
from autoreduce_utils.clients.producer import Publisher

from autoreduce_qp.queue_processor.confluent_consumer import Consumer
from autoreduce_qp.model.database import access as db
from autoreduce_qp.queue_processor.confluent_consumer import setup_kafka_connections

from autoreduce_qp.systemtests.utils.data_archive import DataArchive

# pylint:disable=no-member


def find_run_in_database(test):
    """
    Find a ReductionRun record in the database
    This includes a timeout to wait for several seconds to ensure the database has received
    the record in question
    :return: The resulting record
    """
    instrument = db.get_instrument(test.instrument_name)
    if isinstance(test.run_number, list):
        return instrument.reduction_runs.filter(run_numbers__run_number__in=test.run_number,
                                                batch_run=test.batch_run_test).distinct()
    else:
        return instrument.reduction_runs.filter(run_numbers__run_number=test.run_number)


def submit_and_wait_for_result(test, expected_runs=1, after_submit_url: Optional[str] = None):
    """
    Submit after a reset button has been clicked. Then waits until the queue listener has finished processing.

    Sticks the submission in a loop in case the first time doesn't work. The reason
    it may not work is that resetting actually swaps out the whole form using JS, which
    replaces ALL the elements and triggers a bunch of DOM re-renders/updates, and that isn't fast.

    Args:
        expected_runs: The number of additional runs that should be in the database after the submission
        after_submit_url: The url to go to after the submission. If None, the default url is used.
    """
    test.consumer._processing = True  # pylint:disable=protected-access
    if not after_submit_url:
        expected_url = reverse("runs:run_confirmation", kwargs={"instrument": test.instrument_name})
    else:
        expected_url = after_submit_url

    def submit_successful(driver) -> bool:
        try:
            test.page.submit_button.click()
        except ElementClickInterceptedException:
            pass
        # the submit is successful if the URL has changed
        return expected_url in driver.current_url

    total_expected = ReductionRun.objects.count() + expected_runs
    WebDriverWait(test.driver, 30).until(submit_successful)

    start_time = time.time()
    while test.consumer.is_processing_message():
        time.sleep(5)
        if time.time() > start_time + 120:  # Prevent waiting indefinitely and break after 2 minutes
            break
    time.sleep(10)  # Wait for the message to be processed

    def runs_completed(_):
        # If your count is innacurate - check that the status of the runs
        # in the fixtures is not set to be "queued" by accident. Any other status will work.
        current = ReductionRun.objects.filter(~Q(status=Status.get_queued())
                                              & ~Q(status=Status.get_processing())).count()
        if current == total_expected:
            return True
        return False

    WebDriverWait(test.driver, 120).until(runs_completed, "Timed out while waiting for the runs to finish")

    return find_run_in_database(test)


def setup_external_services(instrument_name: str, start_year: int,
                            end_year: int) -> Tuple[DataArchive, Publisher, Consumer]:
    """
    Sets up a DataArchive complete with scripts, database client and queue client and listeners and returns their
    objects in a tuple
    :param instrument_name: Name of the instrument
    :param start_year: Start year for the archive
    :param end_year: End year for the archive
    :return: Tuple of external objects needed.
    """
    data_archive = setup_archive(instrument_name, start_year, end_year)
    try:
        publisher, consumer = setup_kafka_connections()
    except ConnectionException as err:
        raise RuntimeError("Could not connect to Kafka - check your broker. If running locally check that "
                           "the Kafka Docker container is running") from err

    return data_archive, publisher, consumer


def setup_archive(instrument_name: str, start_year: int, end_year: int) -> DataArchive:
    """Create a DataArchive."""
    data_archive = DataArchive([instrument_name], start_year, end_year)
    data_archive.create()

    return data_archive
