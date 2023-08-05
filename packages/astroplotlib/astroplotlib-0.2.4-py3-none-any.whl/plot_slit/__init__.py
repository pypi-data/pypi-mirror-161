#!/usr/bin/env python

##### Import Modules #####

#from __future__ import print_function
#from numpy import *
import numpy as np
#import pyfits                        
from astropy.io import fits
from astLib import astWCS
import matplotlib.pyplot as plt

import plot_functions as pfunc

import matplotlib as mpl
mpl.rcParams['axes.labelsize']= 15
mpl.rcParams['legend.fontsize']= 15
mpl.rcParams['xtick.major.size']= 16
mpl.rcParams['xtick.minor.size']= 8
mpl.rcParams['ytick.major.size']= 16
mpl.rcParams['ytick.minor.size']= 8
mpl.rcParams['xtick.labelsize']= 15
mpl.rcParams['ytick.labelsize']= 15


def coorfenda(slitsize, aper, ra, dec, th, ct_ap, scaper, scima, pnts, pntslab, 
              pntstxt, image, scale, cent, outima, calslit='on', vtmp=0, 
              maskaper='off', verbose='+'):

    '''
    Parameters
    -----------
    slitsize : array_like; [width (arc), heigth (arc), colour, linewidth] 
               or none
    aper   : array_like; [aperfile, colour, linewidth]
    ra     : array_like; [rac,0] or [y,1]
    dec    : array_like; [rac,0] or [y,1]
    th     : float; long-slit angle in counterclockwise relative axis (x+)	 
    ct_ap  : float; (center spectra bidimensional) 
    scaper : float; scale in arcsec for the 2D spectral image
    scima  : float; scale in arcsec for the image
    pnts   : array_like; apertures to label (e.g., [1,10,20]) or none
    pntslab : array_like; [x,y,color,0 or 1 to plot arrow] 
    pntstxt : array_line; apertures text (e.g., [2.2 kpc, 0.0 kpc, -2.2 kpc])
    image   : string;   image name (.fits)   
    scale   : array_line; [scale, unit]
    cent    : array_line; [ctx, cty]
    outfile : string; output file [mean,median,std,area,amin,amax,flux_tot]
    calslit : string; on or off to calculate aperture statitical
    
    Returns
    ---------
    fctx, fcty, ctx, cty ; slit and image centers in pixels
    '''
    # apertures file (col1 : center apertures, col2 : diameter apertures)
    apera = np.loadtxt(aper[0])
    mag   = (((apera[:,0]-ct_ap)*scaper)/scima)
      
    # long-slit center with wsc coordinates 
    if ra[1]==0.0:
        wcs = astWCS.WCS(image)
        pix = wcs.wcs2pix(ra[0], dec[0])
        fctx = pix[0]; fcty = pix[1]
        print ("center fenda (x,y):", pix[0], pix[1])
    
    # long-slit center with x,y coordinates 
    else:
        fctx = ra[0]
        fcty = dec[0]

    # x, y coordinates (in pixels) for the center of each aperture  
    pa = np.deg2rad(th) 
    rth = np.zeros([len(mag),2])
    rth[:,0] = fctx + mag*np.cos(pa)
    rth[:,1] = fcty + mag*np.sin(pa)
    
    # writing the file with x, y coordinates of each aperture (in pixels)
    if outima[0] != 'none' : 
        np.savetxt(outima[0], rth, fmt='%f', delimiter='  ')

    ## plot image ##

    plt.minorticks_on()

    # image center
    if cent[2]==0:
        wcs = astWCS.WCS(image)
        pix = wcs.wcs2pix(cent[0], cent[1])
        ctx = pix[0]; cty = pix[1]
    else:
        ctx = cent[0]; cty = cent[1] 
      
   
    # open the file to write the coordinates of all pixels in each aperture
    fskp = open('aper_xy.dat', 'w')

    # open the file to write the statistic of each aperture
    ficurve = open(outima[1],'w')
    ficurve.write("#     mean     median      sigma       area         min" + 
                  "        max     T_flux\n")
    
    # loading the grid of coordinates of the image
    ima_xy, ima_array = pfunc.callf(image) 

    # delta length of each aperture (in pixels)
    l_aper = (((apera[:,1])*scaper)/scima)*0.5
    
    # delta of width and length of the slite (in pixels)
    slit   = slitsize.split(',') 
    w_slit = (float(slit[0])/scima)*0.5
    l_slit = (float(slit[1])/scima)*0.5 

    # ploting each aperture
    for e in np.arange(len(rth[:,0])):
       
        # x, y coordinates for each aperture (it must be in image units)  
        pfunc.rect((rth[e,0]-ctx)*scale, (rth[e,1]-cty)*scale, w_slit*scale,
             l_aper[e]*scale,th-90, linef=aper[1], linew=float(aper[2]))

        # Calculating the statistic for each aperture (mean, median, etc.)
        if calslit == 'on': 
         
            # x, y coordinates for each aperture (it must be in pixels) 
            sk, skv, skp = pfunc.calcu(pfunc.rect(rth[e,0], rth[e,1], w_slit, 
                                            l_aper[e], th-90, plotr='no'), 
                                       ima_xy, ima_array, verbose=verbose) 
            # sk array: mean, median, sigma, area, min, max, T_flux
            ficurve.write(('{:>10.3g} {:>10.3g} {:>10.3g} {:>10g}  {:>10.3g}' + 
                            ' {:>10.3g} {:>10.3g} \n').format(*np.array(sk)))
            if maskaper == 'on':           
                regmask = pfunc.maskpoly(pfunc.rect(rth[e,0], rth[e,1], w_slit, 
                                              l_aper[e], th-90, plotr='no'), 
                                         ima_xy, ima_array*nan)
                fits.writeto('mask_' + str(vtmp) + '.fits', regmask, 
                             overwrite=True)
            for skxy in skp:
                fskp.write('{:>2d} {:>6.1f} {:>6.1f}\n'.format(vtmp, *skxy))
            vtmp += 1
    
    fskp.close()
    ficurve.close() 

    # plot slit
    if slitsize!='none':
        slitsize=slitsize.split(',')   
        pfunc.rect((fctx-ctx)*scale,(fcty-cty)*scale,w_slit*scale,l_slit*scale,
             th-90,linef=slitsize[2],linew=float(slitsize[3]))
          
    # label apertures
    if pnts != 'none':
        pnts=[float(s) for s in pnts.split(',')]
        pntstxt='  '.join(pntstxt.split('#')[0].split()).split(',')
        pntslab=pntslab.split(',')
        xt=int(pntslab[0]);yt=int(pntslab[1])
        for i, e in enumerate(pnts):
        
            # no arrow
            if pntslab[3]=='0':          
                plt.annotate(pntstxt[i],xy=((rth[e-1,0]-ctx)*scale,
                         (rth[e-1,1]-cty)*scale), xycoords='data', 
                         xytext=(xt,yt), textcoords='offset points', 
                         color=pntslab[2], size='xx-large')
            else:
                plt.annotate(pntstxt[i],xy=((rth[e-1,0]-ctx)*scale, 
                         (rth[e-1,1]-cty)*scale), xycoords='data', 
                         xytext=(xt,yt), textcoords='offset points', 
                         color=pntslab[2], 
                         arrowprops=dict(arrowstyle="->",fc=pntslab[4],
                         linewidth=int(pntslab[5])))
       
    return fctx, fcty, ctx, cty                
