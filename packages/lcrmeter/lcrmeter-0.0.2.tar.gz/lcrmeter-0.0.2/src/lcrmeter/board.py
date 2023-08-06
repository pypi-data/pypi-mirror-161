# -*- coding: utf-8 -*-
"""
******************************************************************************
Created on Thu Apr 22 15:34:53 2022
api_cfc.py: Api to control the Caonabo Driving Board for DNA synthesis.

Version:
    V1.0.0: Initial release.

author = César J. Lockhart de la Rosa
copyright = Copyright 2022, imec
license = GPL
email = lockhart@imec.be, cesar@lockhart-borremans.com
status = Released
******************************************************************************
"""

import pyvisa as visa
# class definition

class OpLCR:
    """
    Class for interfacing the Caonabo Driving Board (CDB).
    
    Parameter
    ---------
    instr_sn : str
        Serial number of the instrument.
    
    ac_level : float
        Level of the AC signal usted for the measurementin. default is 0.1
    
    ac_src_type : str
        Type of the src used for the measurement (can be "voltage" or
        "current"). Default is voltage.
    """
    
    #list of allowed function types.
    f_types={"CPD"  : "Cp-D",
             "CPG"  : "Cp-G",
             "CPQ"  : "Cp-Q",
             "CPRP" : "Cp-Rp",
             "CSD"  : "Cs-D",
             "CSQ"  : "Cs-Q",
             "CSRS" : "Cs-Rs",
             "LPD"  : "Lp-D",
             "LPG"  : "Lp-G",
             "LPQ"  : "Lp-Q",
             "LPRD" : "Lp-Rdc",
             "LPRP" : "Lp-Rp",
             "LSD"  : "Ls-D",
             "LSQ"  : "Ls-Q",
             "LSRD" : "Ls-Rd",
             "LSRS" : "Ls-Rs",
             "GB"   : "G-B",
             "RX"   : "R-X",
             "VDID" : "Vdc-Idc",
             "YTD"  : "Y-td",
             "YTR"  : "Y-tr",
             "ZTD"  : "Z-td",
             "ZTR"  : "Z-tr"}
    
    src_types={"CURR" : "Current",
               "VOLT" : "Voltage"}
    
    
    
    def __init__(self, instr_sn, ac_level=0.1, ac_src_type="voltage"):
        
    
        self.serial_number = instr_sn.upper()
        
        self.connect()
        
        self.auto_range("ON")
        self.set_bias(value=0, src_type="voltage", state="ON")
        self.set_ac(ac_level, ac_src_type)
            
    def connect(self, instr_sn=""):
        """
        Method to connect to the tool.

        Parameters
        ----------
        instr_sn : str, optional
            Serial number of the instrument to connect to. If not specified
            the serial nuber will be taken from the parent class attribute
            "serial_number".
        """
        
        instr_sn = instr_sn.upper()
        
        if instr_sn == "":
            instr_sn = self.serial_number
        else:
            self.serial_number = instr_sn
            
        
        self._res_manager = visa.ResourceManager()
        list_res = self._res_manager.list_resources()
        
        for resource in list_res:
            if instr_sn in resource:
                self._address = resource
            
        try:
            print("Intrument found at: {0}".format(self._address))
        except:
            print("No instrument found"\
                  " with serial number: {0}".format(self.serial_number))
            return
        
        try:
            self._instr = self._res_manager.open_resource(self._address)
        except:
            print("Could not connect to instrument")
            return
        
        self._out_msg = "*IDN?"
        self._description = self._query(self._out_msg)[:-1]
        print("Connected to instruments."\
              " Instrument details: \n{0}".format(self._description))
            
    def _write(self, msg):
        """
        Method to write a message to the instrument

        Parameters
        ----------
        msg : str
            command to be written.
        """
        
        self._instr.write(msg)
    
    def _read(self):
        """
        Method to read from instruments, if there is nothing available it
        will be timed out. The returned message do not contain the return
        character ("\n").

        Returns
        -------
        str
            Message available in buffer.

        """
        
        return self._instr.read()[:-1]
    
    def _query(self, msg):
        """
        Method to write and then read (to query) the instruments.

        Parameters
        ----------
        msg : str
            command to query (ex.: "*IDN?").

        Returns
        -------
        str
            Message returned by instrument.
            (ex.: 'Agilent Technologies,E4980A,MY46414844,A.06.15')

        """
        
        return self._instr.query(msg) [:-1]
    
    
    
    def _function_type(self, human_type):
        """
        Function to return the SCPI command for the description of the function
        type from a human input. for example: if you input "Cp-Rp", "cp-rp" or
        "CP-RP" it will return "CPRP".

        Parameters
        ----------
        human_type : str
            type for the function.

        Returns
        -------
        str
            SCPI type.

        """
        scpi_type = human_type.upper().replace("-","").replace("H", "")
        
        if scpi_type == "VDCIDC":
            scpi_type = "VDID"
        else:
            scpi_type = scpi_type[0:4]
            
        if scpi_type not in self.f_types.keys():
            raise TypeError("Not a known function type")
        
        return scpi_type
    
