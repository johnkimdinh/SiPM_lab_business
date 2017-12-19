#!/usr/bin/env python

################################################################
#                        README                                #
# BACKEND (hardware) script that collects data from the scope  #
################################################################


#Miscellaneous
import os, sys, re
import argparse, time, urllib,matplotlib

#God's given Python library to talk to instruments via different interface
import serial, vxi11

#For plotting business
import numpy as np
import matplotlib.pyplot as plt

#Getting config file
import configSiPM


##############################################
# POWER SUPPLY CLASS TO CONTROL POWER SUPPLY #
##############################################
class Power_Supply:
    #At your service!
    def __init__(self):
        try:
            if os.name=="posix":
		self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1) #Change this for the port, depending on the operating system
		print("Serial link initialized!")  
            elif os.name == "nt":
                self.ser = serial.Serial('COM13', 9600, timeout=1) #COM13 is the usb com 
                print("Serial link initialized!")  
            #self.ser.flushInput()
            #self.__sleep = 0.05
        except Exception as e:
            print(e)      
        
    #Open seasame
    def __enter__(self):
        try:
            if os.name=="posix":
		self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1) #Change this for the port, depending on the operating system
                print("Serial link entered!")
            elif os.name == "nt":
                self.ser = serial.Serial('COM13', 9600, timeout=1) #COM13 is the usb com 
                print("Serial link entered!")
            #self.ser.flushInput()
	    #self.__sleep = 0.05
        except Exception as e:
            print(e)
        return self
        
    #Toutes les bonnes choses ont une fin
    def __exit__(self, *args):
	self.ser.close()
	self.__sleep = 0.05       
	print("Device closed.")
            
    #Okay. Doeiiii!
    def close(self):
        self.ser.close()
	self.__sleep = 0.05    
	print("Device closed.")

    #Ecoute-moi!
    def write(self, message):
        self.ser.write(message)

    #What sayth thou?
    def ask(self, message):
	self.write(message)
	self.write('++read eoi\n')
	reply = self.ser.readline()
	return reply

    # Wie heisst du?
    def get_identifier(self):
        return self.ask('*IDN?\n')

    #This thing has IP!        
    def get_ip(self):
        return self.ask("IPADDR?\n")

    #J vector
    def get_current(self):
        return self.ask('I1?\n')

    #Spatial force integral
    def get_voltage(self):
        return self.ask('V1?\n')

    #I'm your guardian
    def get_ovp(self):
        return self.ask('OVP1?\n')

    #Hell yeah!
    def set_voltage(self, voltage):
        print("Set voltage to: %s Volt.\n" %(voltage) )
        return self.write('V1 %s\n' % voltage)

    #dQ/dt
    def set_current(self, current):
        print "Set current to: %s Ampere\n" %(current)
        return self.write('I1 %s\n' % current)

    # Have you tried to turn it off and on again?
    def reset(self):
        self.write('*RST\n')
        print("Device reset!")

    #Curiosity kills the cat
    def lock(self):
        self.write('IFLOCK\n')
        print("Device locked!")   
    
    #Openseasame!
    def unlock(self):
        self.write('IFUNLOCK\n')
        print("Device unlocked!")   
        
    #Control it locally
    def go_local(self):
        self.write('LOCAL\n')
        print("Press and hold LOCK button to resume local control!")         


              
