# ----------------------------------------------------------------------------------------------------------------------------------------------
# LNHR DAC II QCoDeS controller class
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

from typing import Optional
from time import sleep
from qcodes.instrument import VisaInstrument
        
# class ----------------------------------------------------------------

class BaspiLnhrdac2Controller():
    
    def __init__(self, instrument: VisaInstrument) -> None:
        """
        Controller class for the LNHR DAC II QCoDeS driver. This class contains 
        all commands that can be used to control the device. It also implements 
        the write method which is used to send the commands to the device.

        Parameters:
        instrument: object reference to the instrument created by the
            BaspiLnhrdac2 class.
        """
        
        self.__instrument = instrument

        # communication properties
        self.__ctrl_cmd_delay = 0.2
        self.__mem_write_delay = 0.3

    #-------------------------------------------------

    def write(self, command: str) -> Optional[str]:
        """
        Sends a command or a query to the device. This method overrides 
        the standard QCoDeS write() method

        Parameters:
        command: command as per programmers manual of the device

        Returns:
        string: answer of the device in case of a query

        Raises:
        KeyError: command couldn't be processed by the device
        """

        answer = self.__instrument.ask(command)

        # handshaking: check for succesful acknowledge/ valid answer
        if not "?" in command:
            if answer != "0":
                raise KeyError(f"Command ({command}) could not be processed by the device")
        else:
            if "?" in answer:
                raise KeyError(f"Command ({command}) could not be processed by the device")

        # in case of a control command wait to allow for internal 
        # synchronisation of all the devices variables
        if command[0].lower() == "c":
            sleep(self.__ctrl_cmd_delay)
            if "write" in command:
                sleep(self.__mem_write_delay)

        return answer
    
    #-------------------------------------------------

    ##################################################

    # SET DAC COMMANDS

    ##################################################

    #-------------------------------------------------

    def set_channel_dacvalue(self, channel: int, dacvalue: int) -> str:
        """
        Set a specific DAC channel to a specific value

        Parameters:
        channel: DAC channel
        dacvalue: hexadecimal value (0x0 - 0xFFFFFF)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"{channel:0} {dacvalue:x}")
    
    #-------------------------------------------------

    def set_all_dacvalue(self, dacvalue: int) -> str:
        """
        Set all DAC channels to a specific value

        Parameters:
        dacvalue: hexadecimal value (0x0 - 0xFFFFFF)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"all {dacvalue:x}")
    
    #-------------------------------------------------

    def set_channel_status(self, channel: int, status: str) -> str:
        """
        Turn a specific DAC channel on or off

        Parameters:
        channel: DAC channel (1 - 24)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"{channel} {status}")

    #-------------------------------------------------

    def set_all_status(self, status: str) -> str:
        """
        Turn all DAC channels on or off

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """
        
        return self.write(f"all {status}")

    #-------------------------------------------------

    def set_channel_bandwidth(self, channel: int, bandwidth: str) -> str:
        """
        Set the bandwidth of a specific channel to high- or low-bandwith 
        (100 Hz or 100 kHz)

        Parameters:
        channel: DAC channel
        bandwith: bandwith mode ("LBW" or "HBW")

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """
        
        return self.write(f"{channel} {bandwidth}")

    #-------------------------------------------------

    def set_all_bandwidth(self, bandwidth: str) -> str:
        """
        Set the bandwidth of all channels to high- or low-bandwith 
        (100 Hz or 100 kHz)

        Parameters:
        bandwith: bandwith mode ("LBW" or "HBW")

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """
        
        return self.write(f"all {bandwidth}")
    
    #-------------------------------------------------
    
    ##################################################

    # SET AWG COMMANDS

    ##################################################
    
    #-------------------------------------------------

    def set_awg_memory_value(self, memory: str, address: int, dacvalue: int) -> str:
        """
        Set an AWG memory address to a specific value

        Parameters:
        memory: AWG memory to write into ("A", "B", "C" or "D")
        address: hexadecimal memory address (0x0 - 0x84CF)
        dacvalue: hexadecimal value (0x0 - 0xFFFFFF)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"awg-{memory} {address:x} {dacvalue:x}")

    #-------------------------------------------------

    def set_awg_memory_all(self, memory: str, dacvalue: int) -> str:
        """
        Set the full AWG memory to a specific value

        Parameters:
        memory: AWG memory to write into ("A", "B", "C" or "D")
        dacvalue: hexadecimal value (0x0 - 0xFFFFFF)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"awg-{memory} ALL {dacvalue:x}")

    #-------------------------------------------------
    
    ##################################################

    # SET WAVE COMMANDS

    ##################################################

    #-------------------------------------------------

    def set_wav_memory_value(self, memory: str, address: int, voltage: float) -> str:
        """
        Set a wave memory address to a specific value

        Parameters:
        memory: AWG memory to write into ("A", "B", "C" or "D")
        address: hexadecimal memory address (0x0 - 0x84CF)
        voltage: voltage value (+/- 10.000000 V)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"wav-{memory} {address:x} {voltage:.6f}")

    #-------------------------------------------------

    def set_wav_memory_all(self, memory: str, voltage: float) -> str:
        """
        Set the full wave memory to a specific value

        Parameters:
        memory: AWG memory to write into ("A", "B", "C" or "D")
        voltage: voltage value (+/- 10.000000 V)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"wav-{memory} all {voltage:.6f}")
    
    #-------------------------------------------------
    
    ##################################################

    # SET POLYNOMIAL COMMANDS

    ##################################################

    #-------------------------------------------------

    def set_polynomial(self, memory: str, coefficients: list[float:.6]) -> str:
        """
        Set polynomial coefficients. The polynomial can be applied to 
        the values of the AWG memory when the wave memory is copied into 
        the AWG memory

        Parameters:
        memory: associated AWG memory ("A", "B", "C" or "D")
        coefficients: list of floating-point coefficients in ascending 
            order of their order of power

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        coefficient_string = ""

        for element in coefficients:
            coefficient_string = coefficient_string + f" {str(element)}"

        return self.write(f"poly-{memory}{coefficient_string}")
    
    #-------------------------------------------------

    ##################################################

    # QUERY DATA COMMANDS

    ##################################################

    #-------------------------------------------------

    def get_channel_dacvalue(self, channel: int) -> str:
        """
        Read the present value of a specified DAC channel

        Parameters:
        channel: DAC channel

        Returns:
        string: hexadecimal DAC value (0x0 - 0xFFFFFF)
        """

        return self.write(f"{channel} v?")

    #-------------------------------------------------

    def get_all_dacvalue(self) -> str:
        """
        Read the present value of all DAC channels

        Returns:
        string: hexadecimal DAC value (0x0 - 0xFFFFFF) of all channels, 
            comma separated
        """

        return self.write("all v?")

    #-------------------------------------------------

    def get_channel_dacvalue_registered(self, channel: int) -> str:
        """
        Read the registered value of a specified channel. This is the 
        next value that will be outputted

        Parameters:
        channel: DAC channel

        Returns:
        string: hexadecimal DAC value (0x0 - 0xFFFFFF)
        """

        return self.write(f"{channel} vr?")

    #-------------------------------------------------

    def get_all_dacvalue_registered(self) -> str:
        """
        Read the registered value of all channels. This is the next 
        value that will be outputted

        Returns:
        string: hexadecimal registered DAC value (0x0 - 0xFFFFFF) of all channels, 
            comma separated
        """
        
        return self.write("all vr?")
    
    #-------------------------------------------------

    def get_channel_status(self, channel: int) -> str:
        """
        Read the on or off status of a specified DAC channel

        Parameters:
        channel: DAC channel

        Returns:
        string: status ("ON" or "OFF")
        """
        
        return self.write(f"{channel} s?")

    #-------------------------------------------------

    def get_all_status(self) -> list:
        """
        Read the on or off status of all DAC channels

        Returns:
        list: statuses ("ON" or "OFF") of all channels
        """
        
        return self.write("all s?").replace("\r\n","").split(';')
    
    #-------------------------------------------------

    def get_channel_bandwidth(self, channel: int) -> str:
        """
        Read the bandwith of a specified DAC channel (100 Hz or 100 kHz)

        Parameters:
        channel: DAC channel

        Returns:
        string: bandwith mode ("LBW" or "HBW")
        """
        
        return self.write(f"{channel} bw?")

    #-------------------------------------------------

    def get_all_bandwidth(self) -> list:
        """
        Read the bandwith of all DAC channels (100 Hz or 100 kHz)

        Returns:
        list: bandwidth modes ("LBW" or "HBW") of all channels
        """

        return self.write("all bw?").replace("\r\n","").split(';')

    #-------------------------------------------------

    def get_channel_mode(self, channel: int) -> str:
        """
        Read the current DAC mode of a specific DAC channel

        Parameters:
        channel: DAC channel

        Returns:
        string: current DAC mode ("ERR", "DAC", "SYN", "RMP", "AWG", "---")
        """
        
        return self.write(f"{channel} m?")

    #-------------------------------------------------

    def get_all_mode(self) -> list:
        """
        Read the current DAC mode of all DAC channels

        Returns:
        list: current DAC mode ("ERR", "DAC", "SYN", "RMP", "AWG", "---") of all channels
        """

        return self.write("all m?").replace("\r\n","").split(';')

    #-------------------------------------------------

    def get_awg_memory_value(self, memory: str, address: int) -> str:
        """
        Read the value of a specific AWG memory adress. The AWG must not run

        Parameters:
        memory: AWG memory to read out of ("A", "B", "C" or "D")
        address: hexadecimal memory address (0x0 - 0x84CF)

        Returns:
        string: hexadecimal value (0x0 - 0xFFFFFF)
        """
        
        return self.write(f"awg-{memory} {address:x}?")

    #-------------------------------------------------

    def get_awg_memory_block(self, memory: str, block_start_address: int) -> list:
        """
        Read the values of a AWG memory block (1000 values). The AWG must not run

        Parameters:
        memory: AWG memory to read out of ("A", "B", "C" or "D")
        address: hexadecimal memory address (0x0 - 0x84CF)

        Returns:
        list: hexadecimal values (0x0 - 0xFFFFFF) of the memory block
        """
        
        return self.write(f"awg-{memory} {block_start_address:x} blk?").replace("\r\n","").split(';')

    #-------------------------------------------------

    def get_wav_memory_value(self, memory: str, address: int) -> str:
        """
        Read the value of a specific wave memory adress

        Parameters:
        memory: wave memory to read out of ("A", "B", "C" or "D")
        address: hexadecimal memory address (0x0 - 0x84CF)

        Returns:
        string: voltage ("+/- 10.000000" or "NaN")
        """
        
        return self.write(f"wav-{memory} {address:x}?")

    #-------------------------------------------------

    def get_wav_memory_block(self, memory: str, block_start_address: int) -> list:
        """
        Read the values of a wave memory block (1000 values)

        Parameters:
        memory: AWG memory to read out of ("A", "B", "C" or "D")
        address: hexadecimal memory address (0x0 - 0x84CF)

        Returns:
        list: hexadecimal values (0x0 - 0xFFFFFF) of the memory block
        """
        
        return self.write(f"wav-{memory} {block_start_address:x} blk?").replace("\r\n","").split(';')

    #-------------------------------------------------

    def get_polynomial(self, memory: str) -> list:
        """
        Read polynomial coefficients. The polynomial can be applied to 
        the values of the AWG memory when the wave memory is copied 
        into the AWG memory

        Parameters:
        memory: associated AWG memory ("A", "B", "C" or "D")

        Returns:
        list: listing of floating-point coefficients in ascending 
            order of their order of power
        """
        
        return self.write(f"poly-{memory}?").replace("\r\n","").split(';')
    
    #-------------------------------------------------

    ##################################################

    # QUERY INFORMATION COMMANDS

    ##################################################

    #-------------------------------------------------

    def get_help_commands(self) -> str:
        """
        Get an overview of the ASCII commands and queries of the device
        
        Returns:
        string: overview of the ASCII commands and queries of the device
        """
        # TODO: check multiline output

        ans = self.write("?")
        self.__instrument.visa_handle.clear()

        return ans
    
    #-------------------------------------------------

    def get_help_control(self) -> str:
        """
        Get a help text of the device

        Returns:
        string: help text of the device
        """
        # TODO: check multiline output

        ans = self.write("help?")
        self.__instrument.visa_handle.clear()

        return ans
    
    #-------------------------------------------------
    
    def get_firmware(self) -> str:
        """
        Get the firmware of the device

        Returns:
        string: firmware of the device
        """
        # TODO: check multiline output
       
        ans = self.write("soft?")
        self.__instrument.visa_handle.clear()

        return ans 

    #-------------------------------------------------

    def get_serial(self) -> str:
        """
        Returns the serial number of the device

        Returns:
        string: serial number of the device
        """
        # TODO: check multiline output

        ans = self.write("hard?")
        self.__instrument.visa_handle.clear()

        return ans
    
    #-------------------------------------------------
    
    def get_health(self) -> str:
        """
        Get health parameters (temperature, cpu-load, power-supplies) 
        from the device 
        
        Returns:
        string: temperature, cpu-load, power-supplies of the device
        """
        # TODO: check multiline output, 

        ans = self.write("health?")
        self.__instrument.visa_handle.clear()

        return ans

    #-------------------------------------------------

    def get_ip(self) -> str:
        """
        Get the IP address of the device

        Returns:
        string: IP-adress and subnet mask of the device
        """
        # TODO: check multiline output, 

        ans = self.write("ip?")
        self.__instrument.visa_handle.clear()

        return ans
    
    #-------------------------------------------------

    def get_baudrate(self) -> str:
        """
        Get the baudrate of the RS-232 port of the device

        Returns:
        string: baudrate of the RS-232 port of the device
        """
        # TODO: check multiline output, 

        ans = self.write("serial?")
        

        return ans

    #-------------------------------------------------

    def get_contact(self) -> str:
        """
        Get the contact information in case of a problem

        Returns:
        string: contact information
        """
        # TODO: check multiline output, 

        ans = self.write("contact?")
        self.__instrument.visa_handle.clear()

        return ans
    
    #-------------------------------------------------

    ##################################################

    # UPDATE/ SYNCHRONIZATION CONTROL COMMANDS

    ##################################################

    #-------------------------------------------------
    
    def get_board_update_mode(self, board: str) -> str:
        """
        Read the output channel update mode of a DAC board. A channel 
        can get updated instantly after setting its value or synchronous 
        with all other channels, triggered externally or by software

        Parameters:
        board: higher DAC board ("H") or lower DAC board ("L")

        Returns:
        string: DAC board updates instantly ("0") or synchronous ("1")
        """
        return self.write(f"C UM-{board}?")

    #-------------------------------------------------

    def set_board_update_mode(self, board: str, mode: int) -> str:
        """
        Set the output channel update mode of a DAC board. A channel can 
        get updated instantly after setting its value or synchronous with 
        all other channels, triggered externally or by software

        Parameters:
        board: higher DAC board ("H") or lower DAC board ("L")
        string: DAC board updates instantly ("0") or synchronous ("1")

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C UM-{board} {mode}")

    #-------------------------------------------------

    def update_board_channels(self, board: str) -> str:
        """
        Update all channels of a DAC board synchronously

        Parameters:
        board: higher DAC board ("H"), lower DAC board ("L"), 
            or both ("LH")

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C SYNC-{board}")

    #-------------------------------------------------
    
    ##################################################

    # RAMP/ STEP GENERATOR CONTROL COMMANDS

    ##################################################

    #-------------------------------------------------

    def set_ramp_mode(self, ramp: str, mode: str) -> str:
        """
        Set the mode of a ramp/step generator

        Parameters:
        ramp: ramp/step generator ("A", "B", "C", "D" or "all")
        mode: ramp/step generator mode ("start", "stop" or "hold")

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C RMP-{ramp} {mode}")

    #-------------------------------------------------

    def get_ramp_state(self, ramp: str) -> str:
        """
        Read the state of a ramp/step generator

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")

        Returns:
        string: ramp is idle ("0"), ramping up ("1"), ramping down ("2") 
            or on hold ("3")
        """
        
        return self.write(f"C RMP-{ramp} S?")

    #-------------------------------------------------

    def get_ramp_cycles_done(self, ramp: str) -> str:
        """
        Read the number of cycles that have been completed by a 
        ramp/step generator. This value is internally reset on each 
        ramp/step generator start

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")

        Returns:
        string: completed ramp/step cycles (0 - 4000000000)
        """

        return self.write(f"C RMP-{ramp} CD?")

    #-------------------------------------------------

    def get_ramp_steps_done(self, ramp: str) -> str:
        """
        Read the number of single steps that have been completed by a 
        ramp/step generator. This value is internally reset on each 
        ramp/step generator start

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")

        Returns:
        string: completed ramp/step steps (0 - 4000000000)
        """

        return self.write(f"C RMP-{ramp} SD?")

    #-------------------------------------------------

    def get_ramp_step_size(self, ramp: str) -> str:
        """
        Read the internally calculated step size in Volts

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")

        Returns:
        string: step size in V/step (+/- 10.000000 V)
        """

        return self.write(f"C RMP-{ramp} SSV?")

    #-------------------------------------------------

    def get_ramp_cycle_steps(self, ramp: str) -> str:
        """
        Read the internally calculated steps per ramp cycle

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")

        Returns:
        string: number of steps per cycle (0 - 200000000)
        """

        return self.write(f"C RMP-{ramp} ST?")

    #-------------------------------------------------

    def get_ramp_channel_availability(self, ramp: str) -> str:
        """
        Read if the associated DAC channel of a ramp/step generator is 
        available

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")

        Returns:
        string: associated DAC channel is available ("1") 
            or not available ("0")
        """

        return self.write(f"C RMP-{ramp} AVA?")

    #-------------------------------------------------

    def get_ramp_channel(self, ramp: str) -> str:
        """
        Read which DAC channel is associated with a ramp/step generator

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")

        Returns:
        string: associated DAC channel ("1" - "24")
        """
        return self.write(f"C RMP-{ramp} CH?")

    #-------------------------------------------------

    def set_ramp_channel(self, ramp: str, channel: int) -> str:
        """
        Set which DAC channel will be associated with a 
        ramp/step generator

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")
        channel: selected DAC channel (1 - 24)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """
        
        return self.write(f"C RMP-{ramp} CH {channel}")
    
    #-------------------------------------------------

    def get_ramp_starting_voltage(self, ramp: str) -> str:
        """
        Read the starting voltage of a ramp/step generator

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")

        Returns:
        string: starting voltage (+/- 10.0000000 V)
        """

        return self.write(f"C RMP-{ramp} STAV?")

    #-------------------------------------------------

    def set_ramp_starting_voltage(self, ramp: str, voltage: float) -> str:
        """
        Set the starting voltage of a ramp/step generator

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")
        voltage: starting voltage (+/- 10.0000000 V)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C RMP-{ramp} STAV {voltage:.6f}")

    #-------------------------------------------------

    def get_ramp_peak_voltage(self, ramp: str) -> str:
        """
        Read the peak voltage of a ramp/step generator.
        If the ramp shape is UP- or DOWN-ONLY, this is the stop voltage

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")

        Returns:
        string: stop/peak voltage (+/- 10.0000000 V)
        """

        return self.write(f"C RMP-{ramp} STOV?")

    #-------------------------------------------------

    def set_ramp_peak_voltage(self, ramp: str, voltage: float) -> str:
        """
        Set the peak voltage of a ramp/step generator.
        If the ramp shape is UP- or DOWN-ONLY, this is the stop voltage

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")
        voltage: stop/peak voltage (+/- 10.0000000 V)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C RMP-{ramp} STOV {voltage:.6f}")
    
    #-------------------------------------------------

    def get_ramp_duration(self, ramp: str) -> str:
        """
        Read the ramp time of a ramp/step generator. 
        The resolution is given by the default update rate of 5 ms

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")

        Returns:
        string: ramp time (0.05 s - 1000000 s)
        """

        return self.write(f"C RMP-{ramp} RT?")

    #-------------------------------------------------

    def set_ramp_duration(self, ramp: str, time: int) -> str:
        """
        Set the ramp time of a ramp/step generator. 
        The resolution is given by the default update rate of 5 ms

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")
        time: ramp time (0.05 s - 1000000 s)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C RMP-{ramp} RT {time:.3f}")
    
    #-------------------------------------------------

    def get_ramp_shape(self, ramp: str) -> str:
        """
        Read the set ramp shape of a ramp/step generator. Ramping up generates 
        a sawtooth, ramping up and down generates a triangular waveform

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")

        Returns:
        string: ramp up only ("0"), ramp up and down ("1")
        """

        return self.write(f"C RMP-{ramp} RS?")

    #-------------------------------------------------

    def set_ramp_shape(self, ramp: str, shape: int) -> str:
        """
        Set the ramp shape of a ramp/step generator. Ramping up generates 
        a sawtooth, ramping up and down generates a triangular waveform

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")
        shape: ramp up only (0), ramp up and down (1)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C RMP-{ramp} RS {shape}")

    #-------------------------------------------------

    def get_ramp_cycles(self, ramp: str) -> str:
        """
        Read the set number of ramping cycles of a ramp/step generator. 
        Upon completing the set cycles, the ramp/step generator is stopped

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")

        Returns:
        string: set number of ramp cycles (1 - 4000000000) or infinite cycles (0)
        """

        return self.write(f"C RMP-{ramp} CS?")
    
    #-------------------------------------------------

    def set_ramp_cycles(self, ramp: str, cycles: int) -> str:
        """
        Set the number of ramping cycles of a ramp/step generator. 
        Upon completing the set cycles, the ramp/step generator is stopped

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")
        cycles: number of ramp cycles (1 - 4000000000) or infinite cycles (0)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C RMP-{ramp} CS {cycles}")

    
    #-------------------------------------------------

    def get_ramp_mode(self, ramp: str) -> str:
        """
        Read the set mode of a ramp/step generator. In ramp mode the 
        output is updated every 5 ms. In step mode the output is updated 
        internally, after the associated AWG has finished a cycle

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")

        Returns:
        string: RAMP mode ("0") or STEP ("1")
        """

        return self.write(f"C RMP-{ramp} STEP?")

    #-------------------------------------------------

    def select_ramp_step(self, ramp: str, mode: int) -> str:
        """
        Read the set mode of a ramp/step generator. In ramp mode the 
        output is updated every 5 ms. In step mode the output is updated 
        internally, after the associated AWG has finished a cycle

        Parameters:
        ramp: ramp/step generator ("A", "B", "C" or "D")
        mode: RAMP mode (0) or STEP mode (1)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C RMP-{ramp} STEP {mode}")

    #-------------------------------------------------

    ##################################################

    # 2D-SCAN CONTROL COMMANDS

    ##################################################

    #-------------------------------------------------

    def get_awg_start_mode(self, awg: str) -> str:
        """
        Read the set AWG starting mode of an AWG generator. In auto-start 
        the AWG is internally started after the associated step generator 
        was updated. In normal-start the AWG is started by an external 
        trigger or by software

        Parameters:
        awg: AWG ("A", "B", "C" or "D")

        Returns:
        string: normal-start ("0") or auto-start ("1")
        """

        return self.write(f"C AWG-{awg} AS?")

    #-------------------------------------------------

    def set_awg_start_mode(self, awg: str, mode: int) -> str:
        """
        Set the AWG starting mode of an AWG generator. In auto-start the 
        AWG is internally started after the associated step generator 
        was updated. In normal-start the AWG is started by an external 
        trigger or by software

        Parameters:
        awg: AWG ("A", "B", "C" or "D")
        mode: normal-start (0) or auto-start (1)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C AWG-{awg} AS {mode}")

    #-------------------------------------------------

    def get_awg_reload_mode(self, awg: str) -> str:
        """
        Read the set AWG memory reload mode. In reload-mode, the 
        contents of the associated wave memory are loaded into 
        the AWG memory before each restart. In keep-mode, the AWG 
        memory is not updated. A polynomial can only be applied to 
        the waveform in reload-mode (used for adaptive 2D-scans)

        Parameters:
        awg: AWG ("A", "B", "C" or "D")

        Returns:
        string: keep-mode ("0") or reload-mode ("1")
        """

        return self.write(f"C AWG-{awg} RLD?")

    #-------------------------------------------------

    def set_awg_reload_mode(self, awg: str, mode: int) -> str:
        """
        Set the AWG memory reload mode. In reload-mode, the contents of 
        the associated wave memory are loaded into the AWG memory before 
        each restart. In keep-mode, the AWG memory is not updated. 
        A polynomial can only be applied to the waveform in reload-mode 
        (used for adaptive 2D-scans). Must not be changed if a 2D-scan 
        is running

        Parameters:
        awg: AWG ("A", "B", "C" or "D")
        mode: keep-mode (0) or reload-mode (1)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C AWG-{awg} RLD {mode}")

    #-------------------------------------------------

    def get_apply_polynomial (self, polynomial: str) -> str:
        """
        Read if the associated polynomial of an AWG is applied or not. 
        The polynomial is applied each time the AWG memory is reloaded 
        from its associated wave memory

        Parameters:
        polynomial: polynomial ("A", "B", "C" or "D")

        Returns:
        string: skip polynomial ("0") or apply polynomial ("1")
        """

        return self.write(f"C AWG-{polynomial} AP?")

    #-------------------------------------------------
    
    def set_apply_polynomial(self, polynomial: str, mode: int) -> str:
        """
        Set if the associated polynomial of an AWG is applied or not. 
        The polynomial is applied each time the AWG memory is reloaded 
        from its associated wave memory

        Parameters:
        polynomial: polynomial ("A", "B", "C" or "D")
        mode: skip polynomial (0) or apply polynomial (1)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C AWG-{polynomial} AP {mode}")
    
    #-------------------------------------------------
    
    def get_adaptive_shift_voltage(self, awg: str) -> str:
        """
        Set the voltage shift which is applied to an AWG after each step 
        of it's associated step generator. This modifies the constant 
        coefficient of the associated polynomial

        Parameters:
        awg: AWG ("A", "B", "C" or "D")
        voltage: shift voltage per step (+/- 10.000000 V)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C AWG-{awg} SHIV?")

    #-------------------------------------------------

    def set_adaptive_shift_voltage(self, awg: str, voltage: float) -> str:
        """
        Set the voltage shift which is applied to an AWG after each step 
        of it's associated step generator. This modifies the constant 
        coefficient of the associated polynomial

        Parameters:
        awg: AWG ("A", "B", "C" or "D")
        voltage: shift voltage per step (+/- 10.000000 V)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C AWG-{awg} SHIV {voltage:.6f}")

    #-------------------------------------------------

    ##################################################

    # AWG CONTROL COMMANDS 

    ##################################################

    #-------------------------------------------------

    def get_awg_board_mode(self, board: str) -> str:
        """
        Read the set AWG mode of a DAC board (AWG-A/B or AWG-C/D). In 
        normal mode, all outputs can be used for noraml operation. In 
        AWG-only mode all outputs which have no AWG assigned get blocked.

        Parameters:
        board: lower DAC board ("AB") or higher DAC board ("CD")

        Returns:
        string: normal mode ("0") or AWG-only mode ("1")
        """

        return self.write(f"C AWG-{board} ONLY?")

    #-------------------------------------------------

    def set_awg_board_mode(self, board: str, mode: int) -> str: 
        """
        Set the AWG mode of a DAC board (AWG-A/B or AWG-C/D). In normal 
        mode, all outputs can be used for noraml operation. In AWG-only 
        mode all outputs which have no AWG assigned get blocked.

        Parameters:
        board: lower DAC board ("AB") or higher DAC board ("CD")
        mode: normal mode (0) or AWG-only mode (1)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C AWG-{board} ONLY {mode}")

    #-------------------------------------------------

    def set_awg_start_stop(self, awg: str, command: str) -> str: 
        """
        Start or stop one or multiple AWGs

        Parameters:
        awg: AWG ("A", "B", "C", "D", "AB", "CD" or "all")
        command: start or stop command ("start" or "stop")

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C AWG-{awg} {command}")
    
    #-------------------------------------------------

    def get_awg_state(self, awg: str) -> str:
        """
        Read the current state of operation of an AWG

        Parameters:
        awg: AWG ("A", "B", "C" or "D")

        Returns:
        string: AWG is idle/not running ("0") or AWG is running ("1")
        """

        return self.write(f"C AWG-{awg} S?")

    #-------------------------------------------------

    def get_awg_cycles_done(self, awg: str) -> str: 
        """
        Read the number of cycles that have been completed by an AWG.
        This value is internally reset on each AWG start

        Parameters:
        awg: AWG ("A", "B", "C" or "D")

        Returns:
        string: completed AWG cycles (0 - 4000000000)
        """

        return self.write(f"C AWG-{awg} CD?")
    
    #-------------------------------------------------

    def get_awg_duration(self, awg: str) -> str:
        """
        Read the internally calculated duration of one complete AWG cycle

        Parameters:
        awg: AWG ("A", "B", "C" or "D")

        Returns:
        string: AWG cycle duration (0.00002 s - 136000000 s)
        """

        return self.write(f"C AWG-{awg} DP?")
    
    #-------------------------------------------------

    def get_awg_channel_availability(self, awg: str) -> str: 
        """
        Read the current availability for the selected output channel of an 
        AWG. A channel is only available if there is no AWG running on it

        Parameters:
        awg: AWG ("A", "B", "C" or "D")

        Returns:
        string: DAC channel is not available ("0") or is available ("1")
        """

        return self.write(f"C AWG-{awg} AVA?")
    
    #-------------------------------------------------

    def get_awg_channel(self, awg: str) -> str:
        """
        Read the selected output channel of an AWG

        Parameters:
        awg: AWG ("A", "B", "C" or "D")

        Returns:
        string: selected DAC channel ("1" - "24"), depending on AWG
        """

        return self.write(f"C AWG-{awg} CH?")
    
    #-------------------------------------------------

    def set_awg_channel(self, awg: str, channel: int) -> str: 
        """
        Select an output channel for an AWG

        Parameters:
        awg: AWG ("A", "B", "C" or "D")
        channel: selected DAC channel (1 - 24), depending on AWG

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C AWG-{awg} CH {channel}")
    
    #-------------------------------------------------

    def get_awg_memory_size(self, awg: str) -> str:
        """
        Read the size of an AWG memory

        Parameters:
        awg: AWG ("A", "B", "C" or "D")

        Returns:
        string: AWG memory size ("2" - "34000")
        """

        return self.write(f"C AWG-{awg} MS?")

    #-------------------------------------------------

    def set_awg_memory_size(self, awg: str, size: int) -> str:
        """
        Set the size of an AWG memory

        Parameters:
        awg: AWG ("A", "B", "C" or "D")
        string: AWG memory size (2 - 34000)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C AWG-{awg} MS {size}")
    
    #-------------------------------------------------

    def get_awg_cycles(self, awg: str) -> str:
        """
        Read the set number of AWG cycles. Upon completing the set 
        cycles, the AWG is stopped

        Parameters:
        awg: AWG ("A", "B", "C" or "D")

        Returns:
        string: AWG cycles (0 - 4000000000)
        """

        return self.write(f"C AWG-{awg} CS?")

    #-------------------------------------------------

    def set_awg_cycles(self, awg: str, cycles: int) -> str:
        """
        Set the number of AWG cycles. Upon completing the set cycles, 
        the AWG is stopped

        Parameters:
        awg: AWG ("A", "B", "C" or "D")
        cycles: AWG cycles (0 - 4000000000)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C AWG-{awg} CS {cycles}")

    #-------------------------------------------------

    def get_awg_trigger_mode(self, awg: str) -> str:
        """
        Read the external trigger mode of an AWG. The external trigger 
        can be disabled, only trigger the start, trigger the start and 
        stop or trigger each single step of an AWG

        Parameters:
        awg: AWG ("A", "B", "C" or "D")

        Returns:
        string: external trigger is disabled ("0"), only triggers the start
            of an AWG ("1"), triggers start and stop of an AWG ("2"), or
            triggers every single step of an AWG ("3")
        """

        return self.write(f"C AWG-{awg} TM?")

    #-------------------------------------------------

    def set_awg_trigger_mode(self, awg: str, mode: int) -> str: 
        """
        Set the external trigger mode of an AWG. The external trigger 
        can be disabled, only trigger the start, trigger the start and 
        stop or trigger each single step of an AWG

        Parameters:
        awg: AWG ("A", "B", "C" or "D")
        mode: external trigger is disabled ("0"), only triggers the start
            of an AWG ("1"), triggers start and stop of an AWG ("2"), or
            triggers every single step of an AWG ("3")

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C AWG-{awg} TM {mode}")

    #-------------------------------------------------

    def get_awg_clock_period(self, board: str) -> str:
        """
        Read the AWG clock period of a DAC board (AWG-A/B or AWG-C/D) 
        in us (micro-seconds)

        Parameters:
        board: DAC board ("AB" or "CD")

        Returns:
        string: clock period (10 us - 4000000000 us (micro-seconds))
        """

        return self.write(f"C AWG-{board} CP?")

    #-------------------------------------------------

    def set_awg_clock_period(self, board: str, period: int) -> str:
        """
        Set the AWG clock period of a DAC board (AWG-A/B or AWG-C/D) 
        in us (micro-seconds). It might influence or be influenced 
        by another AWG or the SWG

        Parameters:
        board: DAC board ("AB" or "CD")
        period: clock period (10 us - 4000000000 us (micro-seconds))

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C AWG-{board} CP {period}")
    
    #-------------------------------------------------

    def get_awg_refclock_state(self) -> str:
        """
        Read if the 1 MHz reference clock is on or off

        Returns:
        string: reference clock on or off ("on" or "off")
        """

        return self.write("C AWG-1MHz?")

    #-------------------------------------------------

    def set_awg_refclock_state(self, state: int) -> str: 
        """
        Turn the 1 MHz reference clock on or off

        Parameters:
        state: reference clock on ("1") or off ("0")

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C AWG-1MHz {state}")

    #-------------------------------------------------

    ##################################################

    # STANDARD WAVEFORM GENERATION CONTROL COMMANDS

    ##################################################

    #-------------------------------------------------

    def get_swg_new(self) -> bool:
        """
        Read the mode for the SWG (generate new waveform or use saved 
        waveform)

        Returns:
        bool: generate new waveform (True) or use saved waveform (False)
        """

        return bool(int(self.write("C SWG MODE?")))

    #-------------------------------------------------

    def set_swg_new(self, create_new: bool) -> str:
        """
        Set the mode for the SWG (generate new waveform or use saved 
        waveform)

        Parameters:
        create_new: generate new waveform (True) or use saved waveform (False)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C SWG MODE {int(create_new)}")
    
    #-------------------------------------------------

    def get_swg_shape(self) -> int:
        """
        Read the shape of the SWG (sine, triangle, sawtooth, ramp, 
        pulse, noise or DC voltage)

        Returns:
        int: sine (0), triangle (1), sawtooth (2), ramp (3), 
            pulse (4), fixed noise (5), random noise (6) 
            or DC voltage (7)
        """

        return int(self.write("C SWG WF?"))

    #-------------------------------------------------

    def set_swg_shape(self, shape: int) -> str:
        """
        Set the shape of the SWG (sine, triangle, sawtooth, ramp, pulse, 
        noise or DC voltage)

        Parameters:
        shape: sine (0), triangle (1), sawtooth (2), ramp (3), pulse (4), 
            fixed noise (5), random noise (6) or DC voltage (7)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C SWG WF {shape}")
   
    #-------------------------------------------------

    def get_swg_desired_frequency(self) -> float:
        """
        Read the set desired SWG frequency (0.001 Hz - 10 kHz). Not all 
        frequencies can be reached, dependent on the clock period

        Returns:
        float: desired frequency (0.001 Hz - 10 kHz)
        """

        return float(self.write("C SWG DF?"))

    #-------------------------------------------------

    def set_swg_desired_frequency(self, frequency: float) -> str:
        """
        Set the desired SWG frequency (0.001 Hz - 10 kHz). Not all 
        frequencies can be reached, dependent on the clock period

        Parameters:
        frequency: desired frequency (0.001 Hz - 10 kHz)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """
         
        return self.write(f"C SWG DF {frequency}")
    
    #-------------------------------------------------

    def get_swg_adapt_clock(self) -> int:
        """
        Read the state of the adaptive clock (keep AWG clock period or 
        adapt clock period). If set to adapt, the clock period gets 
        automatically adjusted to reach the desired frequency as close 
        as possible. This might affect the other AWG on the DAC board

        Returns:
        int: keep AWG clock period (False) or adapt clock period (True)
        """

        return bool(int(self.write("C SWG ACLK?")))

    #-------------------------------------------------

    def set_swg_adapt_clock(self, adapt: bool) -> str:
        """
        Set the state of the adaptive clock (keep AWG clock period or 
        adapt clock period). If set to adapt, the clock period gets 
        automatically adjusted to reach the desired frequency as close 
        as possible. This might affect the other AWG on the DAC board

        Parameters:
        adapt: keep AWG clock period (False) or adapt clock period (True)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C SWG ACLK {adapt}")
    
    #-------------------------------------------------

    def get_swg_amplitude(self) -> float:
        """
        Read the set SWG amplitude (peak voltage). For noise this is 
        the RMS value

        Returns:
        string: amplitude (+/- 50.000000 V)
        """

        return float(self.write("C SWG AMP?"))

    #-------------------------------------------------

    def set_swg_amplitude(self, amplitude: float) -> str:
        """
        Set the SWG amplitude (peak voltage). For noise this is 
        the RMS value

        Parameters:
        amplitude: amplitude (+/- 50.000000 V)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C SWG AMP {amplitude:.6f}")
    
    #-------------------------------------------------

    def get_swg_offset(self) -> float:
        """
        Set the SWG DC offset voltage

        Parameters:
        offset: DC offset voltage (+/- 10.000000 V)
        """

        return float(self.write("C SWG DCV?"))

    #-------------------------------------------------

    def set_swg_offset(self, offset: float) -> str:
        """
        Set the SWG DC offset voltage

        Parameters:
        offset: DC offset voltage (+/- 10.000000 V)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C SWG DCV {offset:.6f}")
    
    #-------------------------------------------------

    def get_swg_phase(self) -> float:
        """
        Read the SWG phase shift. Not applacable to noise, ramp 
        and DC offset

        Returns:
        string: phase shift (+/- 360.0000°)
        """

        return float(self.write("C SWG PHA?"))

    #-------------------------------------------------

    def set_swg_phase(self, phase: float) -> str:
        """
        Set the SWG phase shift. Not applacable to noise, ramp 
        and DC offset

        Parameters:
        phase: phase shift (+/- 360.0000°)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C SWG PHA {phase:.4f}")
    
    #-------------------------------------------------

    def get_swg_dutycycle(self) -> float:
        """
        Read the SWG duty cylce for the pulse waveform function. A high 
        level is applied for the set percentage of the waveforms period

        Returns:
        float: duty cycle (0.000 % - 100.000 %)
        """

        return float(self.write("C SWG DUC?"))

    #-------------------------------------------------

    def set_swg_dutycycle(self, dutycycle: float) -> str:
        """
        Set the SWG duty cylce for the pulse waveform function. A high 
        level is applied for the set percentage of the waveforms period

        Parameters:
        dutycycle: duty cycle (0.000 % - 100.000 %)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C SWG DUC {dutycycle:.3f}")

    #-------------------------------------------------

    def get_swg_memory_size(self) -> int:
        """
        Read the size of the wave memory
        
        Returns:
        int: wave memory size (10 - 34000)
        """

        return int(self.write("C SWG MS?"))

    #-------------------------------------------------

    def get_swg_nearest_frequency(self) -> float:
        """
        Read the actual SWG frequency (0.001 Hz - 10 kHz). 
        Since not all frequencies can be reached, the closest frequency 
        to the set desired frequency is internally calculated and used

        Returns:
        float: SWG frequency (0.001 Hz - 10 kHz)
        """
        return float(self.write("C SWG NF?"))

    #-------------------------------------------------

    def get_swg_clipping_status(self) -> bool:
        """
        Read the waveform clipping status. If the waveform exceeds the 
        devices limits (+/- 10.0 V) anywhere, the waveform is clipping 
        
        Returns:
        string: waveform is clipping (True) or not clipping (False)
        """

        return bool(int(self.write("C SWG CLP?")))
    
    #-------------------------------------------------

    def get_swg_clock_period(self) -> int:
        """
        Read the SWG clock period in us (micro seconds). This reads 
        the value that will be used during the waveform generation. 
        It is dependent on other settings of the device and might 
        influence or be influenced by another AWG

        Returns:
        int: clock period in us (micro seconds) (10 - 4000000000)
        """

        return int(self.write("C SWG CP?"))
    
    #-------------------------------------------------

    def get_swg_wav_memory(self) -> int:
        """
        Read the selected wave memory into which the SWG saves the 
        generated waveform. Each AWG memory has an associated wave 
        memory ("A", "B", "C" or "D")

        Returns:
        int: selected wave memory A (0), B (1), C (2) 
            or D (3) 
        """

        return int(self.write("C SWG WMEM?"))

    #-------------------------------------------------

    def set_swg_wav_memory(self, wav: int) -> str:
        """
        Select the wave memory into which the SWG saves the generated 
        waveform. Each AWG memory has an associated 
        wave memory ("A", "B", "C" or "D")

        Parameters:
        wav: select wave memory A (0), B (1), C (2) or D (3)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """
        
        return self.write(f"C SWG WMEM {wav}")

    #-------------------------------------------------

    def get_swg_selected_operation(self) -> int:
        """
        Read the selected wave memory operation that will be applied 
        with the command "Apply to wave memory now" 
        (apply_swg_operation()), represented by a number

        Returns:
        int: select operation "overwrite wave memory" (0), "append 
            to start of memory" (1), "append to end of memory" (2), 
            "sum to start of memory" (3), "sum to end of memory" (4), 
            "multiply to start of memory" (5), "multiply to end of 
            memory" (6), "divide to start of memory" (7) 
            or "divide to end of memory" (8)
        """

        return int(self.write("C SWG WFUN?"))

    #-------------------------------------------------

    def set_swg_selected_operation(self, operation: int) -> str:
        """
        Select the wave memory operation that will be applied with the command 
        "Apply to wave memory now" (apply_swg_operation())

        Parameters:
        operation: select operation "overwrite wave memory" (0), "append 
            to start of memory" (1), "append to end of memory" (2), 
            "sum to start of memory" (3), "sum to end of memory" (4),
            "multiply to start of memory" (5), "multiply to end of 
            memory" (6), "divide to start of memory" (7) 
            or "divide to end of memory" (8)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """
        return self.write(f"C SWG WFUN {operation}")
    
    #-------------------------------------------------

    def get_swg_linearization(self) -> bool:
        """
        Read if the output linearization will be applied, when writing 
        a wave memory's contents to its associated AWG memory

        Returns:
        string: apply linearization (True) or do not apply 
            linearization (False)
        """

        return bool(int(self.write("C SWG LIN?")))

    #-------------------------------------------------

    def set_swg_linearization(self, apply: bool) -> str:
        """
        Set if the output linearization will be applied, when writing a 
        wave memory's contents to its associated AWG memory. A channel 
        must be assigned to the associated AWG

        Parameters:
        apply: apply linearization (True) or do not apply linearization (False)

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C SWG LIN {int(apply)}")
    
    #-------------------------------------------------

    def apply_swg_operation(self) -> str:
        """
        The selected SWG operation is applied to the selected wave memory

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write("C SWG APPLY")
    
    #-------------------------------------------------

    ##################################################

    # WAVE CONTROL COMMANDS

    ##################################################

    #-------------------------------------------------

    def get_wav_memory_size(self, wav: str) -> int:
        """
        Read the size of a wave memory ("A", "B", "C", "D" or "S")

        Parameters:
        wav: wave memory ("A", "B", "C", "D" or "S")

        Returns:
        int: number of points saved in the memory (0 - 34000)
        """

        return int(self.write(f"C WAV-{wav} MS?"))

    #-------------------------------------------------

    def clear_wav_memory(self, wav: str) -> str:
        """
        Clear all contents of a wave memory. The memory size is 
        internally reset to 0

        Parameters:
        wav: wave memory ("A", "B", "C", "D" or "S")

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C WAV-{wav} CLR")

    #-------------------------------------------------

    def save_wav_memory(self, wav: str) -> str:
        """
        Save all contents of a wave memory ("A", "B", "C" or "D") 
        to the internal volatile "WAV-S" memory

        Parameters:
        wav: wave memory ("A", "B", "C" or "D") to copy

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C WAV-{wav} SAVE")

    #-------------------------------------------------

    def get_wav_linearization_channel(self, wav: str) -> int:
        """
        Read which DAC channel is associated to a wave memory. The 
        output linearization will be applied to this channel when 
        the wave memory is written to the associated AWG memory

        Parameters:
        wav: wave memory ("A", "B", "C" or "D")

        Returns:
        string: associated channel for linearization (1 - 24), 
            0 if no linearization will be applied
        """

        return int(self.write(f"C WAV-{wav} LINCH?"))
    
    #-------------------------------------------------
    
    def write_wav_to_awg(self, wav_awg: str) -> str:
        """
        Write all contents of a wave memory to its associated AWG memory.
        The "WAV-S" memory can not be written directly to an AWG memory

        Parameters:
        wav_awg: wave/ AWG memory ("A", "B", "C" or "D")

        Returns:
        string: DAC-Error Code ("0" - "5"). "0" is always "no error"
        """

        return self.write(f"C WAV-{wav_awg} WRITE")
    
    #-------------------------------------------------

    def get_wav_memory_busy(self, wav: str) -> bool:
        """
        Read the state of the wave memory busy flag. If set, 
        the wave memory is currently being written to its associated AWG memory

        Parameters: 
        wav: wave/ AWG memory ("A", "B", "C" or "D")

        Returns:
        string: wave memonry busy (True) or not busy (False)
        """

        return bool(int(self.write(f"C WAV-{wav} BUSY?")))


# main -----------------------------------------------------------------

if __name__ == "__main__":

    # small testing script
    instrument = VisaInstrument('LNHRDAC', 'TCPIP0::192.168.0.5::23::SOCKET')
    DAC = BaspiLnhrdac2Controller(instrument)



    
