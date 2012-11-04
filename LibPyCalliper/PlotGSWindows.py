# -*- coding: utf-8 -*-
#/usr/bin/python

"""
Created on Thu Aug 30 18:05:34 2012

@author: chauvet

wx interface for display de grain size distribution plot

Part of pyCalliper project
"""

import wx
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar

from scipy import array, hstack

#The granulo lib contain functions to compute granulo stuffs from grainsize lists
import granulo as gr

from Functions import *
CURPATH = determine_path()
class ShowGranuloWindows(wx.Frame):
    """
        Class avec pour montrer le graphique de la granulo du projet
    """

    def __init__(self,parent):
        wx.Frame.__init__(self, parent, title="Granulo Plot")

        ico = wx.Icon(CURPATH+'/icons/calliper.png', wx.BITMAP_TYPE_PNG)
        self.SetIcon(ico)

        #store parent data les modification son repercutees sur le parent
        self.parent = parent
        self.InitUI()
        self.Show()

        self.PlotGranulo()

    def InitUI(self):

        # ---------------------------------------------------------------------
        #Main panel
        self.panel = wx.Panel(self)

        # Create the mpl Figure and FigCanvas objects.
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.canvas = FigCanvas(self.panel, -1, self.fig)

        # Since we have only one plot, we can use add_axes
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        self.axes = self.fig.add_subplot(111)

        # Create the navigation toolbar, tied to the canvas
        #
        self.toolbar = NavigationToolbar(self.canvas)

        #
        # Layout with box sizers
        #

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.toolbar, 0, wx.EXPAND)

        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)

    def PlotGranulo(self):
        """
            Use the granulo function to plot the granulo from project data
        """

        #Add silt and sand cathegories with the number of silt and sands
        categories = []
        if 'number_of_silts' in self.parent.Config.keys():
            categories.append({ 'name':'silt', 'names':( 'silt', 'si' ), 'dmax':0.01, 'nog':self.parent.Config['number_of_silts'] })

        if 'number_of_sands' in self.parent.Config.keys():
            categories.append({ 'name':'sand', 'names':( 'sable', 'sa', 'sand' ), 'dmax':0.1, 'nog':self.parent.Config['number_of_sands'] })

        #Concatenate the grain size data
        total_gs = array([])
        for name in self.parent.data.keys():
            if self.parent.data[name]['data'] != None:

                total_gs = hstack([total_gs,GetGrainSize(self.parent.data[name])])

        if len(total_gs) > 0:

            #Plot the granulo on self.axes
            gr.plot_granulo(total_gs, categories, fig_axes = self.axes )
            #update the figure canvas
            self.canvas.draw()

