from . import impl as _impl


def window_rms(signal, window_length=None, max_frequency=1000, match_num_of_cycles_with_samples=True,
               assume_previous_data=False):
    '''Calculates RMS value of the signal using sliding window technique.
    User can specify "window_length" in seconds; the window length should represent the whole number of signal periods.
    The longer the "window_length" is, the longer will be initial transient during which the function doesn't provide
    valid rms value.
    If "window length" is not specified, the function will try to determine window_length by using Fast Fourier
    Transform to find dominant frequency - "window_length" will have length of the one signal period.
    There is also additional option to optimize window_length calculation; if "match_num_of_cycles_with_samples" is set,
    window_length will be calculated to cover the smallest number of signal periods which will ensure that calculated
    number of samples matches exactly the whole number of signal periods. This will make rms calculation more precize,
    but will also increase transient time at the beginning of the rms result.
    If "assume_previous_data" is set to True, the function will assume signal values before the provided ones; In this
    way, rms result will not have transient period during the first "window_length" seconds; rms result will have
    expected values from beginning.

    Parameters
    ----------
    signal : Series
        A Pandas Series with the signal the RMS value is to be calculated.
    window_length : float/int or Timedelta
        Duration in seconds (if float/int) of the window used in the calculation. Defaults to None, in which case the
        period of the strongest frequency found on the signal will be used for window period.
    max_frequency : float/int or Timedelta
        If 'window_length' is not defined, sets the maximum frequency to automatically detect the 'window_length' as
        one period of the signal's strongest frequency. Default: 1000
    match_num_of_cycles_with_samples: bool
        If 'window_length' is not defined, tries to match the 'window_length' with an integer number of cycles of the
        strongest frequency. Default: True
    assume_previous_data: bool
        If set, the return rms array will have valid values from beginning of function analysis. This is achieved
        by assuming that the signal in previous "window_length" seconds behaved exactly the same as in the first
        provided "window_length" seconds.
    Returns
    -------
    rms : Series
        Time series with the same length as signal with the calculated RMS value.

    Examples
    --------
    >>> from typhoon.test.signals import assert_is_constant, pandas_sine
    >>> from typhoon.test.rms import window_rms
    >>> from typhoon.test.ranges import around, after
    >>> from typhoon.types.timedelta import Timedelta as td
    >>> from numpy import sqrt

    >>> sine = pandas_sine(amplitude=220*sqrt(2), frequency=60)
    >>> period = td(1/60)
    >>> rms = window_rms(sine, period)
    >>> assert_is_constant(rms, at_value=around(220, tol_p=0.01), strictness=1, during=after(period))
    '''
    return _impl.window_rms(signal, window_length, max_frequency, match_num_of_cycles_with_samples,
                            assume_previous_data)
