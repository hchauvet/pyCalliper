# -*- coding: utf-8 -*-
#/usr/bin/python

"""
Created on Thu Aug 30 18:05:34 2012

@author: chauvet

wx interface for the MainWindows (project manager) of pyCalliper
edit picture Add Roi | Add scale and | Add exclusions zones

Part of pyCalliper project
"""

import wx
#Set matplotlib backend
import matplotlib
matplotlib.use('WXAgg')

import glob
import os
#pour la sauvegarde
import numpy as np
from scipy import array, hstack

from LibPyCalliper.ImageProcessor import *
from LibPyCalliper.PictureEditor import *
from LibPyCalliper.PlotGSWindows import *

from LibPyCalliper.Functions import *
import pickle

CURPATH = determine_path()

class ProjectManager(wx.Frame):

    def __init__(self,parent):

        super(ProjectManager, self).__init__(parent, title='pyCalliper',
            size=(450, 350))

        ico = wx.Icon(CURPATH+'/icons/calliper.png', wx.BITMAP_TYPE_PNG)
        self.SetIcon(ico)
        self.data = {} #init dict for storing all data
        self.Config = {} #Init dict for configuration parameters
        self.InitUI()
        self.InitMenu()
        self.Centre()
        self.Show()

    def InitConfig(self):
        #function to init the configuration dictionary
        self.Config['Measures'] = ['FilledImage','Centroid','MajorAxisLength','MinorAxisLength','BoundingBox','CentralMoments','BoundingBox']


    def InitUI(self):
        #self.panel = wx.Panel(self, -1)
        #self.frame = wx.Frame(None, -1, "Hello from wxPython")

        # Create the toolbar
        #
        toolbar = self.CreateToolBar()
        load_image = toolbar.AddTool(0, 'Select a folder containing images', wx.Bitmap(CURPATH+'/icons/images.png'),shortHelp='Load pictures folder')
        load_one_image = toolbar.AddTool(6, 'Select an image', wx.Bitmap(CURPATH+'/icons/image.png'),shortHelp='Load a picture')
        toolbar.AddSeparator()
        load_project = toolbar.AddTool(4, 'Load a project', wx.Bitmap(CURPATH+'/icons/load.png'),shortHelp='Load a pyCalliper project')
        save_project = toolbar.AddTool(3, 'Save the project', wx.Bitmap(CURPATH+'/icons/save.png'),shortHelp='Save project')
        toolbar.AddSeparator()
        run_detection = toolbar.AddTool(1, 'Run grain detection', wx.Bitmap(CURPATH+'/icons/wand.png'),shortHelp='Launch grain detection')
        plot_granulo = toolbar.AddTool(2, 'Plot the grain size distribution', wx.Bitmap(CURPATH+'/icons/chart_bar.png'),shortHelp='Plot the grain size distribution')
        export_granulo = toolbar.AddTool(5, 'Export the grain size distribution', wx.Bitmap(CURPATH+'/icons/export.png'),shortHelp = 'Export the grain size distribution')
        toolbar.Realize()

        self.Bind(wx.EVT_TOOL, self.OnComputationStart, run_detection)
        self.Bind(wx.EVT_TOOL, self.OpenImageFolder, load_image)
        self.Bind(wx.EVT_TOOL, self.OnLoadPicture, load_one_image)
        self.Bind(wx.EVT_TOOL, self.OnSaveProject, save_project)
        self.Bind(wx.EVT_TOOL, self.OnLoadProject, load_project)
        self.Bind(wx.EVT_TOOL, self.OnPlotGran, plot_granulo)
        self.Bind(wx.EVT_TOOL, self.ExportGranulo, export_granulo)
        #manage events
        #double click sur la liste -> ouverture de l'editeur
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListSelected)

        # Set up event handler for any worker thread results
        EVT_RESULT(self,self.OnComputationResult)
        # And indicate we don't have a worker thread yet
        self.worker = None

        #The ControlList
        self.ControlList()

        #Create boxes where silt and send number can be entered
        silt_txt = wx.StaticText(self, label=" Number of silts ")
        sand_txt = wx.StaticText(self, label=" Number of sands ")

        self.silt_textbox = wx.TextCtrl(
            self,
            size=(100,-1),
            style=wx.TE_PROCESS_ENTER)

        self.sand_textbox = wx.TextCtrl(
            self,
            size=(100,-1),
            style=wx.TE_PROCESS_ENTER)

        #Add action when the silts and sands are entered
        self.Bind(wx.EVT_TEXT, self.OnSandsEnter, self.sand_textbox)
        self.Bind(wx.EVT_TEXT, self.OnSiltsEnter, self.silt_textbox)

        #Gestion de la fermeture de la fenetre -> lance le calcul
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        #
        # Layout with box sizers
        #

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.list, 1, wx.ALL | wx.EXPAND )
        self.vbox.AddSpacer(10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        flags = wx.ALIGN_CENTER | wx.ALL
        vbox2.Add(silt_txt, 0, border=1, flag=flags)
        vbox2.Add(self.silt_textbox, 0, border=1, flag=flags)

        hbox.Add(vbox2, 0)
        hbox.Add((0, 0), 1, wx.EXPAND)
        vbox3 = wx.BoxSizer(wx.VERTICAL)
        flags = wx.ALIGN_CENTER | wx.ALL
        vbox3.Add(sand_txt, 0, border=1, flag=flags)
        vbox3.Add(self.sand_textbox, 0, border=1, flag=flags)
        hbox.Add(vbox3, 0)

        self.vbox.Add(hbox, 0, flag = wx.ALIGN_CENTER | wx.TOP )

        self.SetSizer(self.vbox)
        self.vbox.SetMinSize((400, 350))
        self.vbox.Fit(self)

    def InitMenu(self):
            #function to init the menu
            menubar = wx.MenuBar()

            #File Menu
            FileMenu = wx.Menu()
            #Process
            ProcessMenu = wx.Menu()

            menu_loadpict = FileMenu.Append(200, 'Load pictures', 'Load pictures from a given folder')
            menu_loadonepict = FileMenu.Append(212, 'Load one picture', 'Load a picture')
            menu_loadproject = FileMenu.Append(202, 'Load project', 'Load a pyCalliper project')
            menu_saveproject = FileMenu.Append(201, 'Save project', 'Save the current project')
            menu_export_gran = FileMenu.Append(203, 'Export Granulo (.txt)', 'Export the granulo to a text file')

            process_strat = ProcessMenu.Append(210, 'Start', 'Start the processing')
            process_stop = ProcessMenu.Append(211, 'Stop', 'Stop the processing')

            viewMenu = wx.Menu()

            #events
            self.Bind(wx.EVT_MENU, self.OpenImageFolder, menu_loadpict)
            self.Bind(wx.EVT_MENU, self.OnLoadPicture, menu_loadonepict)
            self.Bind(wx.EVT_MENU, self.OnSaveProject, menu_saveproject)
            self.Bind(wx.EVT_MENU, self.OnLoadProject, menu_loadproject)
            self.Bind(wx.EVT_MENU, self.ExportGranulo, menu_export_gran)
            self.Bind(wx.EVT_MENU, self.OnComputationStart, process_strat)
            self.Bind(wx.EVT_MENU, self.OnComputationStop, process_stop)

            menubar.Append(FileMenu, '&File')
            menubar.Append(ProcessMenu, '&Process')

            self.SetMenuBar(menubar)

    def OnSandsEnter(self,event):
        """
            Save the number of sands to config dict
        """
        #test si nul
        if event.GetString() != '':
            #save in object
            self.Config['number_of_sands'] = float(event.GetString())


    def OnSiltsEnter(self,event):
        """
            Save the number of silts to config dict
        """
        #test si nul
        if event.GetString() != '':
            #save in object
            self.Config['number_of_silts'] = float(event.GetString())

    def ShowSiltSandInfo(self):
        """
            Update silt and sand textboxes
        """
        if 'number_of_silts' in self.Config.keys():
            self.silt_textbox.ChangeValue(str(self.Config['number_of_silts']))

        if 'number_of_sands' in self.Config.keys():
            self.sand_textbox.ChangeValue(str(self.Config['number_of_sands']))


    def OnLoadProject(self, event):
        """
            Pour charger un projet
        """

        #Ouverture du gestionnaire de fichier
        dlg = wx.FileDialog( self, message="Open a project file ...",
                             defaultDir="~/", defaultFile="", wildcard="Pickle data (*.pkl)|*.pkl",
                             style=wx.FD_OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            #Ajout des donnees de configuration
            self.Config, self.data = LoadProject(path)

            #Update the list
            self.Populate_Control_list_from_project_file()

            #Update Silt and Sand textboxes
            self.ShowSiltSandInfo()


        dlg.Destroy()

    def OnLoadPicture(self,event):
        """
            Load a unique picture with a select file gui
        """

        #Ouverture du gestionnaire de fichier
        dlg = wx.FileDialog( self, message="Open a picture", defaultDir="~/",
                             defaultFile="", wildcard="Image file |*.JPG;*.png;*.jpg",
                             style=wx.FD_OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()

            #Get Image name
            image_path, image_name = os.path.split(path)

            #If this image not already exist in the list load them
            if image_name not in self.data.keys():
                self.data[image_name] = {'Name':image_name,'path':image_path,'proceded':False,'scale':None,'scale_img_and_true':None,'scale_coord':None,'ROI':None,'exclusion_zones':None,'ReadyToProced':False,'data':None}
                # 0 will insert at the start of the list
                # pos = self.list.InsertStringItem(0,image_name)
                pos = self.list.InsertItem(0, image_name)
                # add values in the other columns on the same row
                self.list.SetItem(pos,1,Create_statu_txt(self.data[image_name]))
            else:
                print("Image %s already exist"%image)
        #close the windows
        dlg.Destroy()

    def OnSaveProject(self, event):
        """
            Sauvegarde du projet
        """

        #test si besoin d'ouvrir une boite pour definir un dossier et un nom
        if 'project_save_file' not in self.Config.keys():
            dlg = wx.FileDialog(
            self, message="Save file as ...",
            defaultDir="~/",
            defaultFile="pycal.pkl", wildcard="Pickle data (*.pkl)|*.pkl", style=wx.FD_SAVE
            )

            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                #Save the path and file_name
                self.Config['project_save_file'] = path
            dlg.Destroy()

        if 'project_save_file' in self.Config.keys():
            with open(self.Config['project_save_file'], 'wb') as f:
                pickle.dump({'data':self.data,'config':self.Config}, f, protocol=2)


    def OpenImageFolder(self, event):
        """
            Fonction pour gerer la selection du dossier contenant les images
        """

        #fenetre de dialogue
        dd = wx.DirDialog(None, "Select directory containing images to load", "~/", 0, (10, 10), wx.Size(400, 300))

        # This function returns the button pressed to close the dialog
        ret = dd.ShowModal()

        # Let's check if user clicked OK or pressed ENTER
        if ret == wx.ID_OK:
            #save the image path
            self.img_path = dd.GetPath()
            print(self.img_path)
            #load the list
            self.Populate_Control_list()



        # The dialog is not in the screen anymore, but it's still in memory
        #for you to access it's values. remove it from there.
        dd.Destroy()

    def ControlList(self):

        """
            Liste qui va charger l'ensemble des photos avec les infos
        """

        id=wx.NewId()
        self.list=wx.ListCtrl(self,id,style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.list.Show(True)

        self.list.InsertColumn(0,"Name")
        self.list.InsertColumn(1,"Status")

        self.list.SetColumnWidth(0,150)
        self.list.SetColumnWidth(1,250)

    def Populate_Control_list(self):

        self.image_names = glob.glob(self.img_path + '/*.JPG')
        for image in self.image_names:
            image = os.path.basename(image)
            if image not in self.data.keys():
                self.data[image] = {'Name':image,'path':self.img_path,'proceded':False,'scale':None,'scale_img_and_true':None,'scale_coord':None,'ROI':None,'exclusion_zones':None,'ReadyToProced':False,'data':None}
                # 0 will insert at the start of the list
                pos = self.list.InsertItem(0,image)
                # add values in the other columns on the same row
                self.list.SetItem(pos,1,Create_statu_txt(self.data[image]))
            else:
                print("Image %s already exist"%image)

    def Populate_Control_list_from_project_file(self):

        #Fonction pour recharger la list avec les images d'un projet

        #clear the list
        self.list.DeleteAllItems()

        #boucle sur le repertoire image
        for i in self.data:
            name = self.data[i]['Name']
            pos = self.list.InsertItem(0,name)
            # add values in the other columns on the same row
            self.list.SetItem(pos,1,Create_statu_txt(self.data[name]))

    def OnListSelected(self, e):
        #gestion lors de la selection
        self.selected_index = e.GetIndex()
        self.selected_photo_name = self.list.GetItemText(self.selected_index)
        self.selected_photo = self.data[self.selected_photo_name]


        EditPictureWindows(self,None)

    def UpdateStatu(self,photo_name=None,special_txt=None):
        """
            Upload statu
            of current selected photo in list if photo_name = None
            else of the one of the photo_name
            if special_txt -> display this text else display a text from Create_statu_txt function
        """

        if photo_name:
            idx = find_in_list(self.list,photo_name,0)
        else:
            idx = self.selected_index

        if special_txt:
            msg = special_txt
        else:
            msg = Create_statu_txt(self.data[self.list.GetItemText(idx)])

        self.list.SetItem(idx, 1, msg)

    #Gestion du woker pour creer des sousprocessus de traitement
    #

    def OnComputationStart(self ,event):
        """Start Computation."""

        #si si tout est ok avant de faire les calculs
        for photo_name in self.data:
            # Trigger the worker thread unless it's already busy
            if not self.worker:
                if not self.data[photo_name]['proceded']:
                    if self.data[photo_name]['ReadyToProced']:
                        #set the name of the photo that need to be prosseded
                        self.computation_name = photo_name
                        self.DoSomeComputationWork()

    def DoSomeComputationWork(self):
        if not self.worker:
            #self.status.SetLabel('Starting computation '+self.photos[]['num'])
            self.UpdateStatu(self.computation_name,'Starting Computation')
            self.worker = WorkerThread(self,self.data[self.computation_name])


    def OnComputationStop(self, event):
        """Stop Computation."""
        # Flag the worker thread to stop if running
        if self.worker:
            #self.status.SetLabel('Trying to abort computation')
            print("trying to abort")
            self.worker.abort()

    def OnComputationResult(self, event):
        """Show Result status."""
        if event.data is None:
            # Thread aborted (using our convention of None return)
            #self.status.SetLabel('Computation aborted')
            self.UpdateStatu(self.computation_name,'Computation aborted')

        else:
            # Process results here
            #self.status.SetLabel('Computation Result: %s' % event.data)
            #print 'Computation result: %s' % event.data
            self.UpdateStatu(self.computation_name)

            #Restart the computation if needed
            for photo_name in self.data:
                if not self.data[photo_name]['proceded']:
                    if self.data[photo_name]['ReadyToProced']:
                        self.computation_name = photo_name
                        wx.FutureCall(1, self.DoSomeComputationWork)

        # In either event, the worker is done
        self.worker = None

    def OnPlotGran(self,event):
        #Open the plotgranulo windows
        ShowGranuloWindows(self)

    def OnClose(self,event):
        #Stop workers on close
        if self.worker:
            self.worker.abort()
            del(self.worker)

        #fermeture de cette fenetre
        self.Destroy()

    def ExportGranulo(self, event):
        """
            function to export granulo to a text file
        """

        #Get all grain size
        #Concatenate the grain size data
        total_gs = array([])
        total_gs_pix = array([])
        photo_name = array([])
        photo_scale = array([])


        #If len > 0 save this to file. First ask for a file name and place
        if len(self.data.keys()) > 0:

            dlg = wx.FileDialog(
            self, message="Save file as ...",
            defaultDir="~/",
            defaultFile="", wildcard="Text file |(*.txt)|*.txt|", style=wx.FD_SAVE
            )

            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()

                f = open(path,'w')
                f.write("#pyCalliper granulo file. Grain_size is the small axis length (from center to border)\n#Image_name\tGrain_size (mm)\tGrain_size (pixel)\tScale_length (pixel)\tScale_value (cm)\n")
                #Save the granulo to this file
                for name in self.data.keys():
                    if self.data[name]['data'] != None:
                        total_gs = GetGrainSize(self.data[name])
                        total_gs_pix = GetGrainSize(self.data[name],pixel=True)
                        photo_scale = self.data[name]['scale_img_and_true']

                        for i in range(len(total_gs)):
                            f.write("%s\t%0.3f\t%0.3f\t%0.3f\t%0.3f\n"%( name, total_gs[i], total_gs_pix[i], photo_scale[0], photo_scale[1] ) )

                f.close()


                #OLD STUFF np.savetxt(path,hstack( [photo_name, total_gs, total_gs_pix] ).T)

            dlg.Destroy()


#-------------------------------------------------------------------
