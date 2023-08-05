import matplotlib.pyplot as plt
from ds1052 import DS1052, PointsMode, TriggerStatus

with DS1052() as dso:
    # Acquire the waveform of channel 1 in "normal" points mode
    # which returns 600 data points.
    waveform = dso.read_waveforms([1], PointsMode.normal)[0]
    # waveform.t is a numpy array with time axis values. 0 is the trigger
    # time.
    # waveform.v is a numpy array with the voltage values.
    plt.plot(waveform.t, waveform.v)
    print(
        f'vertical scale: {waveform.v_scale}V/div '
        f'vertical offset: {waveform.v_offset}V')
    print(
        f'timebase scale: {waveform.tb_scale}s/div '
        f'timebase offset: {waveform.tb_offset}s')
plt.show()
