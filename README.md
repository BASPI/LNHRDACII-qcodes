# LNHR DAC II QCoDeS Driver
This repository contains the QCoDeS driver for the Basel Precision Instruments Low Noise High Resolution Digital to Analog Converter II or LNHR DAC II. Additionally there are some examples on how to use the driver.

## Latest Version
The latest version of this driver is v0.2.1. *We generally recommend to use the latest version of the driver to bring out the most of the LNHR DAC II.*

**What's new?**
- This new version adds additional functions for the QCoDeS driver:
    - Reconnect Function, after the connection has been lost, you are now able to reconnect to the DAC II without setting every channel off and all voltages to zero
- The most import functions of the LNHR DAC II are unchanged in comparison to v0.2.0:
    - Voltage, Bandwith and Enable of each channel
    - Arbitrary Waveform Generator (AWG), configurable through either manually setting points or using the Standard Waveform Generator (SWG) for fast creation of simple waveforms (sine, triangle, pulse, white noise and more)
    - Fast adaptive 2D-scan, with sampling rates as fast as 10 &mu;s per point, configurable through very easy to understand QCoDeS parameters. The video below shows an adaptive fast 2D-scan with 50000 points at live speed, done by the LNHRDAC II
 
https://github.com/user-attachments/assets/de2fac24-d2c0-4c25-9fb7-104f3bedb5a8


## Setup
Download `Baspi_Lnhrdac2.py` and `Baspi_Lnhrdac2_Controller.py` and copy it to your project folder. `qcodes_examples.ipynb` gives some examples on how the driver can be used.

## Older Releases
You can find older version of our driver under the `Releases` tab of this repository. Keep in mind that all versions prior to v0.2.0 differ significantly from later releases and are *not* a one-to-one replacement for anything after v0.2.0.
The changes between v0.2.0 to v0.2.1 are mostly incremental and therefore v0.2.1 can be used as one-to-one replacement for v0.2.0. 

We recommend using the latest version, especially if you want to take advantage of the full AWG functionallity of the DAC II.

## Further Documentation
See https://www.baspi.ch/manuals for more information on the LNHR DAC II.

See https://microsoft.github.io/Qcodes/ for more information about the QCoDeS framework.

If you have purchased an LNHR DAC II, you have received an USB stick, which includes the full documentation of the LNHR DAC II. Please be aware, that the official documentation of the LNHR DAC does not include any specific information on how to use the DAC with the QCoDeS framework. However, since the QCoDeS driver of the LNHR DAC II allows for full control of the device and is mainly an interface, the general documentation on the LNHR DAC II is still useful. The general documentation includes documentation about all commands available to the LNHR DAC II.

## Contributing
If you found a bug or are having a serious issue, please use the GitHub issue tracker to report it.
