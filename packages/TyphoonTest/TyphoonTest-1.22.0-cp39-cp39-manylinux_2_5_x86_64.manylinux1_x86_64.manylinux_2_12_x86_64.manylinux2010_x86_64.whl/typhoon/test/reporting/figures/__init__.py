"""
This packages contains functions for attachment of matplotlib figures to allure reports
"""

from . import impl as _impl


def attach_figure(dataframe_list, attachment_name, attach_as_step=False):
    """
    Adds matplotlib figure of provided signals in the allure report as .png image
    attachment. Signals of interest are provided as list of pandas.Dataframe objects; every DataFrame is plotted on
    designated subplot. Attachment is added as new report step with provided 'attachment_name' argument as step message.

    Parameters
    ----------
    dataframe_list: list
        List of pandas.DataFrame or pandas.Series objects which contain signals of interest. Every DataFrame object
        groups signals which should be present on the same subplot.
    attachment_name: string
        Name with which this attachment will be added to allure report.
    attach_as_step: bool - default False
        If set to False, figure is added at the end of the report, no matter when in test it is actually attached. This
        is default allure behaviour, all the attachments are added at the end of the report. To overwrite this
        behaviour and place attachment in the report chronologically in the moment when it is added, it must be
        added in the separate report step. This is achieved by setting this argument to True.

    Returns
    -------
    None

    Examples
    --------
    >>> from typhoon.test.reporting.figures import attach_figure
    >>> from typhoon.test.signals import pandas_3ph_sine
    >>> # create voltage and current three-phase signals
    >>> voltages = pandas_3ph_sine(amplitude=100, frequency=50, Ts=1e-6)
    >>> currents = pandas_3ph_sine(amplitude=30, frequency=50, phase=30, Ts=1e-6)
    >>> # attach figure of voltages and currents to allure report
    >>> attach_figure([voltages, currents], attachment_name="Grid signals")
    """
    _impl.attach_figure(dataframe_list, attachment_name, attach_as_step)