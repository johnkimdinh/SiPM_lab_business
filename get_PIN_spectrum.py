#!/usr/bin/env python

##################################################################
#                        README                                  #
# BACKEND (hardware) script that collects data from the ammeter  #
##################################################################


#Miscellaneous
import time,re, sys, os, shutil, matplotlib

#The hero
import visa
from visa import ResourceManager 

#For plotting business
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

#Getting config file
import configPIN


#####################################################
# PICOAMP CLASS TO CONTROL CURRENT READING DEVICES  #
####################################################
class Keithley6485(object):

	#At your service, milord
        #def __init__(self, host= u'GPIB1::14::INSTR', timeout = 0.5):
        def __init__(self, timeout = 1):
            rm =  visa.ResourceManager("@py")
            self.open = rm.open_resource('GPIB0::14::INSTR')
            self.__sleep = 0.05
            
	#Open seasame
	def __enter__(self):
            rm =  visa.ResourceManager("@py")
            self.open = rm.open_resource('GPIB0::14::INSTR')
	    self.__sleep = 0.05
            return self
            
	#Toutes les bonnes choses ont une fin
	def __exit__(self, *args):
	    self.open.close()
	    
        #Quoi?
	def ask(self, message):
	    return self.open.query(message)
	    time.sleep(0.05)
	    
	#Just do it!
	def send_command(self, message):
	    self.open.write(message)
	    time.sleep(0.05)
	    
	#Hoe heet jij?
	def get_identifier(self):
	    return self.ask('*IDN?')

        #A reset a day keep the troubles away
	def reset(self):
	    self.send_command('*RST')
            time.sleep(0.05)

        #Just a shift of the origin.
	def enable_zero_check(self):
	    self.send_command('SYST:ZCH ON')
	    time.sleep(0.05)

        #Who cares about the origin anyway?
	def disable_zero_check(self):
	    self.send_command('SYST:ZCH OFF')
	    time.sleep(0.05)
		
	#60Hz ou 50Hz?
	def set_nplc(self, NPLC):
	    self.send_command('NPLC ' + str(NPLC))
	    time.sleep(0.05)
	    
	#Protection is important, kiddo!			
	def set_current_range(self, crange):
	    self.send_command('CURR:RANG ' + str(crange))
	    time.sleep(0.05)
	
	#Ready, set, go!
	def trigger_reading(self):
	    self.send_command('INIT')
	    time.sleep(0.05)

        #Translational symmetry = conservation of momentum
	def enable_zero_correction(self):
	    self.send_command('SYST:ZCOR ON')
	    time.sleep(0.05)

        #Comme les autos americaines
	def enable_auto_range(self):
	    self.send_command('CURR:RANG:AUTO ON')
	    time.sleep(0.05)

        #Fetch me number
	def trigger_and_read(self):
	    data = self.ask('READ?')
	    return data
	    #return self.ask('READ?')
	    time.sleep(0.05)
        
        #In the beginning...
	def zero_correction(self):
	    self.enable_zero_check()
	    self.enable_zero_correction()
	    self.disable_zero_check()
	    #self.enable_auto_range()
	    #self.trigger_and_read()
	    #self.set_current_range(2e-11)



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
    text = "\rPercent: [{0}] {1}% {2}".format( "+"*block + "-"*(barLength-block), progress*100, status)
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
			

def check_communication_Pico_Ammeter():
    with Keithley6485() as device:
        device.zero_correction()
        identity = device.get_identifier()
        print("Communication with the PicoAmmeter checked! Identifier is %s" %(identity) )			
		

	
