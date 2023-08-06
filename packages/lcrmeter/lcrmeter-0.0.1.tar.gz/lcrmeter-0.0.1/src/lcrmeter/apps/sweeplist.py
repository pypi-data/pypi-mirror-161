# -*- coding: utf-8 -*-
"""
Created on Wed May 12 13:41:07 2021

@author: dream
"""
import lcrmeter.file_handlers as fh
import lcrmeter.graph_plots as gp
import time
import datetime
import matplotlib
import numpy as np

def create_list(start, end, amnt_points, type_inc = "lin"):
    """
    Function to create a list with [amnt_points] values between [start] annd
    [end] separated in a liner or log10 fashion (determine by [type_inc])
    
    Parameters
    ----------
    start : float
        Starting value for the list.
        
    end : float
        last value for the list.
        
    amnt_points : int
        Amount of data points to be generated for the list.
    
    type_inc : str
        Type of increment between the steps. it can be linear ["lin"] or
        logaritmic["log]. Default is "lin".
    
    Return
    ------
    list of float
        List of elements generated.
    """
      
    if type_inc.upper() == "LIN":
        return list(np.linspace(start, end, amnt_points))
    
    else:
        return list(np.logspace(start=np.log10(start),
                                stop=np.log10(end),
                                num=amnt_points,
                                base=10.0))
        
        


