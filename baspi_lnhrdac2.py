# ----------------------------------------------------------------------------------------------------------------------------------------------
# LNHR DAC II QCoDeS driver
# v0.2.0
# Copyright (c) Basel Precision Instruments GmbH (2024)
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the 
# Free Software Foundation, either version 3 of the License, or any later version. This program is distributed in the hope that it will be 
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details. You should have received a copy of the GNU General Public License along with this program.  
# If not, see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------------------------------------------------------------------------

# imports --------------------------------------------------------------

from Baspi_Lnhrdac2_Controller import BaspiLnhrdac2Controller
from Baspi_Lnhrdac2_Parser import BaspiLnhrdac2Parser as parser

from qcodes.station import Station
from qcodes.instrument import VisaInstrument, InstrumentChannel, ChannelList
from qcodes.parameters import create_on_off_val_mapping
import qcodes.validators as validate

from functools import partial
from time import sleep

# logging --------------------------------------------------------------

import logging

log = logging.getLogger(__name__)

# class ----------------------------------------------------------------

class BaspiLnhrdac2Channel(InstrumentChannel):

    def __init__(self, 
                 parent: VisaInstrument, 
                 name: str, 
                 channel: int, 
                 controller: BaspiLnhrdac2Controller):
        """
        Class that defines a channel of the LNHR DAC II with all its QCoDeS-parameters.

        Channel-Parameters:
        Voltage (-10.0 V ... +10.0 V)
        High Bandwidth (ON/True: 100 kHz, OFF/False: 100 Hz)
        Status (ON/True: channel on, OFF/False: channel off)

        Parameters:
        parent: instrument this channel is a part of
        name: name of the channel
        channel: channel numnber
        controller: the controller the instrument uses for its communication
        """

        super().__init__(parent, name)

        self.voltage = self.add_parameter(
            name = "voltage",
            unit = "V",
            get_cmd = partial(controller.get_channel_dacvalue, channel),
            get_parser = parser.dacval_to_vval,
            set_cmd = partial(controller.set_channel_dacvalue, channel),
            set_parser = parser.vval_to_dacval,
            vals = validate.Numbers(min_value = -10.0, max_value = 10.0),
            initial_value = 0.0
        )

        self.high_bandwidth = self.add_parameter(
            name = "high_bandwidth",
            get_cmd = partial(controller.get_channel_bandwidth, channel),
            set_cmd = partial(controller.set_channel_bandwidth, channel),
            val_mapping = create_on_off_val_mapping(on_val = "HBW", off_val = "LBW"),
            initial_value = False
        )

        self.status = self.add_parameter(
            name = "status",
            get_cmd = partial(controller.get_channel_status, channel),
            set_cmd = partial(controller.set_channel_status, channel),
            val_mapping = create_on_off_val_mapping(on_val = "ON", off_val = "OFF"),
            initial_value = False
        )

# class ----------------------------------------------------------------

class BaspiLnhrdac2(VisaInstrument):
    
    def __init__(self, name, address):
        """
        Main class for integrating the Basel Precision Instruments 
        LNHR DAC II into QCoDeS as an instrument.

        Parameters:
        name: name of the instrument
        address: VISA address of the instrument
        """

        super().__init__(name, address)

        # "library" of all DAC commands
        # not to be used outside of this class definition
        # to only have a single interface to the device
        self.__controller = BaspiLnhrdac2Controller(self)

        # visa properties for telnet communication
        self.visa_handle.write_termination = "\r\n"
        self.visa_handle.read_termination = "\r\n"

        # get number of physicallly available channels
        # for correct further initialization
        channel_modes = self.__controller.get_all_mode()
        self.__number_channels = len(channel_modes)
        if self.__number_channels != 12 and self.__number_channels != 24:
            raise SystemError("Physically available number of channels is not 12 or 24.")

        # create channels and add to instrument
        # save references for later grouping
        channels = {}
        for channel_number in range(1, self.__number_channels + 1):
            name = f"ch{channel_number}"
            channel = BaspiLnhrdac2Channel(self, name, channel_number, self.__controller)
            channels.update({name: channel})
            self.add_submodule(name, channel)

        # grouping channels to simplify simoultaneous access
        all_channels = ChannelList(self, "all channels", BaspiLnhrdac2Channel)
        for channel_number in range(1, self.__number_channels + 1):
            channel = channels[f"ch{channel_number}"]
            all_channels.append(channel)

        self.add_submodule("all", all_channels)

        # display some information after instanciation/ initial connection
        print("")
        self.connect_message()
        print("All channels have been turned off (1 MOhm Pull-Down to AGND) upon initialization "
              + "and are pre-set to 0.0 V if turned on without setting a voltage beforehand.")
        print("")

    #-------------------------------------------------

    def get_idn(self) -> dict:
        """
        Get the identification of the device.

        Returns:
        dict: all QCodes required IDN fields
        """
        vendor = "Basel Precision Instruments GmbH (BASPI)"

        hardware_info = self.__controller.get_serial()
        name = hardware_info[0:11]
        model_nr = hardware_info[12:18]
        channels = hardware_info[52:54]
        model = f"{name} ({model_nr}) {channels} channel version"

        serial = hardware_info[37:51]

        software_info = self.__controller.get_firmware()
        firmware = software_info[18:33]

        idn = {
            "vendor": vendor,
            "model": model,
            "serial": serial,
            "firmware": firmware
        }

        return idn


# main -----------------------------------------------------------------

if __name__ == "__main__":

    station = Station()
    dac = BaspiLnhrdac2('LNHRDAC', 'TCPIP0::192.168.0.5::23::SOCKET')
    station.add_component(dac)

    dac.ch1.status.set("on")
    dac.ch1.voltage.set(5.0)
    res = dac.ch1.voltage.get()
    print(res)
    sleep(1)
    dac.ch1.voltage.set(-3.0)
    res = dac.ch1.voltage.get()
    print(res)
    sleep(1)
    dac.all.voltage.set(5)
    sleep(1)
    dac.all.voltage.set(8.165)
    res = dac.all.voltage.get()
    print(res)
    dac.ch17.high_bandwidth.set(True)
