# Alpha Version 0.2.0 LNHR DAC II QCoDeS Driver
This repository branch contains an untested version of a driver. Any use of it is strongly discouraged. Everything in this branch could break your system and/or your hardware. BASPI is not liable for any damage caused.

## Latest Release
The latest version of this driver is v0.1.1.

**What's new?**
- We greatly improved the general code documentation.
- We now provide some examples for you in the  form of a Jupyter Notebook. It should help with understanding and setting up our QCoDeS driver.
- Names of files and methods have been changed to better fall in line with the general QCoDeS guidelines, while the old method names still work.
- The `write` method has been improved. It now does a simple handshaking with the DAC and raises an error if the DAC could not process a command. It also implements some necessary delays to avoid race conditions.

This version of the driver aims to be a one by one replacement for the original version of the driver. Make sure to change the the filenames in the import section of your code. If you have any issues with that, please use the GitHub issue tracker to report it, or get in contact with us.

## Setup
This code is an improved version of the original Basel Precision Instruments LNHR DAC II QCoDeS driver. Everything should be backwards compatible. `baspi_lnhrdac2.py`replaces the old `DAC_1060_v060723.py`and `qcodes_gate_parameters.py`replaces the old `Parameterhelp_240709.py`. Additionally `qcodes_examples.ipynb` gives some examples on how the driver can be used. Copy the files into your project folder and change the filenames in the import section of your code to run this new experimental pre-release of the QCoDeS driver.

## Older Releases
If you want to use an older version of our driver, you can find them in the Releases tab of this repository.

## Further Documentation
See https://www.baspi.ch/manuals for more information on the LNHR DAC II.

See https://microsoft.github.io/Qcodes/ for more information about the QCoDeS framework.

If you have purchased an LNHR DAC II, you have received an USB stick, which includes the full documentation of the LNHR DAC II. Please be aware, that the official documentation of the LNHR DAC does not include any specific information on how to use the DAC with the QCoDeS framework. However, since the QCoDeS driver of the LNHR DAC II allows for full control of the device and is mainly an interface, the general documentation on the LNHR DAC II is still useful. The general documentation includes documentation about all commands available to the LNHR DAC II.

## Contributing
If you found a bug or are having a serious issue, please use the GitHub issue tracker to report it.