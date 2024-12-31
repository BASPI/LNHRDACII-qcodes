# imports --------------------------------------------------------------

from typing import Optional
from time import sleep
from qcodes.station import Station
from qcodes.instrument import InstrumentChannel, VisaInstrument, ChannelList
from qcodes.parameters import MultiChannelInstrumentParameter
from functools import partial

# class ----------------------------------------------------------------

class valueconverter():
    """
    This class contains methods to convert a voltage value of the 
    LNHR DAC II to a hexadecimal value and vice versa. Hexadecimal values
    are used in the devices memory.
    """

    #-------------------------------------------------

    def vval_to_dacval(vval: float) -> int:
        """
        Convert a LNHR DAC II voltage into an internal hexadecimal value

        Parameters:
        vval: voltage value in V

        Returns:
        int: hexadecimal value, used internally by the DAC
        """

        return round((float(vval) + 10.000000) * 838860.74)

    #-------------------------------------------------

    def dacval_to_vval(dacval: int) -> float:
        """
        Convert a LNHR DAC II internal hexadecimal value into a voltage

        Parameters:
        dacval: hexadecimal value, used internally by the DAC
        
        Returns:
        float: voltage value in V
        """

        return round((int(dacval.strip(), 16) / 838860.74) - 10.000000, 6)

# class ----------------------------------------------------------------

class lnhrdac2controller():

    def __init__(self, instrument: VisaInstrument):
        self.__instrument = instrument

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
        # TODO: empty_buffer() necessary?, return sequence (multi command)

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
            sleep(self._ctrl_cmd_delay)
            if "write" in command:
                sleep(self._mem_write_delay)

        return answer

    def set_voltage(self, channel: int, value: int):
        self.write(f"{channel} {value:x}")

    def get_voltage(self, channel: int):
        return self.write(f"{channel} v?")
    
# class ----------------------------------------------------------------

class lnhrdac2channel(InstrumentChannel):

    def __init__(self, parent: VisaInstrument, name: str, channel: int, controller: lnhrdac2controller):

        super().__init__(parent, name)

        self.voltage = self.add_parameter(
            "voltage",
            unit = "V",
            get_cmd = partial(controller.get_voltage, channel),
            get_parser = valueconverter.dacval_to_vval,
            set_cmd = partial(controller.set_voltage, channel),
            set_parser = valueconverter.vval_to_dacval
        )

# class ----------------------------------------------------------------

class lnhrdac2(VisaInstrument):
    
    def __init__(self, name, address):

        super().__init__(name, address)

        controller = lnhrdac2controller(self)

        # visa properties for telnet communication
        self.visa_handle.write_termination = "\r\n"
        self.visa_handle.read_termination = "\r\n"

        # create channels and add to instrument
        # save references for later grouping
        channels = {}
        for channel_number in range(1, 25):
            name = f"ch{channel_number}"
            channel = lnhrdac2channel(self, name, channel_number, controller)
            channels.update({name: channel})
            self.add_submodule(name, channel)

        # grouping channels to simplify simoultaneous access
        all_channels = ChannelList(self, "all channels", lnhrdac2channel)
        for channel_number in range(1, 25):
            channel = channels[f"ch{channel_number}"]
            all_channels.append(channel)

        # channel list for setting/getting all channels at once
        self.add_submodule("all", all_channels)
        


# main -----------------------------------------------------------------

if __name__ == "__main__":

    station = Station()
    dac = lnhrdac2('LNHRDAC', 'TCPIP0::192.168.0.5::23::SOCKET')
    station.add_component(dac)
    dac.ch1.voltage.set(5.3)
    res = dac.ch1.voltage.get()
    print(res)
    sleep(1)
    dac.ch1.voltage.set(0)
    res = dac.ch1.voltage.get()
    print(res)
    sleep(1)
    dac.all.voltage.set(5)
    sleep(1)
    dac.all.voltage.set(8.4684)
    res = dac.all.voltage.get()
    print(res)

    