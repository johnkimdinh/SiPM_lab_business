import Tkinter as tk
from Tkinter import *

import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
from tkFileDialog import askopenfilename
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import numpy as np
from numpy import sqrt, pi, exp, linspace, random
from scipy.optimize import curve_fit

global x_data , y_data
x_data = []
y_data = []
f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)



def load_data_file():
	file_name = askopenfilename()
	global voltage_data
	voltage_data = [float(line.rstrip()) for line in open(file_name)]
	return(voltage_data)



def update_canvas():
	hist, bin_edges = np.histogram(voltage_data, bins = slider_bin.get())
	bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
	a.plot(bin_centers, hist)
	a.set_title("Finger spectrum", fontsize = 30)
	a.set_xlabel('Peak amplitude [mV]', fontsize = 20)
	a.set_ylabel('Frequency [# events]', fontsize = 20)
	a.set_yscale('log')
	a.grid()
	canvas.draw()


	
def clear_canvas():
	a.cla()
	canvas.draw()



def analysis():
	'''
	Peak height spectrum analysis routine:
	Plots the histogram and find the ROUGH positions of the pedestal, 1phe and 2phe peaks.
	'''
	a.cla()
	hist, bin_edges = np.histogram(voltage_data, bins = slider_bin.get()) #Python histogram
	bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2 #Python plots histogram with bin edges, so we shift by 1/2 the distance
	peak_index = indexes(np.array(hist), thres=slider_thres.get(), min_dist=slider_min_dist.get()) #The ROUGHT peaks finding routine

	first_valley = (bin_centers[peak_index[0]] + bin_centers[peak_index[1]])/2
	second_valley = (bin_centers[peak_index[1]] + bin_centers[peak_index[2]])/2	
	

	pedestal_count = 0.
	first_pe_count = 0.
	total_count = float(len(voltage_data))

	for item in voltage_data:
		if item <= first_valley:
			pedestal_count = pedestal_count + 1
		elif item > first_valley and item <= second_valley:
			first_pe_count = first_pe_count + 1
	
	P_OXT = (total_count - pedestal_count - first_pe_count)/(total_count - pedestal_count)
	Photon_count = -np.log(pedestal_count / total_count)

	print ("ROUGH ESTIMATION:")
	print ("Photon count: %s" %(Photon_count) )
	print ("Optical crosstalk probability: %s" %(P_OXT) )
	print ("Pedestal peak: %s" %(bin_centers[peak_index[0]]))
	print ("1st phe peak: %s" %(bin_centers[peak_index[1]]))
	print ("2nd phe peak: %s\n" %(bin_centers[peak_index[2]]))


	###########################
	# Plotting on GUI canvass #
	###########################
	a.plot(bin_centers, hist)
	a.set_yscale('log')
	a.axvline(x = first_valley, color = 'r', label = "Photon count: %s" %(np.round(Photon_count,decimals = 3)) )
	a.axvline(x = second_valley, color = 'g', label = "$P_{OXT}$: %s" %(np.round(P_OXT, decimals = 3)) )
	for item in peak_index:
		a.plot(bin_centers[item], hist[item], 'rD')
	a.set_title("Finger spectrum", fontsize = 30)
	a.set_xlabel('Peak amplitude [V]', fontsize = 20)
	a.set_ylabel('Frequency [# events]', fontsize = 20)
	a.set_xlim([0,np.amax(voltage_data)])
	a.set_ylim([1,len(voltage_data)])
	a.legend()
	a.grid()
	canvas.draw()



