# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 17:16:30 2012

@author: terrain
"""

from numpy import array, concatenate, arange
from pylab import plot, xlim, ylim, xlabel, ylabel
import re as re

###########################
###########################

def extr_dig(the_str):
    number = ''.join( re.findall( '\d', the_str ) )
    if number == '':
        number = 1
    else:
        number = int(number)
    return number

###########################
###########################

def separate_sizes( the_data, categories ):

    lc = len(categories)
    size_array = array([])
    for category in categories:
        category['nog'] = 0

    for element in the_data:

        try:
            size_array = concatenate( ( size_array, [ float(element) ] ) )

        except:
            toggle_error = True

            for category in categories:
                if element.endswith( category['names'] ):
                    category['nog'] += extr_dig(element)
                    toggle_error = False
                    break

            if toggle_error:
                print('"' + element + '"' + ' is not a proper entry')

    return ( size_array, categories )

###########################
###########################

def plot_granulo( size_array, categories, the_label = 'granulo' , fig_axes = None):

    size_array.sort()
    grain_size = array([])
    n = array([])
    ncum = 0

    for category in categories:
        grain_size = concatenate( ( grain_size, [ category['dmax'] ] ) )
        ncum += category['nog']
        n = concatenate( ( n, [ ncum ] ) )

    grain_size = concatenate( ( grain_size, size_array ) )
    n = concatenate( ( n, arange( ncum + 1, ncum + 1 + len(size_array) ) ) )


    cdf = n/(max(n)*1.)

    #If an axes is given
    if fig_axes != None:
        fig_axes.plot( grain_size, cdf, label = the_label )
        fig_axes.set_ylim( [ 0, 1.01 ] )
        fig_axes.set_xlabel('grain size [mm]')
        fig_axes.set_ylabel('cdf')
    else:
        plot( grain_size, cdf, label = the_label )

        ylim( [ 0, 1.01 ] )
        xlabel('grain size [mm]')
        ylabel('cdf')

