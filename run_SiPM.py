#!/usr/bin/env python

################################################################
#                        README                                #
# FRONTEND (GUI) script that collects data from the scope      #
################################################################


from Tkinter import * # Python GUI module
import os, sys, time  # Utility modules

# Standalone script that controls oscilloscope and power supply
import get_SiPM_spectrum
from get_SiPM_spectrum import Power_Supply as P_S
from get_SiPM_spectrum import Oscilloscope as O_S

LARGE_FONT= ("Verdana", 12)

###################################################
# UTILITY FUNCTIONS. MAY OR MAY NOT BE USEFUL     #
###################################################

# Long gone are the days of IBM's punch cards.
def save_config_file(entries):
	print ("Saving input card to %s file:" %(config_file_name))
	with open(config_file_name, 'w') as f:
		for entry in entries:
			field = entry[0]
			text  = entry[1].get()
			f.write("%s = %s \n" %(field, text) )
			print('%s = %s' % (field, text)) 

	print ("="*50)
	validate_start_button_state()


# Better be safe than sorry.
def validate_start_button_state():
	input_file = open(config_file_name, "r")
	for i, line in enumerate(input_file):
    		if line.startswith('Output_folder_name'):
			folder_name = line.strip().split()[-1]
			break

        absolute_path = os.path.join(os.getcwd(),folder_name[1:-1]) 
	condition_1 = not os.path.exists(absolute_path) #Folder name does not exist yet
	if condition_1:
		b2.configure(state=ACTIVE)
		print("Input card is okay. Ready to go!")
	else:
		b2.configure(state=DISABLED)
		print("Condition_1 not statisfied: Folder name existed. Please change folder name in config file")

		
# A Spaniard's favorite pasttime.
def makeform(root, fields):
	entries = []
	for i, item in enumerate(fields):
		row = Frame(root)
		lab = Label(row, width=25, text=item.replace("_", " "), anchor='w')
		ent = Entry(row)
		ent.insert(END, default_values[i]) #Disable this line for a blank start
		row.pack(side=TOP, fill=X, padx=5, pady=5)
		lab.pack(side=LEFT)
		ent.pack(side=RIGHT, expand=YES, fill=X)
		entries.append((item, ent))
	return entries


# Still alive?
def hardware_test():
        get_SiPM_spectrum.check_communication_Power_Supply()
        get_SiPM_spectrum.check_communication_Oscilloscope()
        print("="*100)


# In search of a Nobel Prize!
def run_main_program():
	b2.configure(relief=SUNKEN, state=DISABLED) #Disarm button during main run to prevent mishap
	print ("Main program now running...")    
	get_SiPM_spectrum.main()
	validate_start_button_state()
	b2.configure(relief=RAISED, state=DISABLED) #Disarm button during main run to prevent mishap



###################################################
# HERE IS THE MAIN PART OF THIS SCRIPT            #
###################################################
config_file_name = 'configSiPM.py'

# Retrieving data from input card
with open(config_file_name) as f:
	fields = [] #LHS of the equation. Definition of the value
	default_values = [] #RHS of the equation. Actual value 
	content = f.readlines()
	for item in content:
		fields.append(item.strip().split()[0])
		default_values.append(item.strip().split()[-1])


# Initialization GUI
root = Tk()
root.title("SiPM Data Collection Routine")

label = Label(root, text="INPUT CARD", font=LARGE_FONT)
label.pack(pady=10,padx=10)

ents = makeform(root, fields)

# Hardware diagnosis
b0 = Button(root, text='Check hardware',command=hardware_test) #Click to CHECK and SAVE new input file
b0.pack(side=LEFT, padx=5, pady=5)
	
# Actions on "Save config file" button
root.bind('<Return>', (lambda event, e=ents: save_config_file(e))) #Hit "Enter" to save new input file   
b1 = Button(root, text='Save config file',command=(lambda e=ents: save_config_file(e))) #Click to CHECK and SAVE new input file
b1.pack(side=LEFT, padx=5, pady=5)

# Actions on "GET DATA" button
b2 = Button(root, text ="GET DATA", state=DISABLED, command=run_main_program) #Won't be able to click this if input file is not valid. See validate_start_button_state() for valid conditions
b2.pack(side=LEFT, padx=5, pady=5)

# Close shop!
b3 = Button(root, text='Quit', command=root.quit)
b3.pack(side=LEFT, padx=5, pady=5)

root.mainloop()
