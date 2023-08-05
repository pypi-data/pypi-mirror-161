#!/usr/bin/env python

# Import Modules
import numpy as np
import matplotlib.pyplot as plt

from astroquery.vizier import Vizier
from astropy import units as u
from astropy.io import fits
import plot_functions as pfunc

from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy.coordinates import Angle

import matplotlib as mpl
mpl.rcParams['axes.labelsize']   = 15
mpl.rcParams['legend.fontsize']  = 15
mpl.rcParams['xtick.major.size'] = 8
mpl.rcParams['xtick.minor.size'] = 4
mpl.rcParams['ytick.major.size'] = 8
mpl.rcParams['ytick.minor.size'] = 4
mpl.rcParams['xtick.labelsize']  = 15
mpl.rcParams['ytick.labelsize']  = 15

def catalog(image, catalog, r, starpix, cent, delta, limt, cmap, outima, label,
            scale, nameaxis, imasz) :
    '''
    Plot catalogue object on images

     Parameters
     ----------

     image : file or str,
         name of image (.fits)
     catalogue : file or str
         cataogue name
     r : float,
         radius in user unit
     starpix : file or str, default: none,
         print a file with coordinates in WCS (if the user want to)
     cent : array_like,
         [centx,centy], image center in pixels
     delta : array_like,
         [deltax,deltay], width (delta X) and height (delta Y) of the matrix
         figure.
     limt : array_lile,
         [zmin,zmax,0 or 1], minimum and maximum intensity levels to be
             displayed. Scale to be used (linear=0 or log=1)
     cmap : dict,
        ['colormap','0' or '1']  Color map
     outima :  file or str, default : none,
        name of the output file
     label : str-bool,
        1 to put a label in each object 0 to none
     scale : float,
         scale of image stick
     nameaxis : array,
         [xlabel, ylabel]
     *Color maps to use: autumn, bone, cool, copper, flag, gray, hot, hsv, jet,
                         pink, prism, spring, summer, winter and spectral.
     if you want an inversion of the color map, just use the '_r' sufix,
     e.g, gray_r
    '''
    image_ima = fits.open(image)
    w = WCS(image_ima[0].header)

    # option for daofind output
    if catalog[0]=='0':
        sx, sy = np.loadtxt(catalog[1], unpack=True,
                            usecols=(int(catalog[2])-1, int(catalog[3])-1))
        print ('\nNumber of the star found : %s \n'%(len(sx)))

        # print a file with coordinates in WCS (if the user wants to)
        if starpix != 'none' :
            ra, dec = w.all_pix2world(sx,sy,0)
            coorh2wcs = np.column_stack((ra, dec))
            np.savetxt(starpix, coorh2wcs, fmt='%3.12f')

    # option for a coordinate file in degrees or dd:mm:seg or hr:mm:seg
    if catalog[0]=='1':
        # Reading
        lma = np.loadtxt(catalog[1], dtype='str')
        ra  = lma[:, int(catalog[2]) - 1]
        dec = lma[:, int(catalog[3]) - 1]

        if ra[0].find(':') < 0:
            radec = SkyCoord(ra, dec, unit=u.deg)
            ra2d  = radec.ra.deg
            dec2d = radec.dec.deg
        else:
            radec = SkyCoord(ra, dec, unit=(u.hourangle, u.deg))
            ra2d  = radec.ra.deg
            dec2d = radec.dec.deg

        sx, sy = w.all_world2pix(ra2d, dec2d, 0)

        # Print a file with the coordinates in pixels
        if starpix != 'none' :
            lma[:,int(catalog[2])-1] = np.transpose(sx)
            lma[:,int(catalog[3])-1] = np.transpose(sy)
            np.savetxt(starpix, lma, '%s', delimiter='\t')

    # Option to retrieve the data from a given catalog
    if catalog[0]=='2':

        centima = w.all_pix2world(cent[0],cent[1], 0)
        print('\nCenter pix coordenates centx:{}  centy:{}'.format(cent[0],
                                                                 cent[1]))
        print('Center coordenates RA:{}  DEC:{}'.format(centima[0], centima[1]))

        coord_obj = SkyCoord.from_name(catalog[1])
        print ("Coordinates (RAC, DEC) of {} : ({}, {})".format(catalog[1],
               coord_obj.ra.degree,  coord_obj.dec.degree))

        viz = Vizier()
        viz.ROW_LIMIT = -1
        initab = viz.query_region(SkyCoord(ra=centima[0], dec=centima[1],
                                            unit=(u.deg, u.deg)),
                                  radius=Angle(float(catalog[3])/3600., "deg"),
                                  catalog=catalog[4])

        for table_name in initab.keys():
            print ('\n Vizier table name:, table_name')
            cattab = initab[table_name]
        headert='\t'.join(cattab.colnames)

        cattab_out =  cattab.to_pandas().to_numpy()
        np.savetxt(catalog[2], cattab_out, '%s', delimiter='\t', header=headert)

        print ('')
        nstars = len(cattab)
        print (len(cattab)," stars downloaded")
        print ('')
        print ("catalog fields:")
        print (cattab.colnames)

        sky = SkyCoord(cattab['RAJ2000'], cattab['DEJ2000'], unit='deg')
        sx, sy = w.world_to_pixel(sky)

        if starpix != 'none':
            cattab['RAJ2000'] = sx
            cattab['DEJ2000'] = sy
            cattab_out =  cattab.to_pandas().to_numpy()
            np.savetxt(starpix, cattab_out, '%s', delimiter='\t', header=headert)

    # Plot objects
    plt.clf()
    imasz = imasz.split(',')
    if imasz[0] == 'none':
        fig = plt.figure(1)
    else:
        fig = plt.figure(int(imasz[2]),figsize=(float(imasz[0]),
                         float(imasz[1])))
    AX = fig.add_subplot(1, 1, 1)




    for e in range(len(sx)):
        pfunc.circ ((sx[e]-cent[0])*scale,  (sy[e]-cent[1])*scale,
                    float(r[0])*scale, linef=r[1], linew=float(r[2]), AX=AX)
        # label the objects
        if label==1:
            plt.annotate(str(e+1), xy=((sx[e]-cent[0])*scale,
                        (sy[e]-cent[1])*scale), xycoords='data',
                         xytext=(float(r[3]),float(r[4])), textcoords='offset points',
                         arrowprops=dict(arrowstyle="->",color=r[1]))

    pfunc.figure(image, cent, delta, limt, cmap, scale, outima,
                     nameaxis=nameaxis, bbox='tight', AX=AX)

    plt.show()
