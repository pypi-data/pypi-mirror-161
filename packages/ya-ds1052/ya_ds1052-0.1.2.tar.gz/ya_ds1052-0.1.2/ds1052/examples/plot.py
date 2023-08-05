#!/usr/bin/env python

"""Let the DS1052 find reasonable settings for the actual signals (equivalent
to pressing the AUTO button) and acquire waveforms for both channels.

Connect for example the probe adjustment signal of the DSO to both inputs.
"""

import sys
try:
    import matplotlib.pyplot as plt
except ImportError:
    print('matplotlib is required to run this test.')
from ds1052 import DS1052, PointsMode, TriggerStatus


if __name__ == '__main__':
    with DS1052() as dso:
        # Acquire waveforms for channel 1 and 2 in "normal" points mode
        # which returns 600 data points.
        w1, w2 = dso.read_waveforms((1, 2), PointsMode.normal)
    print(
        f'time base scale: %{w1.tb_scale}s/div '
        f'time base offset: %{w1.tb_offset}s')
    print(f'channel 1 scale: %{w1.v_scale}V/div offset: {w1.v_offset}')
    print(f'channel 2 scale: %{w2.v_scale}V/div offset: {w2.v_offset}')

    color = 'tab:red'
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('CH1 (V)', color=color)
    ax1.plot(w1.t, w1.v, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    color = 'tab:blue'
    ax2 = ax1.twinx()
    ax2.set_ylabel('CH2 (V)', color=color)
    ax2.plot(w2.t, w2.v, color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    # Set the vertical range of both curves to values that result in a
    # similar image as shown on the DSO's own display.
    ax1.set_ylim(
        (- 4 * w1.v_scale - w1.v_offset, 4 * w1.v_scale - w1.v_offset))
    ax2.set_ylim(
        (- 4 * w2.v_scale - w2.v_offset, 4 * w2.v_scale - w2.v_offset))
    plt.show()
