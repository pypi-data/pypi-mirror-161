# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #

from django.urls import path
from autoreduce_frontend.autoreduce_webapp.view_utils import login_and_uows_valid
from autoreduce_frontend.reduction_viewer.views import (run_queue, run_summary, runs_list, fail_queue, run_confirmation,
                                                        variables, pause, configure_new_batch_run, configure_new_runs,
                                                        rerun_jobs)

app_name = "runs"

urlpatterns = [
    path('queue/', run_queue.run_queue, name='queue'),
    path('failed/', fail_queue.fail_queue, name='failed'),
    path('<str:instrument>/', runs_list.runs_list, name='list'),
    path('<str:instrument_name>/<int:run_number>/', run_summary.run_summary, name='summary'),
    path('<str:instrument_name>/batch/<int:pk>/', run_summary.run_summary_batch_run, name='batch_summary'),
    path('<str:instrument_name>/batch/<int:pk>/<int:run_version>/',
         run_summary.run_summary_batch_run,
         name='batch_summary'),
    path('<str:instrument_name>/<int:run_number>/<int:run_version>/', run_summary.run_summary, name='summary'),
    path('<str:instrument>/rerun_jobs/', rerun_jobs.rerun_jobs, name='rerun_jobs'),
    path('<str:instrument>/configure_batch_run/',
         login_and_uows_valid(configure_new_batch_run.BatchRunSubmit.as_view()),
         name='configure_batch_run'),
    path('<str:instrument>/configure_new_runs/', configure_new_runs.configure_new_runs, name='variables'),
    path('<str:instrument>/configure_new_runs/<int:start>/', configure_new_runs.configure_new_runs, name='variables'),
    path('<str:instrument>/variables_summary/', variables.instrument_variables_summary, name='variables_summary'),
    path('<str:instrument>/variables/<int:start>/<int:end>/delete',
         variables.delete_instrument_variables,
         name='delete_variables'),
    path('<str:instrument>/variables/experiment/<int:experiment_reference>/',
         configure_new_runs.configure_new_runs,
         name='variables_by_experiment'),
    path('<str:instrument>/variables/experiment/<int:experiment_reference>/delete/',
         variables.delete_instrument_variables,
         name='delete_variables_by_experiment'),
    path('<str:instrument>/pause/', pause.instrument_pause, name='pause'),
    path('<str:instrument>/confirmation/', run_confirmation.run_confirmation, name='run_confirmation'),
]
