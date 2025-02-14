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

from qcodes.station import Station
from qcodes.instrument import VisaInstrument, InstrumentChannel, ChannelList, InstrumentModule
from qcodes.parameters import ParameterWithSetpoints, create_on_off_val_mapping
import qcodes.validators as validate

from numpy import array
from functools import partial
from dataclasses import dataclass
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
            get_parser = BaspiLnhrdac2Controller.dacval_to_vval,
            set_parser = BaspiLnhrdac2Controller.vval_to_dacval,
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
        waveform: holds the values that will be outputted by the AWG using numpy arrays
        waveform_setpoints: holds the time-axis values of the waveform parameter using numpy arrays
        trigger: AWG external trigger mode

        Parameters:
        parent: instrument this channel is a part of
        name: name of the channel
        awg: AWG designator
        controller: the controller the instrument uses for its communication
        """

        super().__init__(parent, name)
        self.__controller = controller

        if awg.lower() == "a" or awg.lower() == "b":
            board = "ab"
        elif awg.lower() == "c" or awg.lower() == "d":
            board = "cd"

        self.channel = self.add_parameter(
            name = "channel",
            get_cmd = partial(controller.get_awg_channel, awg),
            set_cmd = partial(controller.set_awg_channel, awg),
            vals = validate.Ints(min_value=1, max_value=24)
        )

        self.cycles = self.add_parameter(
            name = "cycles",
            get_cmd = partial(controller.get_awg_cycles, awg),
            set_cmd = partial(controller.set_awg_cycles, awg),
            vals = validate.Ints(min_value=0, max_value=4000000000),
            initial_value = 0
        )

        self.sampling_rate = self.add_parameter(
            name = "sampling_rate",
            unit = "s",
            get_cmd = partial(controller.get_awg_clock_period, board),
            set_cmd = partial(controller.set_awg_clock_period, board),
            get_parser = self.__get_parser_awg_sampling_rate,
            set_parser = self.__set_parser_awg_sampling_rate,
            vals = validate.Numbers(min_value = 0.00001, max_value = 4000.0)
        )

        self.waveform_setpoints = self.add_parameter(
            name = "waveform_setpoints",
            unit = "s",
            get_cmd = partial(self.__get_awg_waveform_setpoints, awg),
            get_parser = partial(array, dtype = float),
            vals = validate.Arrays(shape = (controller.get_wav_memory_size(awg),))        
        )

        self.waveform = self.add_parameter(
            name = "waveform",
            unit = "V",
            parameter_class = ParameterWithSetpoints,
            get_cmd = partial(self.__get_awg_waveform, awg),
            set_cmd = partial(self.__set_awg_waveform, awg),
            get_parser = partial(array, dtype = float),
            set_parser = list,
            setpoints = (self.waveform_setpoints,),
            vals = validate.Arrays(shape = (controller.get_wav_memory_size(awg),))
        )

        self.trigger = self.add_parameter(
            name = "trigger",
            get_cmd = partial(controller.get_awg_trigger_mode, awg),
            set_cmd = partial(controller.set_awg_trigger_mode, awg),
            val_mapping = {"disable": 0, "start only": 1, "start stop": 2, "single step": 3},
            initial_value = "disable"
        )

        self.enable = self.add_parameter(
            name = "enable",
            get_cmd = partial(controller.get_awg_run_state, awg),
            set_cmd = partial(controller.set_awg_start_stop, awg),
            get_parser = BaspiLnhrdac2AWG.__get_parser_awg_enable,
            val_mapping = create_on_off_val_mapping(on_val = "START", off_val = "STOP"),
            initial_value = False
        )

        board = None

    #-------------------------------------------------

    @staticmethod
    def __get_parser_awg_sampling_rate(val: int) -> float:
        """
        
        """

        return round(val / 1000000, 6)
    
    #-------------------------------------------------

    @staticmethod
    def __set_parser_awg_sampling_rate(val: float) -> int:
        """
        
        """
        
        print("Manually setting the sampling rate of an AWG might influence other AWGs, due to shared sampling rates of AWG A and B aswell as AWG C and D.")
        return int(val * 1000000)
    
    #-------------------------------------------------

    def __get_awg_waveform_setpoints(self, awg: str) -> list[float]:
        """
        
        """

        board = {"a": "ab", "b": "ab", "c": "cd", "d": "cd"}
        memory_size = self.__controller.get_wav_memory_size(awg)
        clock_period = self.__controller.get_awg_clock_period(board[awg])

        increment = clock_period / 1000000
        setpoints = []
        for index in range(0, memory_size):
            setpoints.append(round(index*increment,6))

        return setpoints
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
    
    #-------------------------------------------------

    @staticmethod
    def __get_parser_awg_enable(val: bool) -> str:
        """
        Parsing method for the parameter "enable". Ensures correct function of val_mapping = create_on_off_val_mapping().
        Output of enable.get() has to be a valid input of enable.set().
        """

        if val: return "START"
        else: return "STOP"
    

# class ----------------------------------------------------------------

@dataclass
class BaspiLnhrdac2SWGConfig():
    """
    Dataclass to pass a configuration of the LNHR DAC II SWG module.

    Attributes: 
    shape: "sine", "cosine, "triangle", "sawtooth", "ramp", "rectangle", "pulse", "fixed noise", "random noise" or "DC"
    frequency: signal frequency in Hz (0.001 Hz - 10000 Hz)
    amplitude: signal amplitude in V (+/- 10.000 V)
    offset: signal DC-offset (+/- 10.000 V)
    phase: signal phaseshift in ° (deg) (+/- 360.000°)
    dutycycle: signal dutycycle in % (0.0 - 100.0), only applicable with shape "pulse"
    """

    shape: str = "sine"
    frequency: float = 100.0
    amplitude: float = 0.5
    offset: float = 0.0
    phase: float = 0.0
    dutycycle: float = 0.0

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

        self.configuration = self.add_parameter(
            name = "configuration",
            get_cmd = self.__get_configuration,
            set_cmd = self.__set_configuration
        )
    
    #-------------------------------------------------

    def __get_configuration(self) -> BaspiLnhrdac2SWGConfig:
        
        pass

    #-------------------------------------------------

    def __set_configuration(self, config: BaspiLnhrdac2SWGConfig) -> None:
        """
        Create a waveform using the standard waveform generator. The resulting waveform is automatically written into the waveform memory.

        config-Attributes:
        shape: "sine", "cosine, "triangle", "sawtooth", "ramp", "rectangle", "pulse", "fixed noise", "random noise" or "DC"
        frequency: signal frequency in Hz (0.001 Hz - 10000 Hz)
        amplitude: signal amplitude in V (+/- 10.000 V)
        offset: signal DC-offset (+/- 10.000 V)
        phase: signal phaseshift in ° (deg) (+/- 360.000°)
        dutycycle: signal dutycycle in % (0.0 - 100.0), only applicable with shape "pulse"

        Parameters:
        awg: selected AWG
        config: object containing SWG configuration
        """
        
        self.__controller.set_swg_new(True)

        # always use "adapt clock" here, clock gets checked again in swg.apply
        self.__controller.set_swg_adapt_clock(True)

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

        if config.shape not in awg_shapes:
            raise ValueError(f"Value '{config.shape}' is invalid. Valid values are: {list(awg_shapes.keys())}.")
        
        # specify waveform
        self.__controller.set_swg_shape(awg_shapes[config.shape])
        self.__controller.set_swg_desired_frequency(config.frequency)
        self.__controller.set_swg_amplitude(config.amplitude)
        self.__controller.set_swg_offset(config.offset)

        if config.shape == "cosine":
            self.__controller.set_swg_phase(config.phase + 90.0)
        else:
            self.__controller.set_swg_phase(config.phase)
        if config.shape == "rectangle":
            self.__controller.set_swg_dutycycle(50.0)
        elif config.shape == "pulse":
            self.__controller.set_swg_dutycycle(config.dutycycle)

    #-------------------------------------------------

    def apply(self, awg: str) -> None:
        """
        Apply the SWG configuration to an AWG waveform.

        Parameters:
        awg: selected AWG
        """

        awg = awg.lower()
        self.__controller.set_swg_wav_memory(awg)

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

@dataclass
class BaspiLnhrdac2Fast2dConfig():
    """
    Dataclass to pass a configuration of the LNHR DAC II Fast Scan 2D module.

    Attributes:
    
    """

    x_channel: int = 1,
    x_start_voltage: float = 0.0,
    x_stop_voltage: float = 1.0,
    x_steps: int = 10,
    y_channel: int = 2,
    y_start_voltage: float = 0.0,
    y_stop_voltage: float = 1.0,
    y_steps: int = 10,
    acquisition_delay: float = 0.0,
    adaptive_shift: float = 0.0
  
# class ----------------------------------------------------------------

class BaspiLnhrdac2Fast2d(InstrumentModule):

    def __init__(self, 
                 parent: VisaInstrument, 
                 name: str, 
                 controller: BaspiLnhrdac2Controller):
        """
        
        """

        super().__init__(parent, name)
        self.__controller = controller

        self.configuration = self.add_parameter(
            name = "configuration",
            get_cmd = None,
            set_cmd = None
        )

        self.trigger = self.add_parameter(
            name = "trigger",
            get_cmd = None,
            set_cmd = None
        )

        self.x_axis = self.add_parameter(
            name = "x_axis",
            unit = "V",
            get_cmd = None,
            set_cmd = None,
            vals = None
        )

        self.y_axis = self.add_parameter(
            name = "y_axis",
            unit = "V",
            parameter_class = ParameterWithSetpoints,
            get_cmd = None,
            set_cmd = None,
            setpoints = (self.x_axis,),
            vals = None
        )

        self.enable = self.add_parameter(
            name = "enable",
            get_cmd = None,
            set_cmd = None
        )    

    #-------------------------------------------------

    def __get_2d_configuration(self) -> BaspiLnhrdac2Fast2dConfig:
        pass

    #-------------------------------------------------

    def __set_2d_configuration(self, config: BaspiLnhrdac2Fast2dConfig) -> None:
        """
        
        """

        # choose AWG, ramp and channels
        try:
            if not self.__controller.get_awg_run_state("a") and self.__controller.get_ramp_state("a") == 0:
                awg_ramp = "a"
            elif not self.__controller.get_awg_run_state("b") and self.__controller.get_ramp_state("b") == 0:
                awg_ramp = "b"
            elif not self.__controller.get_awg_run_state("c") and self.__controller.get_ramp_state("c") == 0:
                awg_ramp = "c"
            elif not self.__controller.get_awg_run_state("d") and self.__controller.get_ramp_state("d") == 0:
                awg_ramp = "d"
            else:
                raise SystemError
        except (KeyError, SystemError):
            raise SystemError("There are not enough AWG resources available. Try again after stopping currently running AWGs and ramp generators.")
        
        self.__controller.set_awg_channel(awg_ramp, config.y_channel)
        if not self.__controller.get_awg_channel_availability(awg_ramp):
            raise SystemError(f"The chosen y-axis output (channel {config.y_channel}) is not available.")
        
        self.__controller.set_ramp_channel(awg_ramp, config.x_channel)
        if not self.__controller.get_ramp_channel_availability(awg_ramp):
            raise SystemError(f"The chosen x-axis output (channel {config.y_channel}) is not available.")
        
        memory = {"a": 0, "b": 1, "c": 2, "d": 0}
        board ={"a": "ab", "b": "ab", "c": "cd", "d": "cd"}

        # set up x-axis
        self.__controller.set_ramp_starting_voltage(awg_ramp, config.x_start_voltage)
        self.__controller.set_ramp_peak_voltage(awg_ramp, config.x_stop_voltage)
        ramp_time = 0.005 * (config.x_steps + 1)
        self.__controller.set_ramp_duration(awg_ramp, ramp_time)
        self.__controller.set_ramp_shape(awg_ramp, 0)
        self.__controller.set_ramp_cycles(awg_ramp, 1)
        self.__controller.select_ramp_step(awg_ramp, 1)

        # set up y-axis
        clock_period = int(config.acquisition_delay * 1000)
        period = config.y_steps * (0.000001 * clock_period)
        frequency = 1.0 / period
        amplitude = config.y_stop_voltage - config.y_start_voltage
        offset = config.y_start_voltage

        if period < 0.006:
            raise SystemError(f"The configured y-axis sweep is too short ({period} s). Increase number of steps or acquisition delay. Minimal sweep time is 0.006 s.")
        
        self.__controller.set_awg_cycles(awg_ramp, 1)
        self.__controller.set_awg_trigger_mode(awg_ramp, 0)

        if self.__controller.get_awg_clock_period(board[awg_ramp]) != clock_period: 
            try:
                self.__controller.set_awg_clock_period(board[awg_ramp], clock_period)
                print(f"Clock period of AWG {board[awg_ramp][0].upper()} and {board[awg_ramp][1].upper()} has been changed to {clock_period}.")
            except KeyError: 
                raise SystemError(f"Clock period of AWG {board[awg_ramp][0].upper()} and {board[awg_ramp][1].upper()} cannot be changed. Try again after stopping currently running AWGs.")
            
        self.__controller.set_swg_adapt_clock(False)
        self.__controller.set_swg_new(True)
        self.__controller.set_swg_shape(3)
        self.__controller.set_swg_desired_frequency(frequency)
        self.__controller.set_swg_amplitude(amplitude)
        self.__controller.set_swg_offset(offset)
        self.__controller.set_swg_phase(0)
        self.__controller.set_swg_wav_memory(memory)
        self.__controller.set_swg_selected_operation(2)
        
        if self.__controller.get_wav_memory_size(awg_ramp) > 0:
            print(f"Memory of AWG {awg_ramp.upper()} is not empty and will b e overwritten.")

        self.__controller.clear_wav_memory(awg_ramp)
        self.__controller.apply_swg_operation()
        last_mem_adr = int(self.__controller.get_wav_memory_size(awg_ramp))
        self.__controller.set_wav_memory_value(memory[awg_ramp], last_mem_adr, config.y_start_voltage)
        self.__controller.write_wav_to_awg(awg_ramp)
        
            # adaptive shift
    #-------------------------------------------------

    def __get_2d_trigger(self):
        pass

    #-------------------------------------------------

    def __set_2d_trigger():
        pass

    #-------------------------------------------------

    def __get_2d_x_axis():
        pass

    #-------------------------------------------------

    def __get_2d_x_axis():
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

        # create 2D scan Parameter, only one is allowed
        name = "fast2d"
        fast2d = BaspiLnhrdac2Fast2d(self, name, self.__controller)
        self.add_submodule(name, fast2d)

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

    # a little example on how to use this driver

    station = Station()
    dac = BaspiLnhrdac2('LNHRDAC', 'TCPIP0::192.168.0.5::23::SOCKET')
    station.add_component(dac)



