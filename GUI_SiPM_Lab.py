#!/usr/bin/env python

###################################################################
#                        README                                   #
# MASTER FRONTEND GUI script that binds several frontend scripts  #
###################################################################

import matplotlib
#matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import Tkinter as tk
from Tkinter import *
#from Tkinter import ttk
import ttk

from matplotlib import colors
import matplotlib.pyplot as plt
import numpy as np

import subprocess, os

LARGE_FONT= ("Verdana", 12)


#########################################################
# HERE ARE CLASSES FOR DIFFERENT WINDOWS OF THE GUI     #
#########################################################

# Home_windows ties all the pages together
class Home_windows(tk.Tk):

	def __init__(self, *args, **kwargs):
        
		tk.Tk.__init__(self, *args, **kwargs)
		tk.Tk.wm_title(self, "SiPM lab software")
        
        
		container = tk.Frame(self)
		container.pack(side="top", fill="both", expand = True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)

		self.frames = {}

		for F in (PageStart, PageOne, PageTwo, PageThree, PageQuit):
			frame = F(container, self)
			self.frames[F] = frame
			frame.grid(row=0, column=0, sticky="nsew")

		self.show_frame(PageStart)

	def show_frame(self, cont):

		frame = self.frames[cont]
		frame.tkraise()

#Starting page
class PageStart(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="HOME", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button = ttk.Button(self, text="SiPM software", command=lambda: controller.show_frame(PageOne))
	#button.hover = HoverInfo(button, 'Collect SiPM data and analyze them')
        button.pack(fill=X,padx=10, pady=10)

        button2 = ttk.Button(self, text="PIN diode software", command=lambda: controller.show_frame(PageTwo))
	#button2.hover = HoverInfo(button2, 'Collect PIN diode data and analyze them')
        button2.pack(fill=X,padx=10, pady=10)

        button3 = ttk.Button(self, text="Instrument Dashboard", command=lambda: controller.show_frame(PageThree))
	#button3.hover = HoverInfo(button3, 'Random pretty plot')
        button3.pack(fill=X,padx=10, pady=10)

        button4 = ttk.Button(self, text="Quit Software", command=lambda: controller.show_frame(PageQuit))
	#button4.hover = HoverInfo(button4, 'Exit program')
        button4.pack(fill=X,padx=10, pady=10)


#This is the page for SiPM software
class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="SiPM software", font=LARGE_FONT)
        label.pack(padx=10,pady=10)

        #button0 = ttk.Button(self, text="Collect SiPM data",command=lambda: controller.show_frame(PageTwo))
	button0 = ttk.Button(self, text="Collect SiPM data",command=run_SiPM)
        button0.pack(fill=X,padx=10, pady=10)
	
	button1 = ttk.Button(self, text="Analyze SiPM data", command=analyze_SiPM)
	button1.pack(fill=X,padx=10, pady=10)

        button2 = ttk.Button(self, text="Back to Home", command=lambda: controller.show_frame(PageStart))
        button2.pack(fill=X,padx=10, pady=10)


#This is the page for PIN diode software
class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="PIN software", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        #button0 = ttk.Button(self, text="Collect SiPM data",command=lambda: controller.show_frame(PageTwo))
	button0 = ttk.Button(self, text="Collect PIN data",command=run_PIN)
        button0.pack(fill=X,padx=10, pady=10)
	
	button1 = ttk.Button(self, text="Analyze PIN data", command=lambda: controller.show_frame(PageStart))
	button1.pack(fill=X,padx=10, pady=10)

        button2 = ttk.Button(self, text="Back to Home", command=lambda: controller.show_frame(PageStart))
        button2.pack(fill=X,padx=10, pady=10)


#This is the instrument dashboard page
class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Instrument dashboard", font=LARGE_FONT)
        label.pack(fill=X,pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home", command=lambda: controller.show_frame(PageStart))
        button1.pack()


# This is the page that really quit the GUI
class PageQuit(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="REALLY QUIT?", font=LARGE_FONT)
        label.pack(fill=X,pady=10,padx=10)

        #button0 = ttk.Button(self, text="Collect SiPM data",command=lambda: controller.show_frame(PageTwo))
	button0 = ttk.Button(self, text="Quit!",command=controller.quit)
        button0.pack(fill=X,padx=10, pady=10)
	
        button2 = ttk.Button(self, text="Back to Home", command=lambda: controller.show_frame(PageStart))
        button2.pack(fill=X,padx=10, pady=10)



#############################################################
# CLASS FOR INFO WHEN THE MOUSE HOVERS ABOVE THE BUTTONS    #
#############################################################
class HoverInfo(Menu):
	def __init__(self, parent, text, command=None):
		self._com = command
		Menu.__init__(self,parent, tearoff=0)
		if not isinstance(text, str):
			raise TypeError('Trying to initialise a Hover Menu with a non string type: ' + text.__class__.__name__)
		toktext=re.split('\n', text)
		for t in toktext:
			self.add_command(label = t)
			self._displayed=False
			self.master.bind("<Enter>",self.Display )
			self.master.bind("<Leave>",self.Remove )
	def __del__(self):
		self.master.unbind("<Enter>")
		self.master.unbind("<Leave>")
	 
	def Display(self,event):
		if not self._displayed:
			self._displayed=True
			self.post(event.x_root, event.y_root)
		if self._com != None:
			self.master.unbind_all("<Return>")
			self.master.bind_all("<Return>", self.Click)
	 
	def Remove(self, event):
		if self._displayed:
			self._displayed=False
			self.unpost()
		if self._com != None:
			self.unbind_all("<Return>")
	 
	def Click(self, event):
		self._com()



##############################################################
# UTILITY FUNCTIONS THAT CALL OTHER STANDALONE SCRIPTS       #
##############################################################
def run_SiPM():
	if os.name=="posix":
		subprocess.Popen(['xterm', '-e', 'python run_SiPM.py'])
	elif os.name == "nt":
		import run_SiPM

def analyze_SiPM():
	if os.name=="posix":
		subprocess.Popen(['xterm', '-e', 'python analyze_SiPM.py'])
	elif os.name == "nt":
		import analyze_SiPM

def run_PIN():
	if os.name=="posix":
		subprocess.Popen(['xterm', '-e', 'python run_PIN.py'])
	elif os.name == "nt":
		import run_PIN



#################################################
# TKINTER MAIN LOOP THAT CONTROLS THE GUI       #
#################################################
app = Home_windows()
app.mainloop()