#------------------------------------------------------------------------------
#Methods for configuring the instrument
#------------------------------------------------------------------------------

    def auto_range(self, status="ON"):
        """
        Method to activate autorange.

        Parameters
        ----------
        status : str
            Can be "ON" or "OFF". The default is "ON".
        """
        status = status.upper()
        
        if status not in ["ON", "OFF"]:
            raise("Status must be 'ON' or 'OFF'")
            
        self._out_msg = ":FUNC:IMP:RANG:AUTO {0}".format(status)
    
    def set_meas_time(self, int_time, avr_rate=1):
        """
        Method to set the integration time for the measurement. Can be: short,
        medium or long.

        Parameters
        ----------
        int_time : str
            Integration time. Can be "SHORT", "MEDIUM" or "LONG"
        
        avr_rate : int
            Value from 1 to 255 for the averaging rate.
        """
        
        int_time = int_time.upper()[0:4]
        
        if int_time == "MEDI":
            int_time = "MED"
        
        if int_time not in ["LONG", "MED", "SHORT"]:
            raise("Wrong integration time mode (LONG, MED or SHORT.")
        elif avr_rate < 1 or avr_rate > 255:
            raise("Wrong value for average rate (1-255)")
        
        self._out_msg = ":APER {0},{1}".format(int_time, avr_rate)
        return self._write(self._out_msg)
    
    def get_meas_time(self):
        """
        Method to get the configured integration measurement time and the
        average rate.
        """
        self._out_msg = ":APER?"
        val = self._query(self._out_msg).split(',')
        return [val[0], int(val[1])]
        
    def set_function(self, function):
        """
        Method to selet the function type for the measurement of the LCR.

        Parameters
        ----------
        function : str
            Function type to be measure, can be (caps do not matter): 
                "Cp-D", "Cp-Q", "Cp-G", "Cp-Rp",
                "Cs-D", "Cs-Q", "Cs-Rs",
                "Lp-D", "Lp-Q", "Lp-G", "Lp-Rp",
                "Ls-D", "Ls-Q","Ls-Rs", "Ls-Rdc"
                "R-X", "Z-thd", "Z-thr",
                "G-B", "Y-thd", "Y-thr",
                "Vdc-Idc"
        """
                
        self._out_msg = ":FUNC:IMP:TYPE {0}".format(self._function_type(function))
        self._write(self._out_msg)
    
    def get_function(self):
        """
        Method to return the selected function type for the measurement.

        Returns
        -------
        str
            Function type

        """
        
        self._out_msg = ":FUNC:IMP:TYPE?"
        return self.f_types[self._query(self._out_msg)]
    
    def enable_bias(self):
        """
        Method to enble the bias source.
        
        """
        
        self._out_msg = ":BIAS:STAT ON"
        self._write(self._out_msg)
    
    def dissable_bias(self):
        """
        Method to dissable the bias source.
        
        """
        
        self._out_msg = ":BIAS:STAT OFF"
        self._write(self._out_msg)
    
    def get_bias_state(self):
        """
        Method to get the state of the bias (ON or OFF).
        
        Return
        ------
        
        str
            State ("ON" or "OFF")
        """
        
        self._out_msg = ":BIAS:STAT?"
        
        if self._query(self._out_msg) == "1":
            state = "ON"
        else:
            state = "OFF"
        
        return state
    
        
    def set_bias(self, value, src_type="", state=""):
        """
        Method to set the bias for the measurement. 

        Parameters
        ----------
        value : float
            Value of the source for the bias.
        src_type : str, optional
            Type of source to be biased. Can be voltage or current.
            The default is "" meaning that property remain unchanged.
        
        state : str
            Enable ("ON") or dissable ("OFF") the bias after setting the value.
            The default is "" meaning that property remain unchanged.

        Raises
        ------
        TypeError
            "Not a known bias source type".

        """
        if src_type != "":         
            src_type = src_type.upper()[0:4]
            
            if src_type not in self.src_types.keys():
                raise TypeError("Not a known bias source type")
            
            self._b_src_type = src_type
        else:
            src_type = self._b_src_type
        
        self._out_msg = ":BIAS:{0}:LEV {1}".format(src_type, value)
        self._write(self._out_msg)
        
        if state != "":              
            if state.upper() == "ON":
                self.enable_bias()
            else:
                self.dissable_bias()
        
    def get_bias(self):
        """
        Method to get the state of the bias (ON or OFF).
        
        Return
        ------
        
        float
            State ("ON" or "OFF")
        """
        
        self._out_msg = ":BIAS:{0}:LEV?".format(self._b_src_type)
        return [float(self._query(self._out_msg)), self._b_src_type]

    def set_frequency(self, frequency):
        """
        Method to set the measurement frequency. range is from 20HZ to 2Mhz.
        Units are in Hz.
        
        Parameter
        ---------
        frequency: float
             Value of the measurement frequency.
        """
        
        self._out_msg = ":FREQ {0}".format(frequency)
        self._write(self._out_msg)
    
    def get_frequency(self):
        """
        Method to get the configured measurement frequency. 
        Range is from 20HZ to 20Mhz. Units are in Hz.
        
        Return
        ---------
        float
             Value of the measurement frequency.
        """
        
        self._out_msg = ":FREQ?"
        return float(self._query(self._out_msg))
    
    def set_ac(self, value, src_type = ""):
        """
        Method to set the level (RMS) for the measurement.
        Parameter
        ---------
        value : float
             Value of the measurement voltage.
        
        src_type : str
            Type of the ac source used for the measurement. can be 
            "voltage" or "current". The default is "" meaning that property
            remain unchanged.
        """
        
        if src_type != "":  
            src_type = src_type.upper()[0:4]
            
            if src_type not in self.src_types.keys():
                raise TypeError("Not a known ac source type")
            
            self._ac_src_type = src_type
        else:
            src_type = self._ac_src_type
        
        self._out_msg = ":{0}:LEV {1}".format(src_type, value)
        self._write(self._out_msg)
        
    def get_ac(self):
        """
        Method to get the level (RMS) of the AC source used for the
        measurement.
        
        Returns
        -------
        list
             Returns the value and the type. [Value, src_type]

        """
        
        self._out_msg = ":{0}:LEV?".format(self._ac_src_type)
        value = self._query(self._out_msg)
        return [float(value), self._ac_src_type]

