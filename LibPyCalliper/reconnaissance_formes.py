# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 17:03:56 2012

@author: chauvet

Script python pour tester la reconnaissance d'objets
besoin de scikits image 0.6
"""

import pylab as m
from skimage import filters, color, morphology, measure, exposure
from skimage.feature import peak_local_max
from scipy import ndimage, flipud

try:
    import cv2
    opencv = True
except:
    opencv = False
    print('For best performance install opencv (sudo apt-get install python-opencv)')

#TODO: CLASS AVEC comme option nom image, ROI region of interest et scale
#doit sortir vecteur avec les tailles de grain

def GetGS(image_name, scale, roi=None, show=True,
          min_size=500, exclude_zones=None, flipudflag=False):

    #Load image (Rappel pour convertir couleur to rgb color.rgb2gray)
    if opencv:
        original = cv2.imread(image_name)
    else:
        original = m.imread(image_name)

    if flipudflag:
        original = flipud(original)


    #manage exclusion zone put them to 1 i.e. bottom
    if exclude_zones != None:
         #create markers of background and gravel
        markers_zones = m.zeros_like(original[:,:,0])

        for zone in exclude_zones:
            xa = min(zone[0],zone[2])
            xb = max(zone[0],zone[2])
            ya = min(zone[1],zone[3])
            yb = max(zone[1],zone[3])
            markers_zones[ya:yb,xa:xb] = 1

    if roi != None:
        #crop the image
        xa = min(roi[0],roi[2])
        xb = max(roi[0],roi[2])
        ya = min(roi[1],roi[3])
        yb = max(roi[1],roi[3])

        original = original[ya:yb,xa:xb]

        if exclude_zones != None:
            markers_zones = markers_zones[ya:yb,xa:xb]

    #transform to hsv
    if opencv:
        img = cv2.cvtColor(original, cv2.COLOR_BGR2HSV)
    else:
        img = color.rgb2hsv(original)

    #use s chanel
    img = img[:,:,1]

    #div by 255 si en couleur
    thre = img

    if show:
        m.figure()
        m.imshow(original)

    #test filtre sobel (avoir les pentes)
    if opencv:
        elev = cv2.Laplacian(thre, cv2.CV_64F)
    else:
        elev = filters.sobel(thre)


    #compute an auto threshold
    thresh = filters.threshold_otsu(thre)

    #create markers of background and gravel
    markers = m.zeros_like(thre)
    if show:
        print thresh

    markers[thre < thresh] = 2
    markers[thre > thresh] = 1

    if exclude_zones != None:
        markers[markers_zones == 1] = 1


    #use watershade transform (use markes as starting point)
    segmentation = morphology.watershed(elev, markers)


    #Clean small object
    if opencv:
        kernel = m.ones((2,2), m.uint8)
        closing = cv2.morphologyEx(segmentation-1, cv2.MORPH_CLOSE, kernel)
    else:
        closing = ndimage.binary_closing(segmentation-1)

    tmp = ndimage.binary_fill_holes(closing)
    label_objects, nb_labels = ndimage.label(tmp)

    sizes = m.bincount(label_objects.ravel())
    mask_sizes = sizes > min_size
    mask_sizes[0] = 0
    segmentation_cleaned = mask_sizes[label_objects]

    #relabel cleaned version of segmentation
    label_objects_clean, nb_label_clean = ndimage.label(segmentation_cleaned)

    #plot contour of object
    if show:
        m.contour(ndimage.binary_fill_holes(label_objects_clean), linewidths=1.2, colors='y')

    #trouve les informations des objets
    #old version of scikit properties=measurement_types
    mes = measure.regionprops(label_objects_clean)



    granulo = []
    for prop in mes:
        #Correct orientation ! car orientation prend pas en compte le cadrant !!!
        #: elements of the inertia tensor [a b; b c]
        Orientation = GetOrientation(prop['CentralMoments'])

        x0 = prop['Centroid'][1]
        y0 = prop['Centroid'][0]
        x1 = x0 + m.cos(Orientation) * 0.5 * prop['MajorAxisLength']
        y1 = y0 - m.sin(Orientation) * 0.5 * prop['MajorAxisLength']
        x2 = x0 - m.sin(Orientation) * 0.5 * prop['MinorAxisLength']
        y2 = y0 - m.cos(Orientation) * 0.5 * prop['MinorAxisLength']

        if show:
            m.plot((x0, x1), (y0, y1), '-r', linewidth=2.5)
            m.plot((x0, x2), (y0, y2), '-r', linewidth=2.5)

            m.plot(x0, y0, '.g', markersize=15)

        granulo.append(prop['MinorAxisLength']/scale)
    #    minr, minc, maxr, maxc = prop['BoundingBox']
    #    bx = (minc, maxc, maxc, minc, minc)
    #    by = (minr, minr, maxr, maxr, minr)[
    #    m.plot(bx, by, '-b', linewidth=2.5)


    return m.array(granulo), label_objects_clean, mes


#Function to get the proper orientation
def GetOrientation(CentralMoments):
    #Corrige le cadrant et permet d'avoir l'orientation de l'ellipse !
    mu = CentralMoments

    a = mu[2, 0] / mu[0, 0]
    b = mu[1, 1] / mu[0, 0]
    c = mu[0, 2] / mu[0, 0]

    if a - c == 0:
        Orientation = m.pi / 2.
    else:
        Orientation = - 0.5 * m.arctan2(2 * b, (a - c))


    return Orientation



if __name__ == "__main__":
    #Test de la fonction


    g1 = GetGS('../../IMG_7212.JPG',60.)


    m.show()
