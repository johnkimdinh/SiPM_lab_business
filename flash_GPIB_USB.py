#!/usr/bin/env python

import subprocess, os, time
import visa

def get_bus_id():
	proc = subprocess.Popen(['lsusb'], stdout=subprocess.PIPE)
	out = proc.communicate()[0]
	lines = out.split('\n')
	for line in lines:
		if 'Agilent' in line:
			parts = line.split()
			bus = parts[1]
			dev = parts[3][:3]
			print ("Found bus for Agilent: /dev/bus/usb/%s/%s" %(bus, dev))
	return bus, dev	

def test_communication():

	rm = visa.ResourceManager("@py")
	inst = rm.open_resource('GPIB0::14::INSTR')
	time.sleep(0.05)
	inst.write('*RST')
	time.sleep(0.05)
	a = inst.query("*IDN?")
	print a

def main():
	starting_directory = os.getcwd()
	os.chdir("gpib_firmware-2008-08-10/agilent_82357a/")
	GPIB_bus, GPIB_dev = get_bus_id()
	os.system("sudo fxload -t fx2 -D /dev/bus/usb/%s/%s -I ./measat_releaseX1.8.hex" %(GPIB_bus, GPIB_dev))
	time.sleep(2)
	GPIB_bus, GPIB_dev = get_bus_id()
	os.system("sudo fxload -t fx2 -D /dev/bus/usb/%s/%s -I ./measat_releaseX1.8.hex" %(GPIB_bus, GPIB_dev))
	time.sleep(2)
	os.chdir(starting_directory)
	os.system("gpib_config")
	test_communication()
	print("GPIB adapter can now be used in Linux! Vive l'open source!")
	
if __name__ == "__main__":
	main()