#------------------------------------------------------------------------------
#Methods for reading the instrument
#------------------------------------------------------------------------------
    
    def read_z(self):
        """
        Methad to read the complex impedance after applying corrections from
        the open/short calibration.
        
        Return
        ------
        list float
            [r, x] return a list containing the real part
            (resistance) and the imaginary part (reactance) thus that:
            z = r + ix
        """
        
        self._out_msg = ":FETC:IMP:CORR?"
        z = self._query(self._out_msg).split(",")
        z = [float(z[0]), float(z[1])]
        
        return z
    
    def read(self):
        """
        Method to measure and return according to the selected function.
        
        Return
        ------
        list float
            [value1, value2] Return the values according to the selected
            function. For example if Cp-Rp function is selected it will return
            the capacitor value in farads and the resistance value in ohms.
        """
        
        self._out_msg = ":FETC:IMP:FORM?"
        val = self._query(self._out_msg).split(",")
        val = [float(val[0]), float(val[1])]
        
        return val
    
#------------------------------------------------------------------------------
#Methods for calibrating the instrument
#------------------------------------------------------------------------------
    def _wait_while_busy(self):
        """
        Method to wait for the tool to be free of what she was doing.
        """
        busy = True
        while busy:
            try:
                if self._query('*OPC?') == '1':
                    busy = False
            except:
                busy = True
        
    def correction_open(self):
        """
        Execute open correction for all frequency points.
        """
        input("\nPlease open the terminal at the extreme where the DUT will"\
              " be connected and press enter.")
        
        self._out_msg = ":CORR:OPEN:EXEC"
        self._write(self._out_msg)
        
        print("Executing correction.")
        
        self._wait_while_busy()
        
        print("Correction finished.")

        
    
    def correction_short(self):
        """
        Execute short correction for all frequency points.
        """
        input("\nPlease short the terminal at the extreme where the DUT will"\
              " be connected and press enter.")
        
        self._out_msg = ":CORR:SHORT:EXEC"
        self._write(self._out_msg)
        
        print("Executing correction.")
        
        self._wait_while_busy()

        print("Correction finished.")
    
    def correction_cable(self, length):
        """
        Set the cable length for the phase correction. cable length can be 0,
        1, 2, or 4.
        
        Parameter
        ---------
        length : int
            Cable length (0, 1, 2, 4).
        """
        if length not in [0,1,2,4]:
            raise TypeError("Cable length correction not defined"\
                            " (must be 0, 1,2 or 4).")
            
        self._out_msg = ":CORR:LENGTH {0}".format(length)
        self._write(self._out_msg)
        
    def correct(self, cable_length=0):
        """
        Method to run all the corrections with exeption of load 
        (cable, open and shor).
        
        Parameter
        ---------
        cable_length : int
             Closes value to the cable length from 0, 1, 2 and 4 mt.
        """
        
        self.correction_cable(cable_length)
        
        print("\n******************************************")
        print("Open correction")
        print("******************************************")
        
        self.correction_open()
        
        print("\n******************************************")
        print("Short correction")
        print("******************************************")
        
        self.correction_short()
        
        
    def enable_corrections(self, correction="all"):
        """
        Method to activate the corrections

        Parameters
        ----------
        correction : str, optional
            Correction to be activated can be "short", "open" or "all".
            he default is "all". Remember to first execute the correction.

        """
        correction = correction.upper()
        
        if correction == "OPEN":
            self._out_msg = ":CORR:OPEN:STAT ON"
            self._write(self._out_msg)
        elif correction == "SHORT":
            self._out_msg = "CORR:SHORT:STAT ON"
            self._write(self._out_msg)
        elif correction == "ALL":
            self._out_msg = ":CORR:OPEN:STAT ON"
            self._write(self._out_msg)
            self._out_msg = "CORR:SHORT:STAT ON"
            self._write(self._out_msg)
    
    def dissable_corrections(self, correction="all"):
        """
        Method to activate the corrections

        Parameters
        ----------
        correction : str, optional
            Correction to be activated can be "short", "open" or "all".
            he default is "all". Remember to first execute the correction.

        """
        correction = correction.upper()
        
        if correction == "OPEN":
            self._out_msg = ":CORR:OPEN:STAT OFF"
            self._write(self._out_msg)
        elif correction == "SHORT":
            self._out_msg = "CORR:SHORT:STAT OFF"
            self._write(self._out_msg)
        elif correction == "ALL":
            self._out_msg = ":CORR:OPEN:STAT OFF"
            self._write(self._out_msg)
            self._out_msg = "CORR:SHORT:STAT OFF"
            self._write(self._out_msg)
        
        
    
        
            
        
        

        
        
        
        
     