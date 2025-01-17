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
from qcodes.instrument import VisaInstrument, InstrumentChannel, ChannelList, InstrumentModule
from qcodes.parameters import create_on_off_val_mapping
import qcodes.validators as validate

from functools import partial
from time import sleep
from warnings import warn

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
            set_cmd = partial(controller.set_channel_dacvalue, channel),
            get_parser = parser.dacval_to_vval,
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

        self.enable = self.add_parameter(
            name = "enable",
            get_cmd = partial(controller.get_channel_status, channel),
            set_cmd = partial(controller.set_channel_status, channel),
            val_mapping = create_on_off_val_mapping(on_val = "ON", off_val = "OFF"),
            initial_value = False
        )

# class ----------------------------------------------------------------

class BaspiLnhrdac2AWG(InstrumentModule):
    
    def __init__(self, 
                 parent: VisaInstrument, 
                 name: str, 
                 awg: str, 
                 controller: BaspiLnhrdac2Controller):
        """
        Class which defines an AWG (Arbitrary Waveform Generator) of the LNHR DAC II with all its QCoDeS-parameters.

        AWG-Parameters:
        awg_channel: channel/output the AWG gets routed to
        awg_cycles: number of cycles/repetitions the device outputs before stopping
        swg: Standard Waveform Generator used to quickly create simple signals
        waveform: holds the values that will be outputted by the AWG
        trigger: AWG trigger mode

        Parameters:
        parent: instrument this channel is a part of
        name: name of the channel
        awg: AWG designator
        controller: the controller the instrument uses for its communication
        """
        super().__init__(parent, name)

        self.__controller = controller

        self.channel = self.add_parameter(
            name = "channel",
            get_cmd = partial(self.__controller.get_awg_channel, awg),
            set_cmd = partial(self.__controller.set_awg_channel, awg),
            vals = validate.Ints(min_value=1, max_value=24)
        )

        self.cycles = self.add_parameter(
            name = "cycles",
            get_cmd = partial(self.__controller.get_awg_cycles, awg),
            set_cmd = partial(self.__controller.set_awg_cycles, awg),
            vals = validate.Ints(min_value=0, max_value=4000000000),
            initial_value = 0
        )

        self.waveform = self.add_parameter(
            name = "waveform",
            get_cmd = partial(self.__get_awg_waveform, awg),
            set_cmd = partial(self.__set_awg_waveform, awg),
            initial_value = None
        )

        self.trigger = self.add_parameter(
            name = "trigger",
            get_cmd = partial(self.__controller.get_awg_trigger_mode, awg),
            set_cmd = partial(self.__controller.set_awg_trigger_mode, awg),
            val_mapping = {"disable": 0, "start only": 1, "start stop": 2, "single step": 3},
            initial_value = "disable"
        )

        self.enable = self.add_parameter(
            name = "enable",
            get_cmd = None,
            set_cmd = None
        )

    #-------------------------------------------------
        
    def __get_awg_waveform(self, awg: str) -> list[float]:
        """
        Read the AWG waveform from device memory.

        Parameters:
        awg: selected AWG

        Returns:
        list: AWG waveform values in V (Volt)
        """

        memory = []
        block_size = 1000 # number of points read by get_wav_memory_block()
        memory_size = self.__controller.get_wav_memory_size(awg)
        adress_range_limit = memory_size // block_size
        if memory_size % block_size != 0:
            adress_range_limit += 1

        # read memory blocks (1000 points) instead of single adresses for faster reading
        for address in range(0, adress_range_limit):
            data = self.__controller.get_wav_memory_block(awg, address * block_size)
            last_value = data.pop()
            while last_value == "NaN":
                last_value = data.pop()
            data.append(last_value)
            memory.extend(data)

        if len(memory) != memory_size:
            raise MemoryError("Error occured while reading the devices memory.")   
        
        return memory

    #-------------------------------------------------

    def __set_awg_waveform(self, awg: str, waveform: list[float]) -> None:
        """
        Write an AWG waveform into device memory. Memory is cleared before writing.

        Parameters:
        awg: selected AWG
        waveform: list of voltages (+/- 10.000000 V)
        """

        self.__controller.clear_wav_memory(awg)

        for address in range(0, len(waveform)):
            self.__controller.set_wav_memory_value(awg, address, float(waveform[address]))

        sleep(0.2) # sleep bc bad firmware
        memory_size = self.__controller.get_wav_memory_size(awg)

        if len(waveform) != memory_size:
            raise MemoryError("Error occured while writing to the devices memory.")
        
        self.__controller.write_wav_to_awg(awg)
        while self.__controller.get_wav_memory_busy(awg):
            pass


