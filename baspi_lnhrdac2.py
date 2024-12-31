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

        controller = BaspiLnhrdac2Controller(self)

        # visa properties for telnet communication
        self.visa_handle.write_termination = "\r\n"
        self.visa_handle.read_termination = "\r\n"

        # create channels and add to instrument
        # save references for later grouping
        channels = {}
        for channel_number in range(1, 25):
            name = f"ch{channel_number}"
            channel = BaspiLnhrdac2Channel(self, name, channel_number, controller)
            channels.update({name: channel})
            self.add_submodule(name, channel)

        # grouping channels to simplify simoultaneous access
        all_channels = ChannelList(self, "all channels", BaspiLnhrdac2Channel)
        for channel_number in range(1, 25):
            channel = channels[f"ch{channel_number}"]
            all_channels.append(channel)

        # channel list for setting/getting all channels at once
        self.add_submodule("all", all_channels)
    
    # def __init__(self, 
    #              name: str, 
    #              address: str, 
    #              min_val: float = -10, 
    #              max_val: float = 10, 
    #              baud_rate: int = 115200,
    #              channel_number: int = 24,
    #              **kwargs: Any
    #              ) -> None:
    #     """
    #     Constructor. Creates an instance of the Basel Precision Instruments 
    #     LNHR DAC II SP1060 instrument.

    #     Parameters:
    #     name: Local name of this DAC
    #     address: The VISA address of this DAC. For a serial port this is usually ASRLn::INSTR
    #         n is replaced with the address set in the VISA control panel.
    #     channel_number: Number of channels of this DAC
    #     min_val: The minimum voltage that can be output by the DAC
    #     max_val: The maximum voltage that can be output by the DAC
    #     baud_rate: Set accordingly to the VISA control panel
    #     """
    #     # TODO: check "create channels" and "safety limits", check addition of channel_number

    #     super().__init__(name, address, **kwargs)

    #     # VISA resource properties
    #     self.visa_handle.baud_rate = baud_rate
    #     self.visa_handle.parity = visa.constants.Parity.none
    #     self.visa_handle.stop_bits = visa.constants.StopBits.one
    #     self.visa_handle.data_bits = 8
    #     self.visa_handle.flow_control = visa.constants.VI_ASRL_FLOW_XON_XOFF
    #     self.visa_handle.write_termination = "\r\n"
    #     self.visa_handle.read_termination = "\r\n"

    #     # protected properties for communication with device
    #     self._ctrl_cmd_delay = 0.2
    #     self._mem_write_delay = 0.3

    #     # create channels of this device
    #     channels = ChannelList(self, 
    #                            "Channels", 
    #                            SP1060Channel, 
    #                            snapshotable = False,
    #                            multichan_paramclass = SP1060MultiChannel
    #                            )
        
    #     self.channel_number = channel_number
        
    #     for i in range(1, self.channel_number + 1):
    #         channel = SP1060Channel(self, f"chan{i:1}", i)
    #         channels.append(channel)
    #         self.add_submodule(f"ch{i:1}", channel)
    #     channels.lock()
    #     self.add_submodule("channels", channels)

    #     # Safety limits for sweeping DAC voltages
    #     # inter_delay: Minimum time (in seconds) between successive sets.
    #     #              If the previous set was less than this, it will wait until the
    #     #              condition is met. Can be set to 0 to go maximum speed with
    #     #              no errors.    
         
    #     # step: max increment of parameter value.
    #     #       Larger changes are broken into multiple steps this size.
    #     #       When combined with delays, this acts as a ramp.
    #     for chan in self.channels:
    #         chan.volt.inter_delay = 0.02
    #         chan.volt.step = 0.01
        
    #     # display some information after instanciation/ initial connection
    #     self.connect_message()
    #     voltages = self.channels[:].volt.get()
    #     print("Current DAC output (Channel 1 ... Channel 24): ")
    #     print(voltages)

    #-------------------------------------------------

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
    dac.ch17.high_bandwidth.set(1.58)
