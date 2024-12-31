# ----------------------------------------------------------------------------------------------------------------------------------------------
# LNHR DAC II QCoDeS parser for value conversion
# v0.2.0
# Copyright (c) Basel Precision Instruments GmbH (2024)
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the 
# Free Software Foundation, either version 3 of the License, or any later version. This program is distributed in the hope that it will be 
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details. You should have received a copy of the GNU General Public License along with this program.  
# If not, see <https://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------------------------------------------------------------------------

# class ----------------------------------------------------------------

class BaspiLnhrdac2Parser():
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