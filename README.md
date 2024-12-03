# Experimental Pre-Release of the LNHR DAC II QCoDeS Driver
This repository contains the QCoDeS driver for the Basel Precision Instruments *Low Noise High Resolution Digital to Analog Converter II* or *LNHR DAC II*. Additionally there are some examples of to use the driver.

## Latest Release
This is an experimental version of the LNHR DAC II QCoDeS driver. Not everything is extensively tested. All code may be subject to change.

We are currently working on an improved version of the driver. Once it releases the newest features and changes will be listed here.

## Setup
This code is an improved version of the original Basel Precision Instruments LNHR DAC II QCoDeS driver. Everything should be backwards compatible. `baspi_lnhrdac2.py`replaces the old `DAC_1060_v060723.py`and `qcodes_gate_parameters.py`replaces the old `Parameterhelp_240709.py`. Additionally `qcodes_examples.ipynb` gives some examples on how the driver can be used. Copy the files into your project folder and change the filenames in the import section of your code to run this new experimental pre-release of the QCoDeS driver.

## Further Documentation
See https://www.baspi.ch/manuals for more information on the LNHR DAC II.

See https://microsoft.github.io/Qcodes/ for more information about the QCoDeS framework.

If you have purchased an LNHR DAC II, you have received an USB stick, which includes the full documentation of the LNHR DAC II. Please be aware, that the official documentation of the LNHR DAC does not include any specific information on how to use the DAC with the QCoDeS framework. However, since the QCoDeS driver of the LNHR DAC II allows for full control of the device and is mainly an interface, the general documentation on the LNHR DAC II is still useful. The general documentation includes documentation about all commands available to the LNHR DAC II.

## Contributing
If you found a bug or are having a serious issue, please use the GitHub issue tracker to report it.