def refine():
	'''
	Peak height spectrum analysis routine:
	First it plots the histogram and find the ROUGH positions of the pedestal, 1phe and 2phe peaks.
	Then it finds a more accurate peak position by fitting a Gaussian. 
	Averages of gaussian will be used to determine the "cuts" that separate pedestal, 1phe and 2phe peaks
	Sigmas of gaussian will be used to estimate the uncertainties of photons count and optical crosstalk.
	'''
	a.cla()
	hist, bin_edges = np.histogram(voltage_data, bins = slider_bin.get()) #Python histogram
	bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2 #Python plots histogram with bin edges, so we shift by 1/2 the distance
	peak_index = indexes(np.array(hist), thres=slider_thres.get(), min_dist=slider_min_dist.get()) #The ROUGHT peaks finding routine

	first_valley = (bin_centers[peak_index[0]] + bin_centers[peak_index[1]])/2
	second_valley = (bin_centers[peak_index[1]] + bin_centers[peak_index[2]])/2	
	
	#Get data for each peak
	x_pedestal_peak, y_pedestal_peak = get_data_between_valley(bin_centers, hist, 0.0, first_valley)
	x_1phe_peak, y_1phe_peak = get_data_between_valley(bin_centers, hist, first_valley, second_valley)
	x_2phe_peak, y_2phe_peak = get_data_between_valley(bin_centers, hist, second_valley, 2* second_valley - first_valley)

	#Gaussian fitting
	initial_guess_pedestal = [y_pedestal_peak[0], x_pedestal_peak[0], (x_pedestal_peak[-1] + x_pedestal_peak[0])/2 ]
	parameters_pedestal = gaussian_fitting(x_pedestal_peak, y_pedestal_peak, initial_guess_pedestal ) #Values for amplitude, center, width	
	initial_guess_1phe = [np.amax(y_1phe_peak), x_1phe_peak[np.argmax(y_1phe_peak)], 2e-6 ]
	parameters_1phe = gaussian_fitting(x_1phe_peak, y_1phe_peak, initial_guess_1phe ) #Values for amplitude, center, width
	initial_guess_2phe = [y_2phe_peak[0], x_2phe_peak[0], 2e-6 ]
	parameters_2phe = gaussian_fitting(x_2phe_peak, y_2phe_peak, initial_guess_2phe ) #Values for amplitude, center, width

	#Get fit value	
	x_fit_pedestal, y_fit_pedestal = gaussian_list(x_pedestal_peak[0], x_pedestal_peak[-1], parameters_pedestal[0], parameters_pedestal[1], parameters_pedestal[2])
	x_fit_1phe, y_fit_1phe = gaussian_list(x_1phe_peak[0], x_1phe_peak[-1], parameters_1phe[0], parameters_1phe[1], parameters_1phe[2])
	x_fit_2phe, y_fit_2phe = gaussian_list(x_2phe_peak[0], x_2phe_peak[-1], parameters_2phe[0], parameters_2phe[1], parameters_2phe[2])

	#Updated valley cut
	first_valley = (parameters_pedestal[1] + parameters_1phe[1])/2
	second_valley = (parameters_1phe[1] + parameters_2phe[1])/2	

	#Calculating photon count and optical crosstalk
	pedestal_count = 0.
	first_pe_count = 0.
	total_count = float(len(voltage_data))

	for item in voltage_data:
		if item <= first_valley:
			pedestal_count = pedestal_count + 1
		elif item > first_valley and item <= second_valley:
			first_pe_count = first_pe_count + 1
	
	P_OXT = (total_count - pedestal_count - first_pe_count)/(total_count - pedestal_count)
	Photon_count = -np.log(pedestal_count / total_count)

	print ("REFINED ESTIMATION:")
	print ("Photon count: %s" %(Photon_count) )
	print ("Optical crosstalk probability: %s" %(P_OXT) )
	print ("Pedestal peak: %s" %(parameters_pedestal[1]) )
	print ("1st phe peak: %s"  %(parameters_1phe[1]) )
	print ("2nd phe peak: %s\n"%(parameters_2phe[1]) )


	###########################
	# Plotting on GUI canvass #
	###########################
	a.plot(bin_centers, hist)
	a.axvline(x = first_valley, color = 'r', label = "Photon count: %s" %(np.round(Photon_count,decimals = 3)) )
	a.axvline(x = second_valley, color = 'g', label = "$P_{OXT}$: %s" %(np.round(P_OXT, decimals = 3)) )
	a.plot(x_pedestal_peak, y_pedestal_peak, 'k.', label = "Pedestal events")
	a.plot(x_fit_pedestal, y_fit_pedestal, 'k-')
	a.plot(x_1phe_peak, y_1phe_peak, 'k*', label = "1phe events") 
	a.plot(x_fit_1phe, y_fit_1phe, 'k-')
	a.plot(x_2phe_peak, y_2phe_peak, 'kD', label = "2phe events")
	a.plot(x_fit_2phe, y_fit_2phe, 'k-') 
	a.set_yscale('log')
	a.plot(parameters_pedestal[1],parameters_pedestal[0], 'rD')
	a.plot(parameters_1phe[1],parameters_1phe[0], 'rD')
	a.plot(parameters_2phe[1],parameters_2phe[0], 'rD')	
	a.set_title("Finger spectrum", fontsize = 30)
	a.set_xlabel('Peak amplitude [V]', fontsize = 20)
	a.set_ylabel('Frequency [# events]', fontsize = 20)
	a.set_xlim([0,np.amax(voltage_data)])
	a.set_ylim([1,len(voltage_data)])
	a.legend()
	a.grid()
	canvas.draw()



