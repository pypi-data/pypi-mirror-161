#!/usr/bin/env python

import os
import matplotlib.pyplot as plt
import matplotlib as mpl

import numpy as np
from scipy.ndimage import filters

from pyraf import iraf
from astropy.table import Table
from astropy.io import fits

import plot_functions as pfunc

def plot_graf(fig, subplot1, vect, parmx, parmy, rads, rads2, scale,
              task, taskerr, cora1='b.', corp1='r.', labely=0, labelx=0,
              sticky=0, stickx=0, hspace1=0, wspace1=0,gridc='black'):

    labels = {'SMA':'$Semi-major\,axis$',
              'INTENS':'$Intens$', 'ELLIP':'$\\epsilon$',
              'PA':'$Position\,Angle\,(degree)$', 'RSMA':'$R^{1/4}$',
              'MAG':'$mag$', 'TFLUX_E':'$Total\,Flux\,inside\,ellipse$',
              'TFLUX_C':'$Total\,flux\,inside\,circle$',
              'TMAG_E':'$Total\,mag\,inside\,ellipse$',
              'TMAG_C':'$Total\,mag\,inside\,circle$',
              'NPIX_E':'$Total\,pixels\,inside\,ellipse$',
              'NPIX_C':'$Total\,pixels\,inside\,circle$',
              'A4':'$A4$', 'B4':'$B4$', 'MAG2':'$mag/arcsec^{2}$',
              'R_eq_E':'$R_{eq}\,of\,ellipse$',
              'R_eq_E_ARC':'$R_{eq}\,of\,ellipse$',
              'TFLUX_T':'$Total\,flux\,inside\,R_{eq}$',
              'TMAG_T':'$Total\,mag\,inside\,R_{eq}$',
              'NPIX_T':'$Total\,pixels\,inside\,R_{eq}$',
              'R_eq_T':'$R_{eq}$','R_eq_T_ARC':'$R_{eq}$',
              'SMA_ARC':'Semi-major axis','SMA_LOG':'$\\log(sma)$'}

    # is there error bar?
    try:
        taskerr[parmy]
        kopen='1'
    except:
        kopen='0'

    mpl.rcParams['grid.color']  = gridc

    ax = fig.add_subplot(subplot1[0],subplot1[1],subplot1[2])

    if hspace1 != '0':
        plt.subplots_adjust(hspace=float(hspace1))
    if wspace1 != '0':
        plt.subplots_adjust(wspace=float(wspace1))

    ax.minorticks_on()

    if parmx == 'RSMA':
        scale = scale**(0.25)

    if kopen=='1':
        ax.errorbar(vect[rads2[0]:rads2[1] + 1:rads2[2], task[parmx]]*scale,
                    vect[rads2[0]:rads2[1] + 1:rads2[2],task[parmy]],
                    yerr=vect[rads2[0]:rads2[1] + 1:rads2[2],
                    task[taskerr[parmy]]], fmt=corp1, ecolor='k')
        ax.errorbar(vect[rads[0]:rads[1] + 1:rads[2], task[parmx]]*scale,
                    vect[rads[0]:rads[1] + 1:rads[2],task[parmy]],
                    yerr=vect[rads[0]:rads[1] + 1:rads[2],
                    task[taskerr[parmy]]], fmt=cora1, ecolor='k')

    else:
        ax.plot(vect[rads2[0]:rads2[1] + 1:rads2[2],task[parmx]]*scale,
                vect[rads2[0]:rads2[1] + 1:rads2[2],task[parmy]],corp1)

        ax.plot(vect[rads[0]:rads[1] + 1:rads[2],task[parmx]]*scale,
                vect[rads[0]:rads[1] + 1:rads[2],task[parmy]], cora1)

    if parmy.find('MAG') != -1 and (vect[0,task[parmy]]<vect[1,task[parmy]]):
        plt.ylim(plt.ylim()[::-1])

    ax.grid(True)
    if labely != 0:
        plt.ylabel(r'%s'%(labels[parmy]))
    if labelx != 0:
        plt.xlabel(r'%s'%(labels[parmx]))

    if sticky == 0:
        plt.setp( ax.get_yticklabels(), visible=False)
    if stickx == 0:
        plt.setp( ax.get_xticklabels(), visible=False)



