## Changelog

### 0.1.2
- New method DS1052.screenshot(): Retrieves a BMP image from the DS1052.
- Property DS1052.channel[<ch>].filter_enabled: Raise DS1052PropertySetError
  on attempts to set this property while the DS1052 is in "stop" mode.
- Improved range check of DS1052.trigger.{edge,pulse,video}.level:
  Only allow values in the range (-6 * v_scale .. 6 * v_scale) - v_offset
  where v_scale and v_offset are the vertical scale/offset ot the tirgger
  source.
- Same check as above for DS1052.trigger.slope.voltage_level_lower
  and DS1052.trigger.slope.voltage_level_upper.
- classes TriggerModeSettingsEdge, TriggerModeSettingsPulse,
  TriggerModeSettingsVideo, TriggerModeSettingsSlope,
  TriggerModeSettingsAlternation, Trigger, Channel, _Channels, DS1052:
  Methods get_config() and set_config() added.
- New properties Channel.offset_range, Channel.trigger_level_range
  Channel.scale_range
- Property Channel.offset: Incorrect calculation of value limits fixed.

### 0.1.1
First public release
