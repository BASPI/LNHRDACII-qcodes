# LNHR DAC II QCoDeS Driver
This repository contains the QCoDeS driver for the Basel Precision Instruments Low Noise High Resolution Digital to Analog Converter II or LNHR DAC II. Additionally there are some examples on how to use the driver.

## Latest Version
The latest version of this driver is v0.2.1.

**What's new?**
- This new version adds additional functions for our QCoDeS driver. The structure of the driver did not change in general and still works as before.
- The most import functions of the LNHR DAC II are still easily accessible through QCoDeS parameters:
    - Voltage, Bandwith and Enable of each channel
    - Arbitrary Waveform Generator (AWG), configurable through either manually setting points or using the Standard Waveform Generator (SWG) for fast creation of simple waveforms (sine, triangle, pulse, white noise and more)
    - Fast adaptive 2D-scan, with sampling rates as fast as 10 &mu;s per point, configurable through very easy to understand QCoDeS parameters. The video below shows an adaptive fast 2D-scan with 50000 points at live speed, done by the LNHRDAC II
 
https://github.com/user-attachments/assets/de2fac24-d2c0-4c25-9fb7-104f3bedb5a8


**NOW NEW**
- Reconnect Function ():
  after the connection has been lost, you are now able to reconnect to the DAC II without setting every channel off and all voltages to zero

This version of the driver aims not to be a one by one replacement for the earlier versions of the driver. We recommend starting a new project if you are using this version of the driver. Make sure to check out the example Notebooks to get started. If you have any issues with the driver, please use the GitHub issue tracker to report it, or get in contact with us.

## Setup
Download `Baspi_Lnhrdac2.py` and `Baspi_Lnhrdac2_Controller.py` and copy it to your project folder. `qcodes_examples.ipynb` gives some examples on how the driver can be used.

## Older Releases
If you want to use an older version of our driver, you can find them in the `Releases` tab of this repository. Be advised that everything before v0.2.0 is vastly different than everything after v0.2.0. 
However, the changes between v0.2.0 and v0.2.1 are relatively small and mostly incremental.

## Further Documentation
See https://www.baspi.ch/manuals for more information on the LNHR DAC II.

See https://microsoft.github.io/Qcodes/ for more information about the QCoDeS framework.

If you have purchased an LNHR DAC II, you have received an USB stick, which includes the full documentation of the LNHR DAC II. Please be aware, that the official documentation of the LNHR DAC does not include any specific information on how to use the DAC with the QCoDeS framework. However, since the QCoDeS driver of the LNHR DAC II allows for full control of the device and is mainly an interface, the general documentation on the LNHR DAC II is still useful. The general documentation includes documentation about all commands available to the LNHR DAC II.

## Contributing
If you found a bug or are having a serious issue, please use the GitHub issue tracker to report it.
