"""
This python package deals with logging of report messages to report, and with report organization in general.
"""

import allure


def report_message(message):
    """
    Logs message to the allure report. This function is used when just one simple report message should be logged to
    report. For organizing report steps in one logical group, look at ``typhoon.test.reporting.messages.report_step``
    function.

    Parameters
    ----------
    message: string
        Message to be logged in allure report.

    Returns
    -------
    None

    Examples
    --------
    >>> from typhoon.test.reporting.messages import *
    >>> # add message to report
    >>> report_message("Report message on the root level of the report")
    >>> # add composite report step with some report messages inside
    >>> with report_step("Report step which groups more report messages together"):
    >>>     report_message("Report message inside report step")
    >>>     report_message("Another report message inside report step")

    See Also
    --------
    typhoon.test.reporting.messages.report_step
    """
    with allure.step(message):
        pass


def report_step(message):
    """
    Adds message in allure report, like ``typhoon.test.reporting.messages.report_message`` function, but, in contrast to
    it, this function should be used to organize more functions and report messages in one logical
    group. It can be viewed as tool for better report organization.

    Parameters
    ----------
    message: string
        Message to be logged for the report step which unifies all the functions and messages called inside of it, in
        context manager manner.

    Returns
    -------
    None

    Examples
    --------
    >>> from typhoon.test.signals import pandas_sine
    >>> from typhoon.test.rms import window_rms
    >>> from typhoon.test.reporting.messages import *
    >>> # add report step for creating sinusoidal reference and computing its rms value
    >>> with report_step("Create sinusoidal reference and calculate its rms value:"):
    >>>     with report_step("Create reference:"):
    >>>         reference = pandas_sine(amplitude=100, frequency=50, phase=0, Ts=1e-6)
    >>>     with report_step("Calculate rms:"):
    >>>         rms = window_rms(reference, window_length=1/50, assume_previous_data=True)

    See Also
    --------
    typhoon.test.reporting.messages.report_message
    """
    return allure.step(message)