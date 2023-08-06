"""
This package contains function relevant to signal filtering
"""
from . import impl as _impl
import scipy.signal as signal

def moving_average(signal, window_length, assume_previous_data=False):
    """
    Calculates average value of the provided signal by using moving window technique, similar to
    'typhoon.test.rms.window_rms' function. User is specifying the size of the moving window in seconds with
    'window_length' argument. To get valid rms value, window size should represent whole number of signal periods.
    If "assume_previous_data" is set to True, the function will assume signal values before the provided ones; In this
    way, rms result will not have transient period during the first "window_length" seconds; rms result will have
    expected values from beginning. Otherwise, initial transient will be present during that period.

    Parameters
    ----------
    signal: pandas.Series
        pandas.Series which represents the signal which average value should be calculated.
    window_length: float
        Length of the moving window for average calculation, in seconds.
    assume_previous_data: bool - default True
        If set, the resulting average signal will have valid values from beginning of function analysis. This is
        achieved by assuming that the signal in previous "window_length" seconds behaved exactly the same as in the
        first provided "window_length" seconds.

    Returns
    -------
    result: pandas.Series
        The resulting signal which represents the instantaneous average of the provided one. The time indices of the
        input and output signals are identical.

    Examples
    --------
    >>> from typhoon.test.signals.filtering import moving_average
    >>> from typhoon.test.signals. import pandas_sine
    >>> # calculate average signal for the pure sine - the result will give zero signal
    >>> sine = pandas_sine(amplitude=100, frequency=50, Ts=1e-6)
    >>> average1 = moving_average(sine, window_length=1/50)
    >>> # create sine signal with some offset - moving_average detects that offset as average value
    >>> sine_offset = sine + 100
    >>> average2 = moving_average(sine_offset, window_length=1/50)

    See Also
    --------
    typhoon.test.rms.window_rms
    """
    return _impl.moving_average(signal, window_length, assume_previous_data)


def low_pass_filter(input_signal, N, Wn, analog=False, fs=None):
    """
    Wrapper around 'scipy.signal <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html>'
    function that represents Butterworth digital and analog filter design. It is used to design low-pass filter as
    Nth-order digital or analog Butterworth filter and return the filter coefficients.

    Parameters
    ----------
    signal: pandas.Series
        Input signal which should be filtered
    N: int
        The order of the filter.
    Wn: int/float
        The critical frequency. The point at which the gain drops to 1/sqrt(2) that of passband(the "-3 dB point").
    analog: bool, optional
        When True, analog filter is used for filtering, otherwise it is digital
    fs: float, optional
        The sampling frequency of the digital system.
    """
    return _impl.low_pass_filter(input_signal, N, Wn, analog, fs)


def high_pass_filter(input_signal, N, Wn, analog=False, fs=None):
    """
    Wrapper around 'scipy.signal <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html>'
    function that represents Butterworth digital and analog filter design. It is used to design high-pass filter as
    Nth-order digital or analog Butterworth filter and return the filter coefficients.

    Parameters
    ----------
    signal: pandas.Series
        Input signal which should be filtered
    N: int
        The order of the filter.
    Wn: int/float
        The critical frequency. The point at which the gain drops to 1/sqrt(2) that of passband(the "-3 dB point").
    analog: bool, optional
        When True, analog filter is used for filtering, otherwise it is digital
    fs: float, optional
        The sampling frequency of the digital system.
    """
    return _impl.high_pass_filter(input_signal, N, Wn, analog, fs)


def band_pass_filter(input_signal, N, Wn, analog=False, fs=None):
    """
    Wrapper around 'scipy.signal <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html>'
    function that represents Butterworth digital and analog filter design. It is used to design band-pass filter as
    Nth-order digital or analog Butterworth filter and return the filter coefficients.

    Parameters
    ----------
    signal: pandas.Series
        Input signal which should be filtered
    N: int
        The order of the filter.
    Wn: array-like
        The critical frequencies - length-2 sequence. The point at which the gain drops to 1/sqrt(2) that of
        passband(the "-3 dB point").
    analog: bool, optional
        When True, analog filter is used for filtering, otherwise it is digital
    fs: float, optional
        The sampling frequency of the digital system.
    """
    return _impl.band_pass_filter(input_signal, N, Wn, analog, fs)


def band_stop_filter(input_signal, N, Wn, analog=False, fs=None):
    """
    Wrapper around 'scipy.signal <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html>'
    function that represents Butterworth digital and analog filter design. It is used to design band-stop filter as
    Nth-order digital or analog Butterworth filter and return the filter coefficients.

    Parameters
    ----------
    signal: pandas.Series
        Input signal which should be filtered
    N: int
        The order of the filter.
    Wn: array-like
        The critical frequencies - length-2 sequence. The point at which the gain drops to 1/sqrt(2) that of
        passband(the "-3 dB point").
    analog: bool, optional
        When True, analog filter is used for filtering, otherwise it is digital
    fs: float, optional
        The sampling frequency of the digital system.
    """
    return _impl.band_stop_filter(input_signal, N, Wn, analog, fs)