def indexes(y, thres, min_dist):
	'''Peak detection routine.
	Finds the peaks in *y* by taking its first order difference. By using
	*thres* and *min_dist* parameters, it is possible to reduce the number of
	detected peaks.
	Parameters
	----------
	y : ndarray
	1D amplitude data to search for peaks.
	thres : float between [0., 1.]
	Normalized threshold. Only the peaks with amplitude higher than the
	threshold will be detected.
	min_dist : int
	Minimum distance between each detected peak. The peak with the highest
	amplitude is preferred to satisfy this constraint.
	Returns
	-------
	ndarray
	Array containing the indexes of the peaks that were detected
	'''

	# find the peaks by using the first order difference
	dy = np.diff(y)
	thres *= np.max(y) - np.min(y)
	peaks = np.where((np.hstack([dy, 0.]) < 0.)  & (np.hstack([0., dy]) > 0.)  & (y > thres))[0]
    
	if peaks.size > 1 and min_dist > 1:
		highest = peaks[np.argsort(y[peaks])][::-1]
		rem = np.ones(y.size, dtype=bool)
		rem[peaks] = False

	for peak in highest:
		if not rem[peak]:
			sl = slice(max(0, peak - min_dist), peak + min_dist + 1)
			rem[sl] = True
			rem[peak] = False

        peaks = np.arange(y.size)[~rem]

	return peaks



def get_data_between_valley(data_peak_height, data_peak_frequency, start_peak_valley, stop_peak_valley):
	#Extract peaks from histogram according to start and stop value
	peak_height_list = []
	peak_frequency_list = []
	for i in range(len(data_peak_height)):
		if data_peak_height[i] >= start_peak_valley and data_peak_height[i] <= stop_peak_valley:
			peak_height_list.append(data_peak_height[i])
			peak_frequency_list.append(data_peak_frequency[i])
		elif data_peak_height[i] > stop_peak_valley:
			break
	return peak_height_list, peak_frequency_list


def gaussian(x, amp, cen, wid):
	return amp * exp(-(x-cen)**2 /wid)

def gaussian_list(x_start, x_stop, amp, cen, wid):
	x_list = np.linspace(x_start, x_stop, num=100)
	y_list = []
	for item in x_list:
		y_list.append(gaussian(item, amp, cen, wid))
	return x_list, y_list 

def gaussian_fitting(x_data, y_data, initial_guess):
	'''
	x_data: peak height values
	y_data: frequency of peak heights
	initial_guess: give the fitting routine some educated initially guess, in the form of [amplitude, center, width] eg: [100,0,0.001]
	'''
	best_vals, covar = curve_fit(gaussian, x_data, y_data, p0 = initial_guess)
	return best_vals



##############################################
# GUI BUSINESS FOR ANALYSIS WINDOWS          #
##############################################                       

root = Tk()
root.title("SiPM Analysis Routine")

# Plotting data
a.plot(x_data,y_data, '.')
canvas=FigureCanvasTkAgg(f,root)
canvas.get_tk_widget().pack(side=tk.BOTTOM,fill=tk.BOTH,expand=True)
toolbar = NavigationToolbar2TkAgg(canvas, root)
toolbar.update()
canvas.show()

#Button 1
button0=tk.Button(root,text="Choose file", command = load_data_file)
button0.pack(side=LEFT)

#Button 3
button1=tk.Button(root,text="Draw", command = update_canvas)
button1.pack(side=LEFT)

#Button 2
button2=tk.Button(root,text="Analyze", command = analysis)
button2.pack(side=LEFT)

#Button 3
button3=tk.Button(root,text="Refine", command = refine)
button3.pack(side=LEFT)

#Button 4
button4=tk.Button(root,text="Clear plot", command = clear_canvas)
button4.pack(side=LEFT)

#Button 5
button5=tk.Button(root,text="Quit",command=root.quit)
button5.pack(side=LEFT)


#Slider thres
slider_thres = Scale(root, from_=0.001, to=0.501, tickinterval=0.2, resolution= 0.01, sliderlength = 20, length = 200, orient=HORIZONTAL, label = 'peak thres (ignore small peaks)')
slider_thres.set(0.1)
slider_thres.pack(side=RIGHT)

#Slider min distance
slider_min_dist = Scale(root, from_=1, to=100, tickinterval=20, resolution= 1, sliderlength = 20, length = 200, orient=HORIZONTAL, label = 'min dist (ignore neighbor peaks)')
slider_min_dist.set(2)
slider_min_dist.pack(side=RIGHT)

#Slider bin
slider_bin = Scale(root, from_= 0, to=400, tickinterval=100, sliderlength = 20, length = 200, orient=HORIZONTAL, label = '# bins (more peaks)')
slider_bin.set(200)
slider_bin.pack(side=RIGHT)


root.mainloop()