# class ----------------------------------------------------------------

class BaspiLnhrdac2SWG(InstrumentModule):

    def __init__(self, parent: VisaInstrument, name: str, controller: BaspiLnhrdac2Controller):
        """
        Class defining the Standard Waveform Generator (SWG) module of the LNHR DAC II with all its Qcodes Parameters.

        SWG-Parameters:
        configuration: 
        apply: 

        Parameters:
        parent: instrument this channel is a part of
        name: name of the module
        controller: the controller the instrument uses for its communication
        """

        super().__init__(parent, name)

        self.__controller = controller

        self.awg = self.add_parameter(
            name = "awg",
            get_cmd = self.__controller.get_swg_wav_memory,
            set_cmd = self.__controller.set_swg_wav_memory
        )

        self.configuration = self.add_parameter(
            name = "configuration",
            get_cmd = self.__get_configuration,
            set_cmd = self.__set_configuration
        )
    
    #-------------------------------------------------

    def __get_configuration(self) -> list:
        pass

    #-------------------------------------------------

    def __set_configuration(self, user_config: dict) -> None:
        """
        Create a waveform using the standard waveform generator. The resulting waveform is automatically written into the waveform memory.

        user_config-Parameters:
        shape: "sine", "cosine, "triangle", "sawtooth", "ramp", "rectangle", "pulse", "fixed noise", "random noise" or "DC"
        frequency: signal frequency in Hz (0.001 Hz - 10000 Hz)
        amplitude: signal amplitude in V (+/- 10.000 V)
        offset: signal DC-offset (+/- 10.000 V)
        phase: signal phaseshift in ° (deg) (+/- 360.000°)
        dutycycle: signal dutycycle in % (0.0 - 100.0), only applicable with shape "pulse"

        Parameters:
        awg: selected AWG
        user_config: dictionary containing SWG configuration

        """
        
        swg_config = {
            "shape": "sine",
            "frequency": 100.0,
            "amplitude": 0.5,
            "offset": 0.0,
            "phase": 0.0,
            "dutycycle": 50.0
        }

        # overwrite defaults if specified
        for key in user_config.keys():
            if key in swg_config.keys():
                swg_config[key] = user_config[key]
            else:
                raise KeyError(f"Key '{key}' is invalid. Valid keys are: {list(swg_config.keys())}")

        self.__controller.set_swg_new(True)

        # always use "adapt clock" here, clock gets checked again in swg.apply
        self.__controller.set_swg_adapt_clock(True)

        # specify waveform
        awg_shapes = {"sine": 0,
                      "cosine": 0,
                      "triangle": 1,
                      "sawtooth": 2,
                      "ramp": 3,
                      "rectangle": 4,
                      "pulse": 4,
                      "fixed noise": 5,
                      "random noise": 6,
                      "DC": 7}

        if swg_config["shape"] not in awg_shapes:
            raise ValueError(f"Value '{swg_config["shape"]}' is invalid. Valid values are: {list(awg_shapes.keys())}.")
        
        self.__controller.set_swg_shape(awg_shapes[swg_config["shape"]])
        self.__controller.set_swg_desired_frequency(swg_config["frequency"])
        self.__controller.set_swg_amplitude(swg_config["amplitude"])
        self.__controller.set_swg_offset(swg_config["offset"])

        if swg_config["shape"] == "cosine":
            self.__controller.set_swg_phase(swg_config["phase"] + 90.0)
        else:
            self.__controller.set_swg_phase(swg_config["phase"])
        if swg_config["shape"] == "rectangle":
            self.__controller.set_swg_dutycycle(50.0)
        elif swg_config["shape"] == "pulse":
            self.__controller.set_swg_dutycycle(swg_config["dutycycle"])

     #-------------------------------------------------

    def apply(self) -> None:
        """
        Apply the SWG configuration to an AWG waveform.

        Parameters:
        awg: selected AWG
        """

        awg = self.__controller.get_swg_wav_memory().lower()

        # decide on keep or adapt clock period
        other_awg = {"a": "b", "b": "a", "c": "d", "d": "c"}
        other_awg_size = self.__controller.get_awg_memory_size(other_awg[awg])
        if other_awg_size > 2:
            self.__controller.set_swg_adapt_clock(False)
        else:
            self.__controller.set_swg_adapt_clock(True)

        desired_frequency = self.__controller.get_swg_desired_frequency()
        nearest_frequency = self.__controller.get_swg_nearest_frequency()
        if nearest_frequency != desired_frequency:
            warn(f"Frequency of {desired_frequency} Hz cannot be reached with the current settings. "
                + f"A frequency of {nearest_frequency} Hz is used instead. "
                + f"Changing AWG or clearing unused AWG waveforms might resolve this issue.")

        # apply SWG configuration to AWG waveform
        self.__controller.apply_swg_operation()
        self.__controller.write_wav_to_awg(awg)
        while self.__controller.get_wav_memory_busy(awg):
            pass
  