##############################################
# OSCILLOSCOPE CLASS TO CONTROL SCOPE        #
##############################################       
class Oscilloscope(vxi11.Instrument):
	#My IP is at your service!
    def __init__(self, host='147.96.10.14', timeout = 10):
        self.__sleep = 0.05
        vxi11.Instrument.__init__(self, host=host)
        
    def __enter__(self, host='147.96.10.14', timeout = 10):
        self.__sleep = 0.05
        vxi11.Instrument.__init__(self, host=host)   
        return self
             
        #Toutes les bonnes choses ont une fin
    def __exit__(self, *args):
	self.close()
	self.__sleep = 0.05   

	#Tu t'appelle comment? 
    def identify(self):
        return self.ask('*IDN?\n')
	time.sleep(0.5)

	#Got time? 
    def check_busy(self):
        return self.ask('BUSY?\n')
	time.sleep(0.5)

        #Ain't nobody got time for that!
    def wait(self):
        self.write('*WAI\n')
	time.sleep(0.5)

	#Shave some bucks off the electric bill! (time in minutes)
    def turn_off_screen(self, time_wait):
        command = 'POWER:BACKLIGHT ' + str(time_wait) + '\n'
        self.write(command) 
	time.sleep(0.5)

	#Slaap lekker! (tijd in minuten)
    def shutdown(self, time_wait):
        command = 'POWER:SHUTDOWN ' + str(time_wait) + '\n'
        self.write(command)
	time.sleep(0.5)

	#Have you tried to turn it off and on again?
    def reboot(self):
        self.write('REBOOT\n') 
	time.sleep(0.5)

	#Beep it baby!    
    def beep(self):
        self.write('BELl\n')
	time.sleep(0.5)

	#A factory reset a day keeps the troubles at bay!
    def reset(self):
        self.write('*RST\n')
	time.sleep(0.5)      

	#Curiosity kills the cat!
    def lock(self):
        self.write('LOCK ALL\n')
	time.sleep(0.5) 

	#Open sesame!
    def unlock(self):
        self.write('LOCK NONE\n')
	time.sleep(0.5)

	#Time art fleeting thing!
    def get_time_div(self):
        return self.ask('HORIZONTAL:SCALE?\n') 
	time.sleep(0.5)

	#Take it slowly, baby!
    def set_time_div(self, timediv):
        self.write('HORIZONTAL:SCALE %s\n' % (timediv))

	#La base hilbertienne
    def get_volt_div(self, channel):
        return self.ask('CH%s?\n' % (channel))  
	time.sleep(0.5)

	#Pourquoi pas?
    def set_volt_div(self, channel, volt_div):
        self.write('CH%s:VOLTS %s\n' % (channel, volt_div))

	#Measure what? 
    def set_parameter(self, parameter):
        if not parameter or not len(parameter):
	    raise UserWarning('Incorrect parameter!\n')
	else:
	   self.write('MEASUREMENT:IMMED:TYPE %s\n' % (parameter))
	   time.sleep(0.5)
	   
        #1,2 o MATH?	   
    def select_measurement_channel(self, channel):
        self.write('MEASUREMENT:IMMED:SOURCE1 %s' %(channel))
        time.sleep(0.5)
        
	#Fetch me measurement!      
    def get_parameter(self):
        time.sleep(0.01)
        return self.ask('MEASUrement:IMMed:VALue?\n')

	#A picture worths a thousand words.
    def get_scopeshot(self, path):
	name = str(time.strftime("%d_%m_%Y_%H_%M_%S_%p"))
	name = os.path.join(path, name)
	try:
	   urllib.urlretrieve("http://147.96.10.14/images/InstrumentScreenShot.png",str(name)+'.png')
        except IOError: #Bug in the urllib library
	   print("IOERROR but nothing serious.\n")
        
        #For debugging purposes
    def measure_query(self):
        return self.ask('MEASUrement:IMMed:VALue?\n')



###################################	   
#BECAUSE A BLANK SCREEN IS BORING #
###################################
def update_progress(progress):
    barLength = 50 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rCollecting data: [{0}] {1}% {2}".format( "+"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()



###################################	   
#DYNAMIC IMPORT FROM CONFIG FILE  #
###################################
def get_input_from_input_card(input_card_name, input_name):
	opened_file = open(input_card_name, "r")
	for line in opened_file:
		splitted_line = line.split("=")
		parameter = splitted_line[0][0:-1] #First part of the string is the name of the input parameter. Ignore last space character
		if parameter == input_name:
			opened_file.close() 
			return splitted_line[1][1:-1] #Second part of the string is the value of the input parameter. Ignore first space character
			break #Don't need to go further



#######################################
# SET POWER SUPPLY VOLTAGE            #	
#######################################	
def set_voltage(voltage):
    with Power_Supply() as device:
        previous_voltage = device.get_voltage()
        print("Previous voltage: %s\n" %(previous_voltage) )
        device.set_voltage(voltage)
        print("DONE with setting new voltage.")
 
def check_communication_Power_Supply():
    with Power_Supply() as device:
        identity = device.get_identifier()
        print("Communication with the Power Supply checked! Identifier is %s" %(identity) )
        
def check_communication_Oscilloscope():
    with Oscilloscope() as device:
        identity = device.identify()
        device.beep()
        print("Communication with the Oscilloscope checked! Identifier is %s" %(identity) )



