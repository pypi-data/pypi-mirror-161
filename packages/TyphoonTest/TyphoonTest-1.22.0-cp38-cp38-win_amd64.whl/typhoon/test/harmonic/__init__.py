"""This package contains functions for frequency-domain operations and transformations."""
from . import impl as _impl
from .impl import FFTResult


def thd(signal, fundamental, max_harmonic, during=None, mode="multiple_harmonics_only", fundamental_tol=0.01):
    r"""Calculates signal THD

    Parameters
    ----------
    signal : Series
        A Pandas Series with the signal the THD value is to be calculated.
    fundamental : int
        Fundamental frequency of the signal
    max_harmonic : int
        Maximum harmonic (with respect to fundamental) to be taken into consideration in the calculation.
    during : 2-element tuple of float/int or Timedelta
        Period of signal to consider for the calculation.
    mode: string - default is 'multiple_harmonics_only'
        Selects one of three possible modes of calculation:
        - 'multiple_harmonics_only' - only harmonics which are divisible with fundamental are taken into consideration
        - 'with_interharmonics' - all harmonics bigger than fundamental are taken into consideration
        - 'all_frequencies' - all frequencies, including subharmonics are included in the calculation
    fundamental_tol : float - default 0.01
        Tolerance to replace provided 'fundamental' value by the one obtained from 'frequency_content' (FFT) of the signal.

    Returns
    -------
    thd : float
        Calculated THD value.

    Note
    ----
        All three calculation modes are based on fast fourier transform; this means that length of the signal which is
        taken into calculation should be chosen carefully, because this is the parameter which defines step between
        detected frequencies. consequently, if needed frequency step is 10Hz, signal should be captured(or sliced
        with during argument) to have length of 0.1s(1/10).

    Examples
    --------
    >>> from typhoon.test.signals import pandas_sine
    >>> from typhoon.test.harmonic import thd

    >>> # create 50 Hz sinusoidal signal - fundamental and add third harmonic
    >>> serie = signals.pandas_sine(1, 50, 1, 1e-6)
    >>> serie += signals.pandas_sine(0.5, 150, 1, 1e-6)
    >>> # add interharmonic
    >>> serie += signals.pandas_sine(1, 125, 1, 1e-6)
    >>> # add two subharmonics
    >>> serie += signals.pandas_sine(1, 10, 1, 1e-6)
    >>> serie += signals.pandas_sine(1, 30, 1, 1e-6)

    >>> # calculate thd with multiple harmonics only
    >>> result = thd(serie, fundamental=50, max_harmonic=10)
    >>> print(result) # prints 0.5

    >>> # calculate thd with interharmonics included
    >>> result = thd(serie, fundamental=50, max_harmonic=10, mode="with_interharmonics")
    >>> print(result) # 1 over sqrt(2)

    >>> # calculate thd with all frequencies included
    >>> result = thd(serie, fundamental=50, max_harmonic=10, mode="all_frequencies")
    >>> print(result) # prints 1
    """
    return _impl.thd(signal, fundamental, max_harmonic, during, mode, fundamental_tol)


def frequency_content(signal, max_frequency, during=None):
    """Calculates the list of harmonic components for a signal using FFT.

    Parameters
    ----------
    signal : Series
        A Pandas Series with the signal the harmonic components are to be calculated.
    max_frequency : int
        Maximum frequency to be taken into consideration in the results.
    during : 2-element tuple of float/int or Timedelta
        Period of signal to consider for the calculation.

    Returns
    -------
    result : FFTResult
        Result of the frequency analysis.

    Examples
    --------
    >>> import typhoon.test.signals as signals
    >>> import typhoon.test.harmonic as harmonic

    >>> serie = signals.pandas_sine(amplitude=100, frequency=60) # zeroed signal
    >>> serie += signals.pandas_sine(amplitude=10, frequency=120)
    >>> serie += signals.pandas_sine(amplitude=2, frequency=180)
    >>> content = harmonic.frequency_content(serie, 200)

    >>> plot(content.freqs, content.fft)
    >>> content(60)
    >>> content(10)
    >>> content(2)
    """
    return _impl.frequency_content(signal, max_frequency, during)

def signal_frequency_zc(signal, during=None, mode="half-cycle"):
    """Calculates frequency of the  signal.

    Measures time between neighboring zero-crossing moments. This method is suitable for sine, square or triangle
    signals. Returns pandas Series with the same length as signal. Frequency in the non-zero crossing moments is
    obtained by zero-order hold.

    Parameters
    ----------
    signal: Series
        A Pandas Series containing signal which frequency need to be calculated
    during : 2-element tuple of float/int or Timedelta
        Period of signal to consider for the calculation.
    mode: string
        String that activates one of two possible modes: for "half-cycle" every zero-crossing is detected, while for
        "full-cycle" every second zero-crossing is detected

    Returns
    -------
    result: pandas.Series
        Series with the calculated frequency values.

    Examples
    --------

    >>> import typhoon.test.signals as signals
    >>> import typhoon.test.harmonic as harmonic
    >>> # sine signal which lasts for one second, sampled 10000 times
    >>> series = signals.pandas_sine(amplitude=10, frequency=50, Ts=1e-4, duration=1)
    >>> frequency = harmonic.signal_frequency_zc(serie)
    returns the Series of the measured frequency(50). The length of the Series is 10000.
    """
    return _impl.signal_frequency_zc(signal, during, mode)