# class ----------------------------------------------------------------

class BaspiLnhrdac2(VisaInstrument):
    
    def __init__(self, name: str, address: str):
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
            raise SystemError("Physically available number of channels is not 12 or 24. Please check device.")

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

        # create awg parameters, dependent on 12/24 channel version
        if self.__number_channels == 12:
            awgs = ("a", "b")
        elif self.__number_channels == 24:
            awgs = ("a", "b", "c", "d")

        for awg_designator in awgs:
            name = f"awg{awg_designator}"
            awg = BaspiLnhrdac2AWG(self, name, awg_designator, self.__controller)
            self.add_submodule(name, awg)

        # create SWG parameter, only one is allowed
        name = "swg"
        swg = BaspiLnhrdac2SWG(self, name, self.__controller)
        self.add_submodule(name, swg)

        # display some information after instanciation/ initial connection
        print("")
        self.connect_message()
        print("All channels have been turned off (1 MOhm Pull-Down to AGND) upon initialization "
              + "and are pre-set to 0.0 V if turned on without setting a voltage beforehand.")
        print("")

    #-------------------------------------------------

    def get_idn(self) -> dict:
        """
        Get the identification information of the device.

        Returns:
        dict: contains all QCodes required IDN fields
        """
        vendor = "Basel Precision Instruments GmbH (BASPI)"
        model = f"LNHR DAC II (SP1060) - {self.__number_channels} channel version"

        hardware_info = self.__controller.get_serial()
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

    dac.ch1.enable.set("on")
    dac.ch1.voltage.set(5.0)
    print(dac.ch1.voltage.get())
    dac.ch1.enable.set(False)
    print(dac.ch1.enable.get())

    dac.all.voltage.set(-3.86)
    print(dac.all.voltage.get())

    dac.ch17.enable.set(True)
    dac.ch17.high_bandwidth.set(True)
    print(dac.ch17.high_bandwidth.get())

    dac.awga.channel.set(3)
    print(dac.awga.channel.get())
    dac.awgb.cycles.set(500)
    print(dac.awgb.cycles.get())
    dac.awgc.trigger.set("single step")
    print(dac.awgc.trigger.get())

    # wave = dac.awga.waveform.get()
    # dac.awgb.waveform.set(wave)

    # swg_config = {
    #     "shape": "rectangle",
    #     "frequency": 250,
    #     "amplitude": 0.5,
    #     }

    # dac.awgd.swg.set(swg_config)
    # print(dac.awgd.waveform.get())

    print("---")

    swg_config = {
        "shape": "sine",
        "frequency": 100,
        "amplitude": 0.5,
        }

    dac.swg.configuration.set(swg_config)
    dac.swg.awg.set("A")
    dac.swg.apply()
    print("check clock period now")
    sleep(10)
    dac.awgb.waveform.set([])
    dac.swg.apply()