#######################################
# GET DISTRIBUTION OF VOLTAGE READING #	
#######################################	
def get_spectrum(folder_name, voltage):
	number_of_events = int(get_input_from_input_card("configSiPM.py", "Number_of_data_points"))
	number_of_bins = int(get_input_from_input_card("configSiPM.py", "Number_of_bins_in_histogram"))
	additional_remarks = get_input_from_input_card("configSiPM.py", "Optional_remarks")
	Scope_channel = get_input_from_input_card("configSiPM.py", "Scope_channel")
	
	#To avoid / and \ in different OSes
        starting_directory = os.path.abspath(os.getcwd())
        try:
            os.mkdir(folder_name)
        except: #Only make folder once
            pass       
            
        os.chdir(folder_name)
	sub_folder_name = str(voltage) + "_Volt"
    	os.mkdir(sub_folder_name)
    	path_to_save =  os.path.abspath(sub_folder_name)
    	
	time_beginning = time.strftime("%c")

        #COLLECT DATA
	data = []
	fail = 0
	i = 0
 	with Oscilloscope() as device:
                print("Oscilloscope connected!")
                device.beep()
                device.select_measurement_channel(Scope_channel) #Can be "CH1", "CH2" or "MATH1"
                device.set_parameter("AMPlitude") #Other measurements include MAX MIN etc (check page 249 of manual)
		while i < number_of_events:
			reply = device.get_parameter()
			if len(reply) ==0:
				print ('NO DATA: pass this measurement' + '\n')
				fail = fail + 1
			else:
				data.append(float(reply))
				i = i + 1
			
			if (i % (0.01*number_of_events) ) == 0:	
				update_progress(int(round(100*i/number_of_events))/100.0)


	#PLOT HISTOGRAM 
	file_name = 'Histogram_for_' + folder_name + "_" +str(voltage)
	file_name = os.path.join(path_to_save,file_name) 
	
	plt.clf()
	matplotlib.rcParams.update({'font.size': 30})
	plt.figure(figsize=(20,20))
	plt.hist(data, normed=True, bins = number_of_bins, alpha=0.6, color='g')
	
	plt.title(folder_name,fontsize=25)
	plt.ylabel('Frequency (events)', fontsize=35)
	plt.xlabel('Voltage (Volt)', fontsize=35)
        plt.yscale('log')
	plt.minorticks_on()
	plt.grid(True, which='both')
 	plt.savefig(file_name + ".png")


	#WRITE VOLTAGE READING FROM SCOPE TO FOLDER
	file_name = 'reading_list_' + str(voltage)
	file_name = os.path.join(path_to_save,file_name)  
	with open(str(file_name)+'.txt', 'w') as output_file:
	    for i in range(0,len(data)):
	        output_file.write(str(data[i]) + '\n')


   	#META FILE: THIS IS EXPERIMENTAL LOG. CHANGE BEFORE ACTUAL RUN
   	filename = 'Experimental log'
	time_end = time.strftime("%c")
   	filename = os.path.join(path_to_save, filename)
    	with open(str(filename)+'.txt', 'w') as output_meta_data:
    	    output_meta_data.write('Voltage: ' + str(voltage) + '\n')
    	    output_meta_data.write('Number_of_events: ' + str(number_of_events) + '\n')
    	    output_meta_data.write('Number_of_bins_in_plot: ' + str(number_of_bins) + '\n')  
    	    output_meta_data.write('Time_at_the_beginning: ' + str(time_beginning) + '\n')
    	    output_meta_data.write('Time_at_the_end: ' + str(time_end) + '\n')
    	    output_meta_data.write('Failed_measurements: ' + str(fail) + '\n')
    	    output_meta_data.write('Additional_remakrs: ' + additional_remarks  + '\n')

    	
        #GET SCOPE SHOT
        print("Getting scope shot. Please wait....")
        filename = 'Scope'
        filename = os.path.join(path_to_save, filename)
        try:
            urllib.urlretrieve("http://192.168.255.4/images/InstrumentScreenShot.png",str(filename)+'.png')
        except IOError: #Bug in the urllib library
            print("IOERROR but nothing serious.\n")
        print("DONE WITH THIS VOLTAGE!")
        print("="*50)
        
        os.chdir(starting_directory)


													
#######################################
# MAIN PART OF THE PROGRAM            #	
#######################################							
def main():
    voltage_start = float(get_input_from_input_card("configSiPM.py", "Start_voltage"))
    voltage_stop = float(get_input_from_input_card("configSiPM.py", "Stop_voltage"))
    voltage_increase = float(get_input_from_input_card("configSiPM.py", "Voltage_increment"))
    voltage_list = np.arange(voltage_start, voltage_stop, voltage_increase)
    
    Output_folder_name = get_input_from_input_card("configSiPM.py", "Output_folder_name")[1:-2] #Get rid of unnecessary quotation marks and space in the string
    for voltage in voltage_list:
        set_voltage(voltage)    
        get_spectrum(Output_folder_name, voltage)

    set_voltage(0) #Set voltage to zero
    print("Done with all measurements! Set voltage to zero to prevent mishap!")
    
if __name__ == "__main__":
    main()