class SweepList:
    """
    Application for measuring a sequence of data points through a list of
    values. and read values.

    Parameters
    ----------
    filename : str
        Path and filename where the results will be stored (plot and data).
    
    lcr : lcrmeter.board.OpLCR()
        LCR instrument to be used.
    
    list_values : list float
        List of values to be swept through.
    
    swp_parameter : str
        Parameter to be swept can be "frequency", "bias" or "ac_level"
    
    delay : float
      Time to be waited in seconds between each meashtrement.
    
    hold : float
        Time in seconds to be waited before the instrument is configured to
        start the sweep. Default value is 1.
    
    cycles : int
        Amount of times the list will be sweeped.
    
    function : str
            Function type to be measure, can be (caps do not matter): 
                "Cp-D", "Cp-Q", "Cp-G", "Cp-Rp",
                "Cs-D", "Cs-Q", "Cs-Rs",
                "Lp-D", "Lp-Q", "Lp-G", "Lp-Rp",
                "Ls-D", "Ls-Q","Ls-Rs", "Ls-Rdc"
                "R-X", "Z-thd", "Z-thr",
                "G-B", "Y-thd", "Y-thr",
                "Vdc-Idc". 
            Default is "" and thus the actual configuration of the tool remain
            unchanged.
    
    read_z : Bool
        In addition to the function the tool also read/record the impedance
        measured. Default is True.
    
    comments : str
        Additional comments to be added to the file and plots.
    """
    
    def __init__(self, filename, lcr, list_values,
                 swp_parameter="frequency",
                 delay=0, hold=1, cycles=1,
                 function="", 
                 read_z=True,
                 comments=""):
        
        
        #Creating attributes from parameters        
        self.lcr = lcr
        self.list_values = list_values
        self.swp_parameter = swp_parameter.upper()
        self.delay = float(delay)
        self.hold = float(hold) 
        self.cycles = cycles
        self.filename = filename
        self.comments = comments
        self.read_z = read_z
        
        
        if function != "":
            self.function = function
            self.lcr.set_function(function)
        else:
            self.function = self.lcr.get_function()
        
        if "DC" in self.function.upper():
            self.header_f1 = "Vdc"
            self.header_f2 = "Idc"
        else:
            self.header_f1 = self.function[0:2].replace("-","")
            self.header_f2 = self.function[-2:].replace("-","")
            
        
        self.param_set_methods = {"FREQUENCY" : self.lcr.set_frequency,
                                  "BIAS"      : self.lcr.set_bias,
                                  "AC_LEVEL"  : self.lcr.set_ac}
            
        self.progressBar = {0: "[..........]",
                            1: "[#.........]",
                            2: "[##........]",
                            3: "[###.......]",
                            4: "[####......]",
                            5: "[#####.....]",
                            6: "[######....]",
                            7: "[#######...]",
                            8: "[########..]",
                            9: "[#########.]",
                           10: "[##########]",}
        
        self.src_units = {"CURR" : "A",
                          "VOLT" : "V"}
        
        self.units = {"CP" : "F",
                      "CS" : "F",
                     "RP" : "Ohm",
                     "RS" : "Ohm",
                     "Y" : "S",
                     "Z" : "Ohm",
                     "D" : "NA",
                     "Q" : "NA",
                     "X" : "Ohm",
                     "Lp" : "H",
                     "Ls" : "H",
                     "G" : "S",
                     "B" : "S",
                     "VDC" : "V",
                     "IDC" : "A",
                     "TD" : "deg",
                     "TR" : "rad",
                     "FREQUENCY" : "Hz",
                     "CURR" : "A",
                     "VOLT" : "V",
                     "BIAS" : self.src_units[self.lcr._b_src_type],
                     "AC_LEVEL" : self.src_units[self.lcr._ac_src_type]}
        

        

        self.set_method = self.param_set_methods[self.swp_parameter]
        self.conf_instr()
        
        
    def conf_instr(self):
        """
        Method to create attributes and configure LCR for sweeping measurement.
        """
        
        #Seting function
        self.lcr.set_function(self.function)
        self.lcr.auto_range("ON")
        
        #Attributes required for working.
        self.timeStamp = []
        self.f1_value = []
        self.f2_value = []
        self.real_z_value = []
        self.img_z_value = []
            

        #Create configuration Messsage:
        msg_header_swep_conf = "\n----------------------------------------\n"\
                               "LCR sweep configuration.\n"\
                               "----------------------------------------\n\n"
            
        msg_swp_param="Sweeping parameter: {0}\n".format(self.swp_parameter)
        msg_hold="Hold value: {0:.3}s\n".format(self.hold)
        msg_delay="Delay between steps: {0:.3}\n".format(float(self.delay))
        msg_amnt_cycles="Amount of cycles : {0}\n".format(self.cycles)
        msg_function="LCR function: {0}\n".format(self.function)
        
        msg_header_lcr_val = "\n----------------------------------------\n"\
                             "LCR parameter values before sweeping.\n"\
                             "----------------------------------------\n\n"
                    
        msg_ac = "AC signal level (RMS): {0}\n".format(self.lcr.get_ac())
        msg_bias = "Value of bias source: {0}\n".format(self.lcr.get_bias())
        msg_bias_state = "Status bias: {0}\n".format(self.lcr.get_bias_state())
        msg_freq = "Frequency value: {0}\n".format(self.lcr.get_frequency())

        
        msg_header_comments = "\n----------------------------------------\n"\
                              "Comments.\n"\
                              "----------------------------------------\n\n"
        
        
        
        self.conf_msg = msg_header_swep_conf\
                        + msg_swp_param\
                        + msg_hold\
                        + msg_delay\
                        + msg_amnt_cycles\
                        + msg_function\
                        + msg_header_lcr_val\
                        + msg_ac\
                        + msg_bias\
                        + msg_bias_state\
                        + msg_freq\
                        + msg_header_comments\
                        + self.comments           

    def meas(self):
        """
        Method to execute a measurement. does not save the data to a file. 
        only run the measurement.
        """
        
        #Attributes required for working.
        self.timeStamp = []
        self.f1_value = []
        self.f2_value = []
        self.real_z_value = []
        self.img_z_value = []
        
        self.progress = 0
        amnt_values = len(self.list_values)
        
        #Starting measurement
        self.conf_instr()

        #Printed informationto the console
        print("\n*********************************************")
        print("Amount of points per cycles: {0}".format(amnt_values))
        print("Amount of cycles: {0}".format(self.cycles))
        print("")
        
        
        
        #Initial hold
        self.set_method(self.list_values[0])
        time.sleep(self.hold)
        
        #Sweep measurement 

        timeZero = time.time()
        
        for cycle in range(1, self.cycles+1):
            
            for value in self.list_values:
                self.set_method(value)
                time.sleep(self.delay)
                [f1_val, f2_val] = self.lcr.read()
                self.f1_value.append(f1_val)
                self.f2_value.append(f2_val)
                
                if self.read_z:
                    [real_z, img_z] = self.lcr.read_z()
                    self.real_z_value.append(real_z)
                    self.img_z_value.append(img_z)
                else:
                    self.real_z_value.append("NA")
                    self.img_z_value.append("NA")
                
                self.timeStamp.append(time.time()-timeZero)
                
                #Printing progress to console
                self.progress = self.progress + 1
                
                n_progress = self.progress/(amnt_values*self.cycles)
                
                bar = int(n_progress*10)
                percent = n_progress*100
                
                print("\rProgress: {0} {1:.1f}%".format(self.progressBar[bar],
                                                        percent), end="")
                
        print("\n*********************************************")
        
        
        self.data = [self.timeStamp,
                     self.list_values,
                     self.f1_value,
                     self.f2_value,
                     self.real_z_value,
                     self.img_z_value]
        
        #Gettting the unit of the swp parameter.
        self.data_headers = ["Time",
                             self.swp_parameter,
                             self.header_f1,
                             self.header_f2,
                             "real_z",
                             "img_z"]
        
        self.data_units = ["s",
                           self.units[self.swp_parameter],
                           self.units[self.header_f1.upper()],
                           self.units[self.header_f2.upper()],
                           "Ohm", "Ohm"]
            
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg_time="Total time: {0}\n".format(self.timeStamp[-1])
        
        self.file_comments = date_time +"\n"+ self.conf_msg  +"\n"+ msg_time
    
    def run(self):
        """
        Method for runing a CV measure. The configuration must be runned first
        by using the method conf_instr(). This will create (or replace) the 
        file specified with the parameter filename.
    
        """
        
        self.meas()

        self.writeFile()

    
    def append(self):
        """
        Method for runing a CV measure. The configuration must be runned first
        by using the method conf_instr(). This will append to an existing file 
        specified with the parameter filename.
        """
        self.meas()

        self.writeFile(append=True)

    def writeFile(self, append = False):
        """
        Method to write the content of data to file
        """
        fh.export_csv(name=self.filename + ".txt",
                      data=self.data,
                      headers=self.data_headers,
                      units=self.data_units,
                      cmt_start=self.file_comments, 
                      delimiter="\t",
                      append=append)
    
    def plot(self, data_x="", data_y="", comment = "F1"):
        
        if data_x == "":
            data_x = self.data[1]
            
        if data_y == "":
            data_y = self.data[2]
        
        
        self.fig = Plot([self.data[1], self.data[2]], comment, fname=self.filename)
    

