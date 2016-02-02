# -*- coding: utf-8 -*-
#/usr/bin/python

"""
Created on Thu Aug 30 18:05:34 2012

@author: chauvet

ImageProcessor contain the threaded worker for proceding the images

Part of pyCalliper project
"""

import wx
from reconnaissance_formes import GetGS, GetOrientation
from threading import *

import os #to get the separator
#Define some event needed for the worker (update txt when computing proces ended
# Define notification event for thread completion
#

EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data


# Thread class that executes processing
class WorkerThread(Thread):
    """Worker Thread Class."""
    def __init__(self, notify_window, photo):

        self.photo = photo
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread. Simulation of
        # a long process (well, 10s here) as a simple loop - you will
        # need to structure your processing so that you periodically
        # peek at the abort variable
        photo = self.photo
        gs, objects_found, measurements = GetGS(photo['path']+os.path.sep+photo['Name'],photo['scale'],
                        roi=photo['ROI'],exclude_zones=photo['exclusion_zones'],show=False,
                        flipudflag=photo['flipud'])

        if self._want_abort:
            # Use a result of None to acknowledge the abort (of
            # course you can use whatever you'd like or even
            # a separate event type)
            wx.PostEvent(self._notify_window, ResultEvent(None))
            return

        else:
            #Add proceded to the photos
            self.photo['proceded'] = True
            self.photo['data'] = {'gs':gs,'labeled_objects_found':objects_found,'ROI':photo['ROI'],'measurements':measurements}
            # Here's where the result would be returned (this is an
            # example fixed result of the number 10, but it could be
            # any Python object)
            wx.PostEvent(self._notify_window, ResultEvent(str(self.photo)))

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1

#-----------------------------------------------------------------------