#######################################
# GET DISTRIBUTION OF CURRENT READING #	
#######################################	
def get_gaussian(folder_name, iteration):
	number_of_events = int(get_input_from_input_card("configPIN.py", "Number_of_data_points"))
	number_of_bins = int(get_input_from_input_card("configPIN.py", "Number_of_bins_in_histogram"))
	NPLC = int(get_input_from_input_card("configPIN.py", "NPLC"))
        additional_remarks = get_input_from_input_card("configPIN.py", "Optional_remarks")
	
	#To avoid / and \ in different OSes
        starting_directory = os.path.abspath(os.getcwd())
        try:
            os.mkdir(folder_name)
        except: #Only make folder once
            pass       
            
        os.chdir(folder_name)
	sub_folder_name = str(iteration) + "_iteration"
    	os.mkdir(sub_folder_name)
    	path_to_save =  os.path.abspath(sub_folder_name)

	time_beginning = time.strftime("%c")

        #COLLECT DATA
	data = []
	fail = 0
	i = 0
 	with Keithley6485() as picoam:
		picoam.set_nplc(NPLC)
		picoam.zero_correction()
		while i < number_of_events:
			reply = picoam.trigger_and_read()
			reply = re.split(r"\s*[,;]\s*", reply.strip())
			if len(reply) ==1:
				print ('NO DATA: pass this measurement' + '\n')
				fail = fail + 1
			else:
				reply = reply[0]
				reply = reply[:-1]
				data.append(float(reply))
				i = i + 1
			
			if (i % (0.01*number_of_events) ) == 0:	
				update_progress(int(round(100*i/number_of_events))/100.0)

				
				
	#GAUSSIAN FIT FOR CALIBRATED DIODE
   	filename = 'GAUSSIAN_RESULT' 
	mu, std = norm.fit(data)
    	filename = os.path.join(path_to_save, filename)
   	with open(str(filename)+'.txt', 'w') as output_meta_data:
		output_meta_data.write("Mean: " + str(mu) + '\n')
 		output_meta_data.write("Std: " + str(std) + '\n')


	#PLOT HISTOGRAM AND GAUSSIAN FIT RESULT
	file_name = 'Histogram for ' + folder_name 
	file_name = os.path.join(path_to_save,file_name) 
	
	plt.clf()
	plt.close('all')
	matplotlib.rcParams.update({'font.size': 30})
	plt.figure(figsize=(20,20))
	plt.hist(data, normed=True, bins = number_of_bins, alpha=0.6, color='g')
	
	xmin, xmax = plt.xlim()
	x = np.linspace(xmin, xmax, 100)
	p = norm.pdf(x, mu, std)
	plt.plot(x, p, 'k', linewidth=2)
	
	plt.title('Fit results: ' + '$\mu$ = ' + str(mu) + ' $\sigma$ = ' +str(std) + ' '+ str(number_of_events)+ ' measurements '+ str(number_of_bins) + 'bins ',fontsize=25)
	plt.ylabel('Frequency (events)', fontsize=35)
	plt.xlabel('Current (Ampere)', fontsize=35)
	plt.minorticks_on()
	plt.grid(True, which='both')
 	plt.savefig(file_name + ".png")

	#WRITE CURRENT READING FROM KEITHLEY TO FOLDER
	file_name = 'reading_list_' + str(NPLC)
	file_name = os.path.join(path_to_save,file_name)  
	with open(str(file_name)+'.txt', 'w') as output_file:
	    for i in range(0,len(data)):
	        output_file.write(str(data[i]) + '\n')

   	#META FILE: THIS IS EXPERIMENTAL LOG. CHANGE BEFORE ACTUAL RUN
   	filename = 'Experimental_log'
	time_end = time.strftime("%c")
   	filename = os.path.join(path_to_save, filename)
    	with open(str(filename)+'.txt', 'w') as output_meta_data:
    	    output_meta_data.write('Number of events: ' + str(number_of_events) + '\n')
    	    output_meta_data.write('Number of bins in plot: ' + str(number_of_bins) + '\n')  
    	    output_meta_data.write('NPLC: ' + str(NPLC) + '\n')  
    	    output_meta_data.write('Time at the beginning: ' + str(time_beginning) + '\n')
    	    output_meta_data.write('Time at the end: ' + str(time_end) + '\n')
    	    output_meta_data.write('Iteration: ' + str(iteration) + '\n')
    	    output_meta_data.write('Failed measurements: ' + str(fail) + '\n')
    	    output_meta_data.write('Additional_remakrs: ' + additional_remarks + '\n')

        os.chdir(starting_directory)
																
#######################################
# MAIN PART OF THE PROGRAM            #	
#######################################	

def main():
    number_of_runs = int(get_input_from_input_card("configPIN.py", "Number_of_runs"))
    i = 0
    while i < number_of_runs:
        try:
            get_gaussian(get_input_from_input_card("configPIN.py", "Output_folder_name")[1:-2], str(i) )
            i = i + 1
        except Exception as e:
            print e
            shutil.rmtree(get_input_from_input_card("configPIN.py", "Output_folder_name")[1:-2], str(i))
            i = i + 1
        

if __name__=="__main__":
    main()
