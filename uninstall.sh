#!/bin/bash

#SCRIPT TO REMOVE PyCalliper
#small bug in pip uninstall
sudo mv  /usr/local/lib/python2.6/dist-packages/pyCalliper-0.2.egg-info /usr/local/lib/python2.6/dist-packages/pyCalliper-0.2-py2.6.egg-info

sudo pip uninstall pyCalliper

