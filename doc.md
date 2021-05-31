==========
pyCalliper
==========

.. image:: calliper.png

.. |date| date::

:author: H.chauvet 
:contact: chauvet[at]ipgp[dot]com
:version: 0.1
:Date: |date|
:copyright: This document has been placed in the public domain. 

.. contents:: Table of Contents

About
=====

PyCalliper is a small python tool to extract grain size distribution from pictures. It allows to replace a calliper on the field by pictures of sampled (using the Wolman technics) grains. 


Installation
============


Using python pip (http://pypi.python.org/pypi/pip). This will download all latest versions of required python packages:

   - matplotlib
   - scypi
   - numpy
   - scikits-image (http://scikits-image.org/)
   - setuptools

For Mac users
-------------

Useful informations about python and pip installation can be found there 
http://docs.python-guide.org/en/latest/starting/install/osx/

For Windows users
-----------------

Useful informations about python and pip installation can be found there 
http://docs.python-guide.org/en/latest/starting/install/win/

To install matplotlib and scikits-image from pip you need to install minggw compiler (see http://stackoverflow.com/a/5051281). 

The easiest way:
 1. Install the python(x,y) distribution. This install wxpython, matplotlib, numpy and scipy required by pyCalliper
    http://code.google.com/p/pythonxy/

 2. Install the last scikits-image with the binary installer provided by Christoph Gohlke
    http://www.lfd.uci.edu/~gohlke/pythonlibs/#scikits-image

 3. Install the pip package of pyCalliper

Pip package
-----------
To use python pip, just open a terminal an type:

.. code:: 
   
   sudo pip install https://morpho.ipgp.fr/OSS/public/include/Codes/pyCalliper-0.1.tar.gz

Run
===

On linux and mac
----------------

Open a terminal an type

.. code::

   pyCalliper

On Windows
----------

Open a command prompt and type:

.. code::

   python C:\Python27\Scripts\pyCalliper


This is for version 2.7 of python.

You can also create a shortcut. 

Screenshots
===========

Main windows
------------

.. figure:: pycalliper_main.png
   :align: center

   Project manager of pyCalliper. 

.. figure:: pycalliper_edit_picture.png
   :width: 700px
   :align: center

   Pictures editor of PyCalliper with a processed image.

Toolbars
--------

.. _toolbar1:
.. figure:: pjm_tb_2.png
   :align: center

   Project manager toolbar.


   =====  ====================================================
    num                         Action
   =====  ====================================================
     1     Load an image folder
     2     Load a single image
     3     Load a pyCalliper project
     4     Save the current project
     5     Start processing of ready images 
     6     Plot the grain size distribution
     7     Export the grain size distribution in a text file
   =====  ====================================================

.. _toolbar2:
.. figure:: pe_tb_2.png
   :align: center

   Picture editor toolbar.


   =====  ====================================================
    num                         Action
   =====  ====================================================
     1     Draw a scale on picture
     2     Draw a region of interest on the picture
     3     Add an exclusion zone to the picture
     4     Set this image for re-processing
     5     Flip this image up-down 
   =====  ====================================================

Quick start tutorial
====================

This quick tutorial shows how to use pyCalliper to process an example picture.
pyCalliper is decomposed in two main windows: a project manager and a picture editor.
Menu description for both of them is provided in section Toolbars_. In this tutorial we use the following image.

.. figure:: IMG_7213.JPG
   :align: center
   :width: 400px

   You can download this image `here <https://morpho.ipgp.fr/OSS/public/docs/doc_11/IMG_7213.JPG>`_ (right click > save link as).

Load one image
--------------

- on project manager use **file > load one image** or the button 2 of the toolbar1_.

- Image is loaded on the project manager image list and his status is set to "No scale defined"

.. figure:: pjm_one_pict.png
   :align: center

   One image loaded in the project manager


Open the picture editor
-----------------------

for this image by double clicking on it.

- define a scale using the button 1 of the toolbar2_. When the scale is defined the picture status in the project manager is set to "Ready to process".

- You can also define a Region Of Interest (ROI) and exclusion zones on the image with the button 2 and 3 of the toolbar2_ respectivly. Define a ROI allow to reduce significantly the processing time.

- When your image is ready, you can close the picture editor windows.

.. figure:: pe_new_img.png
   :align: center

   One image opened in picture editor

Process images 
--------------

By clicking the wand icon (button 5) of the toolbar1_. You can also use the menu **process > start**. The status of the image is set to "Starting computation". When the computation is finished, the image status displays the number of object found "Found xx items".

Check items
-----------

Check items found by the computation by opening the picture editor for the processed image.

- You can remove items by right clicking on its contour.

- To restore a removed item, just left click on its contour.

- You can also change exclusion zones and ROI, then you have to click on the green flag (button 4 of the toolbar2_) to set the image ready for a new computation. The image status is set to "OK for reprocess".

.. figure:: pe_img_processed.png
   :align: center

   One processed image opened in picture editor

Set the silts and sands
-----------------------

Just fill the sand and silt boxes.

.. figure:: pjm_grain_silt.png
   :align: center

   Sands and silts boxes at the bottom of the project manager

Plot grain size distribution
----------------------------

By clicking on the button 6 of the toolbar1_.

Save
----

- Save the entire project by clicking on the third button of the project manager toolbar.
- Export the grain size distribution to a text file (.txt) with the button 7 of the toolbar1_.

Use pyCalliper as python lib
============================

All libraries used by pyCalliper are stored in "/usr/local/lib/python-2.6/dist-packages/LibPyCalliper/" (if your python version is 2.6)

Load a project file
-------------------

.. code:: python


   #All common functions are stored in the Functions file
   from LibPyCalliper import Functions

   #Load the project file "my_proj.py"
   config, data = LoadProject('my_proj.py')

   #data is a dict with all picture data and config is 
   #also a dict with project configuration parameters
   
   print data.keys() #Display all pictures name of the project

   #display all entries for each pictures
   for key in data.keys():
       print data[key].keys()



