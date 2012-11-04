# -*- coding: utf-8 -*-
#/usr/bin/python

"""
Created on Thu Aug 30 18:05:34 2012

@author: chauvet

wx interface for edit the picture:  Add Roi | Add scale and | Add exclusions zones

Part of pyCalliper project
"""

import wx
#the backend is set in MainWindows.py
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar

from matplotlib.patches import Patch, Rectangle

from scipy import flipud, asarray, sqrt, shape, arange, cos, sin, array, hstack
from scipy import ndimage
from scipy.misc import imread

from reconnaissance_formes import GetGS, GetOrientation

from Functions import *
import os

CURPATH = determine_path()

#We need some function contained in Functions.py
from Functions import *
class EditPictureWindows(wx.Frame):
    """
        Class avec l'editeur pour gerer la photo
    """

    def __init__(self,parent,image_dict):
        wx.Frame.__init__(self, parent, title=parent.selected_photo['Name'])

        ico = wx.Icon(CURPATH+'/icons/calliper.png', wx.BITMAP_TYPE_PNG)
        self.SetIcon(ico)

        #store parent data les modification son repercutees sur le parent
        self.photo_data = parent.selected_photo
        self.parent = parent

        #Some constants
        self.flipud_needed = True

        self.InitMenu()
        self.InitUI()
        self.Show()


        self.LoadImage()
        self.UpdateDataOnGraph()

    def InitUI(self):
        #Constant load

        #For the scale
        #
        self.add_scale = False
        self.scale_pts = [None,None]
        self.scale_line = None #to store the graph line of the scale
        self.img_s = None #corresponding length on image
        self.true_s = 1 #true scale in centimeter

        # ROI Selection
        self.add_roi = False
        #Les points du recto
        self.roi_pts = [None,None]
        self.added_roi_rect = None #variable to store mpl patch of the ROI rectangle

        #Exclusion zones
        self.add_zone = False
        self.new_zone_pts = [None,None]
        self.new_zone_rect = []
        self.added_zone_rect = [] #variable to store mpl patch of the exclusion zones rectangle

        #Removed grain
        self.removed_rectangle = {}
        self.added_removed_rectangle = {}
        self.removed_label = [] #list to store label of removed grains (or items)

        #For reprocessing and image
        self.reprocess = False

        # ---------------------------------------------------------------------
        #Main panel
        self.panel = wx.Panel(self)

        # Create the toolbar
        #
        self.toolbar = self.CreateToolBar()
        ascale = self.toolbar.AddLabelTool(0, 'Add scale', wx.Bitmap(CURPATH+'/icons/scale_edit.png'),shortHelp='Draw scale on picture')
        aroi = self.toolbar.AddLabelTool(1, 'Add ROI', wx.Bitmap(CURPATH+'/icons/roi_add.png'),shortHelp='Add a region of interest')
        azone = self.toolbar.AddLabelTool(2, 'Add ROI', wx.Bitmap(CURPATH+'/icons/zone_add.png'),shortHelp='Add an exclusion zone')
        reprocess =self.toolbar.AddLabelTool(3, 'Process on close', wx.Bitmap(CURPATH+'/icons/flag_green.png'),shortHelp='Reprocess this picture')
        flipud_tb =self.toolbar.AddLabelTool(4, 'flipud', wx.Bitmap(CURPATH+'/icons/flipud.png'),shortHelp='Flip up-down this picture')

        if not self.photo_data['proceded']:
            self.toolbar.EnableTool(3,False)

        self.toolbar.Realize()

        self.Bind(wx.EVT_TOOL, self.AddScale, ascale)
        self.Bind(wx.EVT_TOOL, self.AddRoi, aroi)
        self.Bind(wx.EVT_TOOL, self.AddZone, azone)
        self.Bind(wx.EVT_TOOL, self.Reprocess, reprocess)
        self.Bind(wx.EVT_TOOL, self.OnFlipud, flipud_tb)

        # ------------------------------------------------

        #Gestion de la fermeture de la fenetre -> lance le calcul
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Create the mpl Figure and FigCanvas objects.
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.canvas = FigCanvas(self.panel, -1, self.fig)

        # Manage canvas events
        # Bind the 'pick' event for clicking on one of the bars
        #
        self.canvas.mpl_connect('button_press_event', self.OnGraphClick)
        self.canvas.mpl_connect('motion_notify_event', self.OnGraphMove)
        self.canvas.mpl_connect('pick_event', self.OnGraphPick)
        # Since we have only one plot, we can use add_axes
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        self.axes = self.fig.add_subplot(111)

        # Create the navigation toolbar, tied to the canvas
        #
        self.toolbar = NavigationToolbar(self.canvas)

        # Create text zones for scale

        txt_label = wx.StaticText(self.panel, label=" Scale ")
        scale_txt = wx.StaticText(self.panel, label="Pixels = ")
        scale_txt2 = wx.StaticText(self.panel, label="cm")

        self.imgscale_textbox = wx.TextCtrl(
            self.panel,
            size=(80,-1),
            style=wx.TE_READONLY)

        self.truescale_textbox = wx.TextCtrl(
            self.panel,
            size=(80,-1),
            style=wx.TE_PROCESS_ENTER)
        #Add action when the true scale is enter
        self.Bind(wx.EVT_TEXT, self.OnScaleTextEnter, self.truescale_textbox)

        #
        # Layout with box sizers
        #

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.toolbar, 0, wx.EXPAND)
        self.vbox.AddSpacer(10)

        self.vbox.Add(txt_label, 0)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        flags = wx.ALIGN_LEFT | wx.ALL | wx.ALIGN_CENTER_VERTICAL
        self.hbox.Add(self.imgscale_textbox, 0, border=1, flag=flags)
        self.hbox.Add(scale_txt, 0, border=1, flag=flags)
        self.hbox.Add(self.truescale_textbox, 0, border=1, flag=flags)
        self.hbox.Add(scale_txt2, 0, border=1, flag=flags)

        self.vbox.Add(self.hbox, 0, flag = wx.ALIGN_LEFT | wx.TOP)

        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)

        #Update the scale
        self.ShowScale()

    def InitMenu(self):
        #function to init the menu
        menubar = wx.MenuBar()

        #Edit Menu
        EditMenu = wx.Menu()

        remscale = EditMenu.Append(100, 'Remove scale', 'Remove the scale on the current picture')
        remROI = EditMenu.Append(11, 'Remove ROI', 'Remove the region of interest')
        remZone = EditMenu.Append(12, 'Remove exclusion zones', 'Remove exclusion zones')

        viewMenu = wx.Menu()

        #events
        self.Bind(wx.EVT_MENU, lambda event, keys=['scale','scale_coord'], default_values=[None,[None,None]]: self.RemoveData(event, keys, default_values), remscale)
        self.Bind(wx.EVT_MENU, lambda event, keys=['ROI'], default_values=[None]: self.RemoveData(event, keys, default_values), remROI)
        self.Bind(wx.EVT_MENU, lambda event, keys=['exclusion_zones'], default_values=[None]: self.RemoveData(event, keys, default_values), remZone)

        menubar.Append(EditMenu, '&Edit')
        self.SetMenuBar(menubar)

    def Reprocess(self, event):
        #Turn the reprocess flag to true and updata photo_data
        self.reprocess = True
        self.photo_data['proceded'] = False

        self.UpdateParentList()

    def ShowScale(self):
        """
            pour mettre a jour l'affichage de l'echelle
        """

        saved_scale = self.photo_data['scale']
        if saved_scale == None:
            self.imgscale_textbox.ChangeValue("None")
        else:
            self.imgscale_textbox.ChangeValue(str(saved_scale.round(2)))

        self.truescale_textbox.ChangeValue(str(self.true_s))

    def LoadImage(self):
        img = imread(self.photo_data['path']+os.path.sep+self.photo_data['Name'])

        if self.flipud_needed:
            self.axes.imshow(flipud(img), interpolation='nearest',animated=True)
        else:
            self.axes.imshow(img, interpolation='nearest',animated=True)

        self.canvas.draw()
        #store the background boundary box
        self.fig_bg = self.canvas.copy_from_bbox(self.axes.bbox)
        #Save limits
        self.xlims = self.axes.get_xlim()
        self.ylims = self.axes.get_ylim()

    #action when flipud toolbar button is pressed
    def OnFlipud(self,e):
        if self.flipud_needed:
            self.flipud_needed = False
        else:
            self.flipud_needed = True

        #clear
        self.axes.clear()
        #Reload
        self.LoadImage()
        self.UpdateDataOnGraph()

    def OnGraphClick(self,e):

        # test if we are editing the scale
        if self.add_scale:
            #print 'you pressed', e.button, e.xdata, e.ydata
            xi, yi = (round(n,2) for n in (e.xdata, e.ydata))

            if not self.scale_pts[0] and not self.scale_pts[1]:
                #add the first point to self.scale_pts
                self.scale_pts[0] = (xi,yi)
                #create the plot
                self.scale_line, = self.axes.plot(xi,yi,'go-',mec='w',ms=8,mew=2,linewidth=2,label='scale')

                #put the good limits
                self.axes.set_xlim(self.xlims)
                self.axes.set_ylim(self.ylims)
                self.canvas.draw()

            elif not self.scale_pts[1]:

                self.scale_pts[1] = (xi,yi)

                #release the editing scale boolean and compute the scale
                self.edit_scale = False
                self.img_s = sqrt((self.scale_pts[0][0]-self.scale_pts[1][0])**2+(self.scale_pts[0][1]-self.scale_pts[1][1])**2)

                #update the scale
                self.scale_line.set_data([[self.scale_pts[0][0],self.scale_pts[1][0]],[self.scale_pts[0][1],self.scale_pts[1][1]]])

                #put the good limits
                self.axes.set_xlim(self.xlims)
                self.axes.set_ylim(self.ylims)
                self.canvas.draw()

                #unactive add_scale
                self.add_scale = False
                #Save to image dict
                self.SaveModification('scale',self.img_s/self.true_s)
                #Save scale position
                self.SaveModification('scale_coord',self.scale_pts)


                #Update the scale on screen
                self.ShowScale()

        #Test if we are adding a roi
        if self.add_roi:

            self.CompleteRectangleOnClick(e,self.roi_pts,self.roi_rect,'ROI')

        #Test if we are adding a zone
        if self.add_zone:

            self.CompleteRectangleOnClick(e,self.new_zone_pts,self.new_zone_rect[-1],'exclusion_zones')


    def CompleteRectangleOnClick(self,event,pts_var,rectangle_var,name):
        e = event
        if e.xdata != None and e.ydata != None:
            #test sur les points
            if pts_var[0] == None and pts_var[1] == None:
                pts_var[0] = (e.xdata,e.ydata)
                #update the rectangle
                rectangle_var.set_xy(pts_var[0])

            elif pts_var[1] == None:
                pts_var[1] = (e.xdata,e.ydata)
                #add with and length to the rectange
                rectangle_var.set_width(e.xdata-pts_var[0][0])
                rectangle_var.set_height(e.ydata-pts_var[0][1])


                #Save the data
                self.SaveModification(name,[int(pts_var[0][0]),int(pts_var[0][1]),int(pts_var[1][0]),int(pts_var[1][1])])

                #Restart si exclusion_zones
                if name == 'exclusion_zones':
                    self.add_zone = False
                    self.new_zone_pts = [None,None]

    def OnGraphMove(self,event):

        if event.xdata != None and event.ydata != None:
            if self.add_roi:

                #test sur les points
                if self.roi_pts[0] != None and self.roi_pts[1] == None:

                    #update rectangle with coordinate
                    self.roi_rect.set_width(event.xdata-self.roi_pts[0][0])
                    self.roi_rect.set_height(event.ydata-self.roi_pts[0][1])

                    self.canvas.draw()

            #pour les zones
            if self.add_zone:
                #test sur les points
                if self.new_zone_pts[0] != None and self.new_zone_pts[1] == None:

                    #update rectangle with coordinate
                    self.new_zone_rect[-1].set_width(event.xdata-self.new_zone_pts[0][0])
                    self.new_zone_rect[-1].set_height(event.ydata-self.new_zone_pts[0][1])

                    self.canvas.draw()

    def OnGraphPick(self,event):
        """
            Function to manage when an element is picked on the plot
        """

        #print "a cl has been picked"
        #print event.ind

        #Test right click: Remove this item
        if event.mouseevent.button == 3:
            #test if we have picked a linecollection class
            if 'LineCollection' in str(event.artist):
                #get label of the selected object
                label = self.photo_data['data']['measurements'][event.ind[0]]['Label']

                #test if label is already in removed items
                if label not in self.removed_label:
                    #Rectangle limits
                    minr, minc, maxr, maxc = self.photo_data['data']['measurements'][event.ind[0]]['BoundingBox']
                    if self.photo_data['data']['ROI'] != None:
                        yo = min(self.photo_data['data']['ROI'][1],self.photo_data['data']['ROI'][3])
                        xo = min(self.photo_data['data']['ROI'][0],self.photo_data['data']['ROI'][2])
                        minc += xo
                        maxc += xo
                        minr += yo
                        maxr += yo

                    #Add a grey rectangle over the removed item
                    self.removed_rectangle[event.ind[0]] = Rectangle((minc,minr),maxc-minc,maxr-minr,edgecolor='k',fill=False,hatch='/',zorder=1000)
                    self.added_removed_rectangle[event.ind[0]] = self.axes.add_patch(self.removed_rectangle[event.ind[0]])

                    #Add the label to the list
                    self.removed_label.append(label)
                    #Save this to photo data
                    self.SaveModification('removed_items_label',self.removed_label)

                    self.canvas.draw()

        #Test left click: Restore this item
        if event.mouseevent.button == 1:
            #test if we have picked a linecollection class
            if 'LineCollection' in str(event.artist):
                label = self.photo_data['data']['measurements'][event.ind[0]]['Label']
                #test if label is already in removed items
                if label in self.removed_label:
                    #remove the mpatch of the rectangle
                    self.added_removed_rectangle[event.ind[0]].remove()
                    #Remove rectangle
                    self.removed_rectangle.pop(event.ind[0])

                    #remove label from removed_list
                    self.removed_label.remove(label)

                    #Save this to photo data
                    self.SaveModification('removed_items_label',self.removed_label)

                    self.canvas.draw()

    def OnScaleTextEnter(self,event):
        #Action when a true scale is entered

        #test si nul
        if event.GetString() != '':
            #save in object
            self.true_s = float(event.GetString())

            #if img scale != none save in image dict file
            if self.img_s != None:
                self.SaveModification('scale',self.img_s/self.true_s)


    # Toolbar Actions
    def AddScale(self, e):
            #reset to false if is clicked again
            if self.add_scale or (self.scale_pts[0] != None and self.scale_pts[1] != None):
                self.add_scale = False
            else:
                self.add_scale = True
                #put other to false
                self.add_roi = False
                self.add_zone = False

    def AddRoi(self,e):
        #If false
        if not self.add_roi and self.roi_pts[1] == None:
            #Init a rectangle (xy),width,height
            self.roi_rect = Rectangle((None,None),None,None,facecolor='none')
            #add the rect to the plot
            self.added_roi_rect = self.axes.add_patch(self.roi_rect)
            self.add_roi = True
            #put other to false
            self.add_scale = False
            self.add_zone = False

    def AddZone(self, e):

        if not self.add_zone:
            self.new_zone_rect.append(Rectangle((None,None),None,None,facecolor='none',edgecolor='y'))

            self.added_zone_rect.append(self.axes.add_patch(self.new_zone_rect[-1]))
            self.add_zone = True
            #put other to false
            self.add_roi = False
            self.add_scale = False

    def SaveModification(self,key,values):
        #save modified things to the image dict
        #TODO: special append for exclusion zones

        #save the roi to image dict
        if key == 'exclusion_zones' :
            #test if we need to init the list
            if self.photo_data[key] == None:
                self.photo_data[key] = []

            self.photo_data[key].append(values)
        else:

            self.photo_data[key] = values

        self.UpdateParentList()



    def UpdateParentList(self):
        """
            Function to update the parent control list of pictures
        """

        #on chop l'item de la colone statu (1) correspondant a la photo entrain d'etre travaillee
        self.parent.list.SetStringItem(self.parent.selected_index, 1, Create_statu_txt(self.photo_data))

    def OnClose(self, e):
        """
            Gestion de la fermeture de l'editeur de figure -> Lance OnComputationStart de la fenetre parente
        """

        #Ajout un option pour relance le calcul
        #self.parent.OnComputationStart()

        #fermeture de cette fenetre
        self.Destroy()

    def UpdateDataOnGraph(self,no_redraw=['']):
        """
            gestion des donnees a tracer

            no_redraw allow to not redraw some part
        """

        #TODO: un filtre pour afficher grain tourves oui/non

        if self.photo_data['data'] != None and 'data' not in no_redraw:

            if 'labeled_objects_found' in self.photo_data['data']:

                obg_shape = shape(self.photo_data['data']['labeled_objects_found'])
                xi = arange(obg_shape[1])
                yi = arange(obg_shape[0])

                if self.photo_data['data']['ROI'] != None:
                    xi += min(self.photo_data['data']['ROI'][0],self.photo_data['data']['ROI'][2])
                    yi += min(self.photo_data['data']['ROI'][1],self.photo_data['data']['ROI'][3])

                #Store the contour line
                cl = self.axes.contour(xi,yi,ndimage.binary_fill_holes(self.photo_data['data']['labeled_objects_found']), 1, linewidths=1.5, colors='c')

                #Add a picker radius to each lines
                for line in cl.collections:
                    line.set_picker(10)

                #Calcul des axes pour les afficher sur les cailloux
                self.PlotItemAxis()


        #Plot the roi
        if self.photo_data['ROI'] != None and 'ROI' not in no_redraw:
            self.roi_pts = self.photo_data['ROI']
            if self.added_roi_rect == None:
                self.roi_rect = Rectangle((None,None),None,None,fc='none')

            self.roi_rect.set_xy((self.photo_data['ROI'][0],self.photo_data['ROI'][1]))
            self.roi_rect.set_width(self.photo_data['ROI'][2] - self.photo_data['ROI'][0])
            self.roi_rect.set_height(self.photo_data['ROI'][3] - self.photo_data['ROI'][1])


            self.added_roi_rect = self.axes.add_patch(self.roi_rect)



        if self.photo_data['exclusion_zones'] != None and 'exclusion_zones' not in no_redraw:
            for zone in self.photo_data['exclusion_zones'] :
                self.new_zone_rect.append(Rectangle((zone[0],zone[1]),zone[2] - zone[0],zone[3] - zone[1],facecolor='none',edgecolor='y'))
                #add patch to axes
                self.added_zone_rect.append(self.axes.add_patch(self.new_zone_rect[-1]))



        if self.photo_data['scale'] != None and 'scale' not in no_redraw:
            self.scale_pts = self.photo_data['scale_coord']
            self.scale_line = self.axes.plot((self.scale_pts[0][0],self.scale_pts[1][0]), (self.scale_pts[0][1],self.scale_pts[1][1]), 'bo-',mec='w',ms=8,mew=2,linewidth=2,picker=5,label='scale')


        #plot the removed items
        if 'removed_items_label' in self.photo_data:
            #Load the list in self.removed_label
            self.removed_label = self.photo_data['removed_items_label']
            for label in self.removed_label:

                minr, minc, maxr, maxc = self.photo_data['data']['measurements'][label-1]['BoundingBox']

                if self.photo_data['data']['ROI'] != None:
                    yo = min(self.photo_data['data']['ROI'][1],self.photo_data['data']['ROI'][3])
                    xo = min(self.photo_data['data']['ROI'][0],self.photo_data['data']['ROI'][2])
                    minc += xo
                    maxc += xo
                    minr += yo
                    maxr += yo

                #Add a grey rectangle over the removed item
                self.removed_rectangle[label-1] = Rectangle((minc,minr),maxc-minc,maxr-minr,edgecolor='k',fill=False,hatch='/',zorder=1000)
                self.added_removed_rectangle[label-1] = self.axes.add_patch(self.removed_rectangle[label-1])

        #limits
        self.axes.set_xlim(self.xlims)
        self.axes.set_ylim(self.ylims)
        #refresh canvas.
        self.canvas.draw()



    def PlotItemAxis(self):
        for measure in self.photo_data['data']['measurements']:
            measure['Orientation2'] = GetOrientation(measure['CentralMoments']) #compute ellipse orientation

            x0 = measure['Centroid'][1]
            y0 = measure['Centroid'][0]
            x1 = x0 + cos(measure['Orientation2']) * 0.5 * measure['MajorAxisLength']
            y1 = y0 - sin(measure['Orientation2']) * 0.5 * measure['MajorAxisLength']
            x2 = x0 - sin(measure['Orientation2']) * 0.5 * measure['MinorAxisLength']
            y2 = y0 - cos(measure['Orientation2']) * 0.5 * measure['MinorAxisLength']

            #Ajout de la ROI
            if self.photo_data['data']['ROI'] != None:
                xroi = min(self.photo_data['data']['ROI'][0],self.photo_data['data']['ROI'][2])
                yroi = min(self.photo_data['data']['ROI'][1],self.photo_data['data']['ROI'][3])
            else:
                xroi = 0
                yroi = 0

            self.axes.plot(array([x0, x1])+xroi, array([y0, y1])+yroi, '-r', linewidth=2.5)
            self.axes.plot(array([x0, x2])+xroi, array([y0, y2])+yroi, '-r', linewidth=2.5)
            self.axes.plot(x0+xroi, y0+yroi, '.g', markersize=8)

    def RemoveData(self,event,keys,default_values):

        #remove the data from photo_data dict and put the default value
        for key, value in zip(keys,default_values):
            self.photo_data[key] = value

            #put special value
            if key == 'scale':
                self.scale_pts = [None,None]
                self.ShowScale()
                #clean lines
                if self.scale_line != None:
                    self.scale_line.remove()
                #reset scale_line to None
                self.scale_line = None

            if key == 'ROI':
                self.roi_pts = [None,None]
                if self.added_roi_rect != None:
                    self.added_roi_rect.remove()
                self.added_roi_rect = None

            if key == 'exclusion_zones':
                self.new_zone_pts = [None,None]
                self.new_zone_rect = []
                if self.added_zone_rect != []:
                    for added_zone in self.added_zone_rect:
                        added_zone.remove() #remove the Rectangle on the plot

                #reset the added_zone to empty list
                self.added_zone_rect = []



        #update parent
        self.UpdateDataOnGraph()
        self.UpdateParentList()