def ellip(image, table, rad, cora, rad2, corp, cent, delta, limt, cmap, elicon,
          subp, parm, figs, outima, magzp, pixscale, sky, ref, nameaxis,
          szcent=[10, 1], azi_prof=['off', 2, 'INDEF', 'INDEF'], ima_fig='on',
          plot_par='on', cent_ref=[0, 0, 0, 0], rad_cent='no',
          rad_user='range', cbaropt=0, cbar=['vertical', 1.0, 0.0, '%.1f'],
          cbarl=None, barinvt='no',nivelconts_mag='no', flipaxes=[1, 1],
          AX1=None):

    """
    This function plots the ellipses (and its contours) and the
    parameters (e.g., PA, ellipticity, etc.) fitted with the IRAF task ellipse.

    Parameters
    ----------

    image : Image to be plotted.
    table : Output table from IRAF ellipse task in STSDAS format.
    rad   : Range in pixels of the ellipses to be plotted [radmin, radmax, step]
    cora  : Color and symbol of 'rad' points ('g.')
    rad2  : Total range to be plotted of the ellipse parameters
            [radmin, radmax, step]
    corp  : Color and symbol of 'rad2' points ('k.')
    cent  : Center of the image in pixels  [x,y]
    delta : Delta of the image in pixels [dx,dy]
    limt  : Minimun and maximum image intesity to be mapped and intensity scale
            (normal=0, log=1) [z1, z2, 0 or 1]
    cmap  : Color map and invertion of the color map (normal='0',
            invertion='1'), ['colormap','0' or '1']
    elicon: Color ellipses, color countours, sigma smoothness,
            0 no grid or 1 grid, colors and symbols of the ellipes center ('k-'),
            colors and symbols of the photometric center of the galaxy.
    subp  : grid of the subplots for the fitted parameters [nrows, ncolumns]
    parm  : Parameters to be plotted [SMA or RSMA or R_eq, MAG, PA], e.g.,
            (['SMA','MAG','1','1','1','1','0.3','0',
              'SMA','PA','1','1','1','1','0','0'])
    figs  : Width, height in inches of the figures of galaxy image and
            fitter parameters [10, 10, 10, 10]
    outima: Outputs [table (none), image (none), parameters (none) ]"
    magzp : Magnitude of the point zero
    pixscale : Pixels scale in arcsec
    sky   : Sky background value
    ref   : Exposition time of the image.
    units : Factor of the scale for the pixels (e.g, 0.5 (arcsec/pix) or
            0.001(kpc/pix)) , unit scale
    szcent : Size of symbol  and edge of the marker of ellipse centers
    azi_prof : Plot azimuthal profiles of the iso-contours of fitted ellipses
              ['off' or 'on', offset between profiles,'ymin','ymax']
    ima_fig : Activate the figure of the image and fitted ellipse, 'on' or 'off'
    plot_par : Activate the figure of fitted parameters, 'on' or 'off'
    cent_ref : In case that the ellipse were fitted in another Image is
               necessary to transform their coordinates into the coordinate
               system of the current image. To do so, It is necessary to provide
               the previous Image center (cent_ref[0], cent_ref[1]) and its
               respectives coordinates into the current image (cent_ref[2],
               cent_ref[3]). [0, 0, 0, 0]
    rad_cent: 'yes'/'no' to plot the photometric center
    rad_user: 'range' when it's provided  a initial_rad, a final_rad and a step.
              'user' when instead the user provided a list of radii.
    cbaropt: by default (0),  without bar
             We have another three optiond to plot the color bar:
             (1) Traditional one
             (2) One that "dealing colorbar size with all types of axes is",
                 source:
                 https://stackoverflow.com/questions/18195758/ \
                       set-matplotlib-colorbar-size-to-match-graph
             (3) Sugested by http://joseph-long.com/writing/colorbars/
    cbar   : In case to be chosen any of the previous options to plot the color
             bar ([orientation='vertical' or 'horizotal',shrink=1.0,
                   pad=0.0,format='%.2f'])
                 shrink: fraction by which to shrink the colorbar
                 pad   : fraction of axes between colorbar and new image axes
    cbarl  : bar label
    nivelconts_mag: 'yes'/'no' to convert the iso-contour into magnitudes.
    AX1: Image object or None
    """
    task = {'SMA':0, 'INTENS':1, 'INT_ERR':2, 'PIX_VAR':3,'RMS':4, 'ELLIP':5,
            'ELLIP_ERR':6, 'PA':7, 'PA_ERR':8, 'X0':9, 'X0_ERR':10, 'Y0':11,
            'Y0_ERR':12,'GRAD':13, 'GRAD_ERR':14,'GRAD_R_ERR':15,'RSMA':16,
            'MAG':17, 'MAG_LERR':18, 'MAG_UERR':19, 'TFLUX_E':20, 'TFLUX_C':21,
            'TMAG_E':22,'TMAG_C':23,'NPIX_E':24, 'NPIX_C':25,
            'A3':26,'A3_ERR':27, 'B3':28, 'B3_ERR':29, 'A4':30, 'A4_ERR':31,
            'B4':32, 'B4_ERR':33, 'NDATA':34,'NFLAG':35,
            'NITER':36, 'STOP':37, 'A_BIG':38, 'SAREA':39, 'R_eq_E':40,
            'R_eq_E_ARC': 41, 'SMA_ARC':42, 'SMA_LOG':43}

    taskerr = {'INTENS':'INT_ERR', 'ELLIP':'ELLIP_ERR', 'PA':'PA_ERR',
               'X0':'X0_ERR','Y0':'Y0_ERR','GRAD':'GRAD_ERR','MAG':'MAG_LERR',
              'A3':'A3_ERR','B3':'B3_ERR','A4':'A4_ERR','B4':'B4_ERR'}

    colors = {'b':'blue', 'g':'green', 'r':'red', 'c':'cyan', 'm':'magenta',
              'y':'yellow','k':'black','w':'white'}

    ### GRIDS
    #grid.color       :   black   # grid color
    #grid.linestyle   :   :       # dotted
    #grid.linewidth   :   0.5     # in points
    if elicon[0] != 'none' : mpl.rcParams['grid.color']  = colors[elicon[0]]
    mpl.rcParams['grid.linewidth'] =  1     # in points

    #####################
    #### iraf script ####

    tnames = iraf.tlcol(table, Stdout=1)
    tnames=[e.split(' ')[0] for e in tnames[1::]]

    if outima[0] == 'none':
        tabletmp = 'temp.dat'
    else:
        if os.path.exists(outima[0]):
            os.remove(outima[0])
        tabletmp = outima[0]

    iraf.tdump(table, datafil=tabletmp, columns=" ", Stdout=1)

    tab = Table.read(tabletmp, format='ascii')

    tableout = Table(tab, names=tnames)

    area = 2.5*(np.log10(pixscale**2))
    INTENS = tableout['INTENS']
    tableout['MAG'] = -2.5*np.log10((INTENS-sky)/ref) + magzp + area

    TFLUX_E = tableout['TFLUX_E']
    NPIX_E = tableout['NPIX_E']
    tableout['TMAG_E'] = -2.5*np.log10((TFLUX_E-NPIX_E*sky)/ref) + magzp

    TFLUX_C = tableout['TFLUX_C']
    NPIX_C = tableout['NPIX_C']
    tableout['TMAG_C'] = -2.5*np.log10((TFLUX_C-NPIX_C*sky)/ref) + magzp

    tableout.add_column(np.sqrt(NPIX_E/np.pi), name = 'R_eq_E')
    tableout.add_column(np.sqrt(NPIX_E/np.pi)*pixscale, name = 'R_eq_E_ARC')

    SMA = tableout['SMA']
    tableout.add_column(SMA*pixscale, name = 'SMA_ARC')
    tableout.add_column(np.log10(SMA*pixscale), name = 'SMA_LOG')

    # Saving as an ascii table the Stsdas output table from ellipse task.
    # In addition to the default columns, we have added R_eq_E, R_eq_E_ARC,
    # SMA_ARC, and SMA_LOG.
    tableout.write(tabletmp, format='ascii.commented_header', overwrite=True)
    os.system("sed -i \"s/INDEF/nan/g\" {}".format(tabletmp))

    ##############################################################
    #### Loading ascii output table from ellipse and the image ###
    vect=np.loadtxt(tabletmp)
    ima    = fits.open(image)[0].data

    # if it's provied  the rad_initial, rad_final, and step.
    if rad_user == 'range':
        rad[0] = np.where(vect[:,task['SMA']]>=rad[0])[0][0]
        rad[1] = np.where(vect[:,task['SMA']]<=rad[1])[0][-1]

        len_SMA = len(vect[:,task['SMA']])
        print ("Len of SMA array:", len_SMA)

        if rad[1] + rad[2] < len_SMA:
            rad_array = np.arange(rad[0], rad[1] + rad[2], rad[2])
        else:
            rad_array = np.arange(rad[0], len_SMA, rad[2])

    # This option is when it's provied  custommed radii instead.
    else:
        rad_array = np.array(rad)

    print ("Radius (position in the array) of fitted ellipses", rad_array[::-1])

    # Definition of arrays
    elip   = np.take(vect[:,task['ELLIP']], rad_array)
    pa     = np.take(vect[:,task['PA']], rad_array)
    radmaj = np.take(vect[:,task['SMA']], rad_array)
    X0     = np.take(vect[:,task['X0']], rad_array)
    Y0     = np.take(vect[:,task['Y0']], rad_array)
    nivelconts = np.take(vect[:,task['INTENS']], rad_array)
    if nivelconts_mag == 'yes':
        nivelconts = -2.5*np.log10((nivelconts-sky)/(ref*pixscale)) + magzp

    # Creating the figure which contain the galaxy image and the fitted ellipses
    if AX1 is None:
        fig1 = plt.figure(1,figsize=(figs[0],figs[1]))
        AX1 = fig1.add_subplot(1, 1, 1)
        AX1.minorticks_on()

    # Creating the figure which contain the azimuthal profiles of the fitted
    # ellipses
    if azi_prof[0] != 'off':
        fig3 = plt.figure(3)
        AX3 = fig3.add_subplot(1, 1, 1)
        AX3.minorticks_on()
        print('information about ellipse-contour azimuthal profile:')
        print('semi-minor axis,  semi-major axis, PA')

    ########################################################################
    #### plotting the fitted ellipses and their respective iso-contours ####
    i = 0
    for angle in pa:
        '''
        For initial setup of the ellipse is chosen that the semi-major axis is
        aligned with positive 'Y' axis, while the semi-minor axis is aligned
        with positve 'X' axis. The PA increases counterclockwise.

        The dataset of ellipse start conunterclockwise from (-y,0), after
        follows  (0,+x), (+y,0), (-x,0) up to again (-y,0).
        '''

        # Semi-minor axis
        semix = radmaj[i]*(1-elip[i])
        # Semi-major axis
        semiy = radmaj[i]

        if azi_prof[0] != 'off':
            print(np.round(semix,2), np.round(semiy,2), round(angle,2))

        # array [-semiy, -semiy+step,..., semiy-step,semiy]
        y1 = np.linspace(-semiy,semiy,400)
        # Repeat the start point to close the ellipse when it is drawn
        semiy1 = np.array([semiy])
        y1 = np.concatenate((y1,semiy1))
        # Ellipse as function of semimajor axis
        x1 = ((1-(y1**2/semiy**2))*(semix**2))**0.5

        # Now, creating the semi-ellipse remaining: [semiy,...,0,...,-semiy]
        # [0,...,-X,...,0]
        invy1 = y1[::-1]
        x2 = x1*-1.0
        x = np.concatenate((x1,x2))
        y = np.concatenate((y1,invy1))

        # Ellipse PA
        alpha = (angle/180.0)*np.pi

        # Matrix of Transformation
        xp = x*np.cos(alpha) - y*np.sin(alpha)
        yp = x*np.sin(alpha) + y*np.cos(alpha)

        # Ellipse center
        x0 = X0[i]-1
        y0 = Y0[i]-1


        # Center of reference of the galaxy image.
        if cent[0]==0 and cent[1]==0:
            cent_refx = ima.shape[1]
            cent_refy = ima.shape[0]
        else:
            cent_refx = cent[0]
            cent_refy = cent[1]

        # In case that the ellipse were fitted in another Image is necessary
        # to transform their coordinates into the coordinate system of the
        # current image. To do so, It is necessary to provide the previous Image
        # center (cent_ref[0], cent_ref[1]) and its  respectives coordinates
        # into the current image (cent_ref[2], cent_ref[3]).

        if cent_ref[0]!=0 and cent_ref[1]!=0:
            cent_ellipx = -cent_ref[0] + cent_ref[2]
            cent_ellipy = -cent_ref[1] + cent_ref[3]
        else:
            cent_ellipx = 0
            cent_ellipy = 0

        cx = ((x0 - cent_refx + cent_ellipx)*pixscale)*flipaxes[0]
        cy = ((y0 - cent_refy + cent_ellipy)*pixscale)*flipaxes[1]
        xp = xp*pixscale*flipaxes[0] + cx
        yp = yp*pixscale + cy

        # Plot ellipse center
        AX1.plot(cx, cy, elicon[4], markersize=szcent[0], mew=szcent[1])
        # Plotting  ellipse
        AX1.plot(xp, yp, elicon[0], markersize=2)
        i=i+1

        # plot azimuthal profile of the ellipse-contour
        if azi_prof[0] != 'off':
            step = 360./len(xp)
            offset = azi_prof[1]
            k = 1
            colorpa = (['k.','r.','b.','g.','k.'])
            for  xima, yima in zip(xp,yp):
                AX3.plot(k*step, ima[int(yima+y0+1.5),int(xima+x0+1.5)] +
                         offset*i, colorpa[i])
                ima[int(yima+y0+1.5), int(xima+x0+1.5)] = np.nan
                k+=1
            AX3.set_xlabel('Degrees')
            AX3.set_ylabel('Intensity')

    # plot of the photometric center of the galaxy
    if rad_cent != 'no':

        X0     = np.take(vect[:,task['X0']], rad_cent)
        Y0     = np.take(vect[:,task['Y0']], rad_cent)
        # Ellipse center
        x0 = X0-1
        y0 = Y0-1
        cx = ((x0 - cent_refx + cent_ellipx)*pixscale)*flipaxes[0]
        cy = ((y0 - cent_refy + cent_ellipy)*pixscale)*flipaxes[1]

        AX1.plot(cx, cy, elicon[5], markersize=szcent[0]*2,
                         mew=szcent[1])
    # off/on of grids
    if elicon[3] == '0':
        elicon[3]='off'
    else:
        elicon[3]='on'
    # plot the galaxy image
    if ima_fig == 'on':
        pfunc.figure(ima, cent, delta, limt, cmap, pixscale, outima[1],
                     pgrid=[elicon[3], elicon[0]], bbox='tight', cont=elicon[1],
                     nivels=np.sort(nivelconts), sigmag=float(elicon[2]),
                     contc=elicon[1], AX=AX1, nameaxis=nameaxis,
                     cbaropt=cbaropt, barinvt=barinvt, cbar=cbar, cbarl=cbarl,
                     flipaxes=flipaxes)

    #######################################
    #### plot of the fitted parameters ####
    if plot_par == 'on':
        fig2 = plt.figure(2, figsize=(figs[2], figs[3]))
        nsub = subp[0]*subp[1]

        rad2[0] = np.where(vect[:,task['SMA']]>=rad2[0])[0][0]
        rad2[1] = np.where(vect[:,task['SMA']]<=rad2[1])[0][-1]

        for i in range(nsub):
            plot_graf(fig2, (subp[0],subp[1],i+1), vect, parm[i*8], parm[i*8+1],
                      rads=[rad[0],rad[1],rad[2]], rads2=[rad2[0], rad2[1],
                      rad2[2]],
                      scale=pixscale, task=task, taskerr=taskerr,
                      cora1=cora, corp1=corp, labely=int(parm[i*8+2]),
                      labelx=int(parm[i*8+3]), sticky=int(parm[i*8+4]),
                      stickx=int(parm[i*8+5]), hspace1=parm[i*8+6],
                      wspace1=parm[i*8+7], gridc='black')

        if outima[-1] != 'none' :
            plt.savefig(outima[2], format=outima[2].split('.')[-1],
                        bbox_inches='tight')

    #####################################################
    #### plot the azimuthal profiles of iso-contours ####
    if azi_prof[0] != 'off':
        print ("the offset between the azimuthal profile curves is:", offset)
        if azi_prof[2] == 'INDEF':
            miny = np.min(nivelconts) - azi_prof[1]
        else:
            miny = azi_prof[2]
        if azi_prof[3] == 'INDEF':
            maxy = np.max(nivelconts) + azi_prof[1]
        else:
            maxy = azi_prof[3]
        AX3.set_ylim(miny, maxy)
