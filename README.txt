#Ventilator Logger
This is the home directory for the serial COM/USB based logger for the Datex-Ohmeda Aestiva/5 7900 ventilator. The protocol is based on the Ohmeda COM 1.0 Serial Protocol, Version 1.5 (August 14th, 2001). 

In the home directory there must be a token.auth file with the redcap connection details which include the first line is the "OR" string. Second line is the renpoint (HTTPS://...), and the third line is the REDCap API token which must be kept a secret.

RedCap Instrument Structure (CSV)
"Variable / Field Name","Form Name","Section Header","Field Type","Field Label","Choices, Calculations, OR Slider Labels","Field Note","Text Validation Type OR Show Slider Number","Text Validation Min","Text Validation Max",Identifier?,"Branching Logic (Show field only if...)","Required Field?","Custom Alignment","Question Number (surveys only)","Matrix Group Name","Matrix Ranking?","Field Annotation"
record_id,form_1,,text,"Record ID",,,,,,,,,,,,,
or,form_1,,text,or,,"Which operating room",,,,,,,,,,,
datetime,form_1,,text,datetime,,datetime,datetime_seconds_ymd,,,,,,,,,,
meas_tidal_vol,form_1,,text,"Measured Tidal Volume",,ml,,,,,,,,,,,
meas_minute_vol,form_1,,text,"Measured Minute Volume",,"L * 100",,,,,,,,,,,
meas_rr,form_1,,text,"Measured Respiratory Rate",,"per min",,,,,,,,,,,
meas_o2,form_1,,text,"Measured Oxygen",,%,,,,,,,,,,,
meas_max_pres,form_1,,text,"Measured Max Pressure",,"cm H2O",,,,,,,,,,,
meas_insp_plat,form_1,,text,"Measured Inspiratory Plateau Pressure",,"cm H2O",,,,,,,,,,,
meas_mean_pres,form_1,,text,"Measured Mean Pressure",,"cm H2O",,,,,,,,,,,
meas_min_pres,form_1,,text,"Measured Min Pressure",,"cm H2O",,,,,,,,,,,
set_tidal_volume,form_1,,text,"Set Tidal Volume",,ml,,,,,,,,,,,
set_rr,form_1,,text,"Set Respiratory Rate",,"per min",,,,,,,,,,,
set_itoe,form_1,,text,"Set I:E Ratio",,,,,,,,,,,,,
set_peep,form_1,,text,"Set PEEP",,"cm H2O",,,,,,,,,,,
set_insp_pres,form_1,,text,"Set Inspiratory Pressure",,"cm H2O",,,,,,,,,,,
set_vent_mode,form_1,,text,"Set Ventilator Mode",,Pressure/Volume/Bag,,,,,,,,,,,
