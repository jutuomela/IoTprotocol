import re
import math


class Sensor():

    sname=""
    stype=""
    smax=0
    smin=0
    smean=0
    svar=0
    numb_of_vals=0


    def __init__(self, sname, stype):
        self.sname = sname
        self.stype=stype
        
    def add_value(self, value):
        #cant calculate agg for camera
        if self.stype == "camera":
            return
        #or audio
        if self.stype == "asd":
            return
        #for gps we could so TODO later
        if self.stype == "gps":
            return
	if self.stype == "device":
		return
        #calc max, min, mean, and var for device and temp sensors
        if self.stype == "temp":
            value = float(value)
            self.numb_of_vals+=1
            #if this is the first value
            if self.numb_of_vals == 1:
                self.smax=value
                self.smin=value
                self.smean=value
                self.svar=0
                return

            if(self.smax > value):
                self.smax=value
            if(self.smin < value):
                self.smin=value
            
            old_mean = self.smean
            old_var = self.svar
            self.smean= old_mean + (value - old_mean)/self.numb_of_vals
            self.svar = old_var + (value - old_mean)*(value-self.smean)


    def get_mean(self):
        if self.stype == "device" or self.stype == "temp":
            return self.smean
        else:
            return None

    def get_std(self):
        if self.stype == "device" or self.stype == "temp":
            return math.sqrt(self.svar/self.numb_of_vals-1)
        else:
            return None
            
    def get_min(self):
        if self.stype == "device" or self.stype == "temp":
            return self.smin
        else:
            return None

    def get_max(self):
        if self.stype == "device" or self.stype == "temp":
            return self.smax
        else:
            return None
