# -*- coding: utf-8 -*-
#/usr/bin/python

"""
Created on Thu Aug 30 18:05:34 2012

@author: chauvet

This file contain usefull functions

Part of pyCalliper project
"""
import os
from numpy import load as numpy_load

# Function to update statu from the image data dictionary
def Create_statu_txt(one_image_dict):
    """
        look at image key value to define a statu message
        return a string statu

    """

    statu = ''
    if one_image_dict['data'] == None:
        err = 0
        #Test si l'echelle est definie
        if one_image_dict['scale'] == None:
            statu += ' No scale defined '
            err += 1

        if err == 0:
            statu += ' Ready to procced !'
            #put image flag to ready_to_proced to true
            one_image_dict['ReadyToProced'] = True

    else:

        nb_cailloux = len(one_image_dict['data']['gs'])
        statu += ' Found %s items' % nb_cailloux

        if one_image_dict['scale'] == None:
            statu += ' | No scale defined'

        if one_image_dict['proceded'] == False:
            statu += ' | Ok for new proceding'

    return statu

#function to find a text in a listctrl and return it's index
def find_in_list(listctrl,searchValue,col=0):
    for idx in range(listctrl.GetItemCount()):
            item = listctrl.GetItem(idx, col)
            if item.GetText() == searchValue:
                    return idx


#Function to get the path of the current file
def determine_path ():
    try:
        root = __file__
        if os.path.islink (root):
            root = os.path.realpath (root)
        return os.path.dirname (os.path.abspath (root))
    except:
        print "I'm sorry, but something is wrong."
        print "There is no __file__ variable. Please contact the author."
        sys.exit ()

#Function To load the data and the Configuration
def LoadProject(project_file):
    """
        Function to load a pyCalliper project file. It returns config and data dictionnaries

            config, data = LoadProject('my_project.npy')
    """
    alldata = numpy_load(project_file)

    return alldata[1], alldata[0]

#Function to get the grain size from a photo_data dictionary
def GetGrainSize(photo_data):
    """
        Extract grain size from a photo_data dict. photo_data need the key 'measurements' in photo_data['data']
        return the grain size
    """

    gs = []
    #test on photo_data
    if 'measurements' in photo_data['data'].keys():
        for mesure in photo_data['data']['measurements']:
            gs.append((mesure['MinorAxisLength']/photo_data['scale'])*10**1)


    return gs

