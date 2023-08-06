"""
This package is used for different electric power calculations.
"""
from . import impl as _impl


def three_phase_power(voltages, currents, window_length=1/50):
    """
    Calculates three phase power for three-phase systems with both three and four wires. Calculation is based on
    instantaneous power theory. Compared to conventional power theory, which is using voltage and current rms values to
    compute power values, which makes it valid only for steady state analysis, instantaneous power theory utilizes
    instantaneous voltage and current values to compute instantaneous real, reactive and zero power. Consequently,
    this theory is useful for both transient and steady-state analysis, which is more suitable for power electronics
    applications.

    Inputs are phase voltages and phase currents of the observed three-phase system, while the output is
    pandas.DataFrame with 8 signals:

    - Pinst - instantaneous real power;
    - Qinst - instantaneous reactive power;
    - P0inst - instantaneous zero power;
    - Pavg - average value of the instantaneous real power, calculated with moving average function: see
        'typhoon.test.signals.filtering.moving_average;
    - Qavg - average value of the instantaneous reactive power, calculated with the same moving average principle;
    - P0avg - average value of the instantaneous zero power, calculated with the same moving average principle;
    - S - apparent power, calculated as the sqrt(Pavg^2 + Qavg^2);
    - pf - power factor, calculated as the ratio between average real power and apparent power

    Parameters
    ----------
    voltages: pandas.DataFrame
        DataFrame containing three columns, one for every phase voltage
    currents: pd.DataFrame
        DataFrame containing three columns, one for every phase current
    window_length: float - default 1/50
        Value that defines size of the window that is used for calculating average power values from instantaneous ones.
        To get the valid result for average powers, window_length should last for whole number of voltage periods.
        Defaults to 1/50, which is one period for the 50Hz signal.

    Returns
    -------
    result: pandas.DataFrame
        DataFrame containing all eight output signals that are already mentioned. Appropriate signals can be selected
        by using same labels which are mentioned in signal explanation above: Pinst, Qinst, P0inst, Pavg, Qavg, P0avg,
        S and pf respectively.

    Examples
    --------
    >>> from typhoon.test.signals import pandas_3ph_sine
    >>> from typhoon.test.power import three_phase_power
    >>> import numpy as np
    >>> # create voltages and currents DataFrame, which represents three phase system whose power is being measured
    >>> voltages = pandas_3ph_sine(amplitude=100*np.sqrt(2), frequency=50, Ts=1e-6)
    >>> currents = pandas_3ph_sine(amplitude=100*np.sqrt(2), frequency=50, Ts=1e-6, phase=45)
    >>> # calculate three phase power
    >>> powers = three_phase_power(voltages, currents)
    >>> # select all power signals
    >>> p_inst = powers["Pinst"]
    >>> q_inst = powers["Qinst"]
    >>> p0_inst = powers["P0inst"]
    >>> p_avg = powers["Pavg"]
    >>> q_avg = powers["Qavg"]
    >>> p0_avg = powers["Pinst"]
    >>> s = powers["S"]
    >>> pf = powers["pf"]

    See Also
    --------
    typhoon.test.signals.filtering.moving_average
    """
    return _impl.three_phase_power(voltages, currents, window_length)