#---------------------------------------------------------------------
#Plot 
#---------------------------------------------------------------------
class Plot:
    """
    Class to create a plot of the data adquired.
    """
    
    def __init__(self, data, title, fname="./graph"):
        
        self.data = data
        self.filename = fname
        self.plot_enable = True
        
        self.plot_x = "Frequency"
        self.plot_y = "Value"
        
        self.title_font = {'fontname': 'Arial',
                           'size': '16',
                           'color': 'black',
                           'weight': 'normal',
                           'verticalalignment': 'bottom'}
        
        self.axis_font = {'fontname': 'Arial', 'size': '16'}
        self.ticks_text_size = 15
        
        self.border_width = 2
        self.width = 20
        self.height = 15
        self.units = 15
        self.title = "C vs Frequency: " + title 
        
        self.matplotlib_backend = "qt5Agg"
        
        self.getPlot()


    def getPlot(self):
            
        #Creating plots   
        self.plot = gp.plotCV(vwc=self.data[0],
                              iw=self.data[1],
                              style="lin",
                              title = self.title,
                              plot = False)
        
        self.plot.title_font = self.title_font
        self.plot.axis_font = self.axis_font
        self.plot.ticks_text_size = self.ticks_text_size
        self.plot.border_width = self.border_width
        

        
        if not(self.plot_enable):
            matplotlib.use("Agg")
        else:
            matplotlib.use(self.matplotlib_backend)

        
        self.plot.plot()
        
        #saving pdf
        plt_name = self.filename + ".pdf"
        gp.save(self.plot.fig, plt_name,
                width=self.width,
                height=self.height,
                units=self.units,
                format="pdf")
        
        #saving png
        plt_name = self.filename + ".png"
        gp.save(self.plot.fig, plt_name,
                width=self.width,
                height=self.height,
                units=self. units,
                format="png")
