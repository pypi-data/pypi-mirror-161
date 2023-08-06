"""
This module contains basic control blocks implementations
"""

# pyximport is needed to compile dynamically
import typhoon.utils.environment as tytest_env
if tytest_env.is_run_from_source():
    import pyximport
    pyximport.install()

from . import impl as _impl
import pandas


def integrator(input, initial_value, limit_output=False, max_limit=None, min_limit=None):
    """
    Integrates provided input signal. It is implemented by using Backward Euler method.

    Parameters
    ----------
    input: pandas.Series with timedelta index values
        Input signal to be integrated.
    initial_value: int, float
        Initial value of the integrated output signal
    limit_output: bool
        If set to True, limits the output signal. In this case, parameters max_limit and min_limit have to be specified.
    max_limit: int, float
        If limit_output argument is specified, this value limits the output from the upper side. Otherwise, it doesn't
        take effect.
    min_limit: int, float
        If limit_output argument is specified, this value limits the output from the lower side. Otherwise, it doesn't
        take effect.

    Returns
    -------
    result: pandas.Series
    """
    return _impl.integrator(input, initial_value, limit_output, max_limit, min_limit)

