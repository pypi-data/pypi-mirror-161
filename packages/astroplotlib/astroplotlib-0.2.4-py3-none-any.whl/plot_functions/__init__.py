import numpy as np
import matplotlib
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.colors import *
from astropy.io import fits
from astropy.convolution import convolve
from astropy.convolution import Gaussian2DKernel
from scipy.ndimage import filters
import matplotlib.colors as colors
import os, sys

#matplotlib.rcParams['ps.useafm'] = True
#matplotlib.rcParams['pdf.use14corefonts'] = True
#matplotlib.rcParams['text.usetex'] = True


# new color map
mapb_rgb = { 'red'   : ((0.0, 0.0, 0.0),
                       (0.25, 0.0, 0.0),
                       (0.5, 1.0, 1.0),
                       (1.0, 1.0, 1.0)),

             'green' : ((0.0, 0.0, 0.0),
                       (0.5, 0.0, 0.0),
                       (0.75, 1.0, 1.0),
                       (1.0, 1.0, 1.0)),

             'blue'  : ((0.0, 0.0, 0.0),
                       (0.25, 1.0, 1.0),
                       (0.5, 0.0, 0.0),
                       (0.75, 0.0, 0.0),
                       (1.0, 1.0, 1.0)),
            }

#RED:
#(0,0)(0.25,0)(0.5,1)(1,1)
#GREEN:
#(0,0)(0.5,0)(0.75,1)(1,1)
#BLUE:
#(0,0)(0.25,1)(0.5,0)(0.75,0)(1,1)

mapb = LinearSegmentedColormap('b',mapb_rgb)
plt.register_cmap(cmap=mapb)

def ellipse (x0, y0, sma, eps, pa, step=400,
             linef='k-', linew=4, plotr='no', AX=None):
        '''
        For initial setup of the ellipse is chosen that the semi-major axis is
        aligned with positive 'Y' axis, while the semi-minor axis is aligned
        with positve 'X' axis. The PA increases counterclockwise.

        The dataset of ellipse start conunterclockwise from (-y,0), after
        follows  (0,+x), (+y,0), (-x,0) up to again (-y,0).
        '''
        # Semi-minor axis
        a = sma*(1-eps)
        # Semi-major axis
        b = sma

        # angular array
        th = np.deg2rad(np.linspace(0, 360, step))

        # radis array
        rad = np.sqrt(np.square(a*b)/(np.square(b*np.cos(th)) +
                                      np.square(a*np.sin(th))))

        x = rad*np.cos(th)
        y = rad*np.sin(th)

        # Ellipse PA
        alpha = np.deg2rad(pa)

        # Matrix of Transformation
        xp = x*np.cos(alpha) - y*np.sin(alpha)
        yp = x*np.sin(alpha) + y*np.cos(alpha)

        # Matrix of translation
        xp = xp + x0
        yp = yp + y0

        if plotr == 'yes':
            if AX is not None:
                AX.plot(xp, yp, linef, lw=linew)
            else:
                plt.plot(xp, yp, linef, lw=linew)

        return np.column_stack((xp, yp))

def circ(cx, cy, rad, l=50, linef='k-', linew=4, plotr='yes', AX=None):
    """
    Plot a circle.

    Parameters
    ----------
    cx : coordinates x in pix of the center
    cy : coordinates y in pix of the center
    rad : radius of circle
    h  : 0.5*height in pix
    l  : points in line
    lifef : type of the lines and color
    linew : width line

    Return
    -------
    A 2d array with the x, y coordinates of the rectangle

    """

    theta = np.linspace(0.0, 2*np.pi, l)
    xc = cx + rad*np.cos(theta)
    yc = cy + rad*np.sin(theta)

    if plotr == 'yes':
        if AX is not None:
            AX.plot(xc, yc, linef, lw=linew)
        else:
            plt.plot(xc, yc, linef, lw=linew)


    return np.column_stack((xc, yc))


def rect(cx, cy, w, h, a, l=20, linef='k-', linew=4, plotr='yes', AX=None):
    """
    Plot a rectangle.

    Parameters
    ----------
    cx : coordinates x in pix of the center
    cy : coordinates y in pix of the center
    w  : 0.5*width in pix
    h  : 0.5*height in pix
    a  : Angle the rotation in counterclockwise relative to the vertical axis
         (degree)
    l  : points in line
    lifef : type of the lines and color
    linew : width line

    Return
    -------
    A 2d array with the x, y coordinates of the rectangle

    """
    a = np.deg2rad(a)

    pt1 = np.column_stack((np.linspace(cx-w,cx+w,l), np.zeros([l,1])+cy-h))
    pt2 = np.column_stack((np.zeros([l,1])+cx+w, np.linspace(cy-h,cy+h,l)))
    pt3 = np.flipud(np.column_stack((np.linspace(cx-w, cx+w,l),
                    np.zeros([l,1])+cy+h)))
    pt4 = np.flipud(np.column_stack((np.zeros([l,1])+cx-w,
                 np.linspace(cy-h,cy+h,l))))

    r1,r2 = np.hsplit(np.vstack((pt1,pt2,pt3,pt4)),2)
    rx = r1-cx
    ry = r2-cy
    r1p = cx+rx*np.cos(a)-ry*np.sin(a)
    r2p = cy+rx*np.sin(a)+ry*np.cos(a)

    if plotr == 'yes':
        if AX is not None:
            AX.plot(r1p, r2p, linef, lw=linew)
        else:
            plt.plot(r1p, r2p, linef, lw=linew)

    return np.hstack((r1p, r2p))


def image_orientation(image, ext=0):
    """
    This routine show the orientation of North and East axis with respect to
    +X-axis in counterclockwise. In addition displays the pixel scale of the
    image.
    """
    try:
        hdr=fits.open(image)[ext].header

    except Exception as err:
        raise AttributeError("The image doesn't exit or its path is wrong",
                             err)

    try:
        cd1 = hdr['CD1_1']
    except Exception as err:
        raise AttributeError("header keywords CD1_1, CD2_2, ... doesn't"
                          "exit", err)

    cd2 = hdr['CD1_2']
    cd3 = hdr['CD2_1']
    cd4 = hdr['CD2_2']

    agn = np.rad2deg(np.arctan2(cd3,cd1))
    age = np.rad2deg(np.arctan2(cd2,cd4))

    if abs(agn + age) < 182.0 and abs(agn+age) > 178.0:
        age = age*-1.0
        if age < 0.0: age+=360
        thn = np.deg2rad(age+90)
        the = np.deg2rad(age+180)

    elif agn+age<2.0 and agn+age>-2:
        agn = agn*-1
        if agn < 0.0:
            agn+=360
        thn = np.deg2rad(agn+90)
        the = np.deg2rad(agn)


    print (('PA of N and E axes with respect x+ axis measured in ' +
            'counter-closewise direction {:.1f} {:.1f}').format(
            np.fmod(np.rad2deg(thn), 360), np.fmod(np.rad2deg(the), 360)))

    scale = cd1/np.cos(np.deg2rad(agn))

    print('scale arcsec/pixel of the image:', scale*3600)


    return (np.fmod(np.rad2deg(thn), 360), np.fmod(np.rad2deg(the), 360),
            scale*3600)

def image_north_orientation(in_ima, out_ima, north_ang,flip='no',
                            ang_ref_north=90):
    """
    This routine aligns the image to standard convention in astronomy; axis
    North aligns to +Y-axis, while East axis aligns to -X-axis.
    """
    from pyraf import iraf
    PAima = (north_ang - ang_ref_north)*-1
    iraf.imlintran.unlearn()
    iraf.imlintran(input=in_ima, output='temp.fits', xrotation=PAima,
               yrotation=PAima, xmag=1.0, ymag=1.0)

    if flip != 'no':
        # Flipping the image
        iraf.imlintran.unlearn()
        iraf.imlintran(input='temp.fits', output=out_ima, xrotation=180.0,
                       yrotation=0.0, xmag=1.0, ymag=1.0)
    else:
        os.system("mv temp.fits {}".format(out_ima))


    os.system("rm temp.fits")


def zetas(image, delta, scale, parr='3', larrow=5.0, nx=2.0, ny=2.0, lhat=1.16,
          postxtn=1.5, postxte=1.5, carr='k', ctex='k', stex=15, linew=2,
          AX=None):
    """
    Plotting the North and East arrows in a given image.

    Parameters
    ----------

    image : str or array,
        Image name or a array with the North and East axis angles in degrees
        [North-angle, East-Angle] counter wiseclock from positive x-axis.
    delta : array,
        Delta (x,y) of the image.
    scale : float,
        image scale.
    parr : str,
        Location of the arrows, '1' left-bottom, '2' right-bottom,
        '3' right-top, '4' left-top.
    larrow : float,
        Length of the arrow would be a fraction of the minor betwwen x
        and y axes as follow: (dx*scale/larrow.)
    nx : float,
        Margin of the arrow in x-axis is proportional to larrow: nx*larrow.
    ny : float,
        Margin of the arrow in x-axis is proportional to larrow: nx*larrow.
    lhat : float,
        Size of arrow hat is proportional to larrow: larrow*(lhat-1.)
    postxtn : float,
        The position of 'N'  text is proportional to larrow: larrow*postxtn.
    postxte : float,
        The position of 'E'  text is proportional to larrow: larrow*postxtn.
    AX : object,
        Image object or None.
    """

    if type(image) is str:
        data_ima = image_orientation(image)
        thn = data_ima[0]
        the = data_ima[1]
    else:
        try:
            thn = np.deg2rad(image[0])
            the = np.deg2rad(image[1])
        except Exception as err:
            raise AttributeError("It is expected a array as  " +
                                 "[North-angle, East-Angle]", err)

    print (('PA N and E axis with respect x+ axis in ' +
           'counter-closewise {:.1f} {:.1f}').format(
                                              np.fmod(np.rad2deg(thn), 360),
                                              np.fmod(np.rad2deg(the), 360)))

    x=delta[0]*scale
    y=delta[1]*scale

    larr=np.min(delta)*scale/larrow     # arrow length


    posx=larr*np.cos(thn)                # components x north axis
    posy=larr*np.sin(thn)                # components y north axis

    posxe=larr*np.cos(the)               # components x east axis
    posye=larr*np.sin(the)               # components y east axis

    posxt=larr*np.cos(thn)*postxtn       # components x north axis arrow
    posyt=larr*np.sin(thn)*postxtn       # components y north axis arrow

    posxte=larr*np.cos(the)*postxte      # components x east axis arrow
    posyte=larr*np.sin(the)*postxte      # components y east axis arrow

    lhat=larr*(lhat-1.)               # hat legth

    lodir={'1':([nx*larr,ny*larr]), '2':([2*delta[0]*scale-nx*larr,ny*larr]),
           '3':([2*delta[0]*scale-nx*larr,2*delta[1]*scale-ny*larr]),
           '4':([nx*larr,2*delta[1]*scale-ny*larr])}

    if AX is None:
        AX = plt
    AX.arrow(lodir[parr][0]-x, lodir[parr][1]-y, posx, posy, color=carr,
             lw=linew, head_width=lhat, head_length = lhat)
    AX.text(lodir[parr][0]-x+ posxt,  lodir[parr][1]-y + posyt, 'N',
            horizontalalignment='center', color=ctex, fontsize=stex)
    AX.arrow(lodir[parr][0]-x, lodir[parr][1] -y, posxe, posye, color=carr,
             lw=linew, head_width=lhat, head_length = lhat)
    AX.text(lodir[parr][0] -x+posxte, lodir[parr][1]-y + posyte,'E',
            horizontalalignment='center', color=ctex, fontsize=stex)


def bar(delta, scale, barl, bartex, bartexs='medium', parr='1', larrow=5.0,
        nx=1.0, ny=1.0, postxt=1.2, cbar='k-', ctex='k', linew=2, AX=None):

    """
    Plot a scale bar

    Parameters
    ----------

    delta  : delta (x,y) of the image
    scale  : scale of the image
    barl   : leght of the bar in image scale (e.g in arcsec)
    bartex : text above of the bar
    parr   : location of the scale bar, '1' left-bottom,  '2' right-bottom,
             '3' right-top, '4' left-top
    larrow : length of the margin, proportion to minor delta between x and y,
             (dx*scale/larrow)
    nx     : margin in x, proportion to larrow, nx*larrow
    ny     : margin in y, proportion to larrow, nx*larrow
    postxt : separtion of the text , proportion  to larrow, larrow*postxt
    AX : object,
        Image object or None.
    """
    x=delta[0]*scale
    y=delta[1]*scale

    larr=np.min(delta)*scale/larrow

    lodir={'1':([nx*larr,ny*larr]), '2':([2*delta[0]*scale-nx*larr,ny*larr]),
           '3':([2*delta[0]*scale-nx*larr,2*delta[1]*scale-ny*larr]),
           '4':([nx*larr,2*delta[1]*scale-ny*larr])}

    if AX is None:
        AX = plt
    xscale=np.linspace(lodir[parr][0]-x,lodir[parr][0]-x+float(barl),21)
    AX.plot(xscale, np.zeros([21,1])+lodir[parr][1]-y, cbar, lw=linew,
            scalex=False, scaley=False)
    #plt.arrow(xscale[0],lodir[parr][1]-y,xscale[-1]-xscale[0],0,lw=linew)
    AX.text(xscale[11], lodir[parr][1]-y+larr*(postxt-1.0), bartex,
         horizontalalignment='center',color=ctex, fontsize=bartexs)


def figure(image, cent=[0,0], delta=[0,0], limt=[0,0,0], cmap=['jet'],
           scale=1.0, outima='none', figtitle='none',
           nameaxis=['X','Y'], sizeaxis=None,
           flipaxes=[1, 1],
           pgrid=['off','k'], bbox='tight',
           cont='none', imax='no', imin='no', ncont=10, nivels=None,
           sigmag=2.5, contc=None, contl='no', contf='%3.0f', contsz=10,
           contxt=None, contls='solid',
           cbaropt = 0, cbar=None, cbarlb=None, cbartk=None, cbarl=None,
           barinvt='no',
           aextend='on', aspect='equal', interpolation = 'none', alpha=1,
           AX=None):

    """
    Plot a figure with several characteristics like contours, scales,
    colorbar, etc.

    Parameters
    ----------

    image  : Image to plot
    cent   : Center of the image in pixels  [x,y]
    delta  : Delta of the image in pixels [dx,dy]
    limt   : Minimun and maximum image intesity to be mapped and scale of
            the intensity (normal=0, log=1), [z1,z2,0 or 1]
    cmap   : Color map
    scale  : Scale factor
             (e.g, 0.5 (arcsec/pix) or 0.001(kpc/pix))
    outima : Name of the output file (e.g 'file.png', 'file.pdf', etc)
    figtitle : Title of the figure (e.g 'plot a lot points')
    namexis  : Name of the axes (e.g ['axis x','axis y'], 'off' for no label)
    sizeaxis : size of the label of color bar
    flipaxes: flip the orintation of the axes [1, 1]
    pgrid  : [True,'k'], plot a grid to the image and its colour
    bbox   : Bbox in inches. Only the given portion of the figure is saved. If
             'tight', try to figure out the tight bbox of the figure.
    cont   : Enable contour plot
    imax   : maximum nivel intesity  for the contour
    imin   : minimum nivel intesity  for the contour
    ncont  : Number of the contour
    Nivels : Let the user choose the contour nivels ([n1,n2,n3,...,nf])
    sigmag : Sigma of the Gaussian kernel
    contc  : Color to contours
    contl  : Enable contour Label
    contf  : Contour label Format ('%3.0f')
    contzs : Size contour label (recommend 10)
    contls : contour style Line ('solid','dashed')
    contxt : manual labels for the contours ['1 sig','2 sig']
    cbaropt : by default (0),  without bar
              We have another three options to plot the color bar:
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
    cbarlb : list of manual ticks label for bar ['100','1000','10000']
    cbartk : list of manual ticks for bar [100,1000,10000]
    cbarl  : bar label
    barinvt : 'yes'/'no', To invert the bar scale
    aspect : aspect parameter of the imshow function
    interpolation: interpolation parameter of the imshow function
    alpha : alpha parameter of the imshow function
    aextend : 'off'/'on' extend parameter of the imshow function
    AX     : object,
             Image object or None.

    Some examples of color maps you can use : autumn, bone, cool, copper,
    flag, gray, hot, hsv, jet, pink, prism, spring, summer, winter and spectral.
    if you want an inversion of the color map, just use the '_r' sufix,
    e.g, gray_r.
    """

    AX.minorticks_on()

    try:
        iman = fits.open(image)
        ima = iman[0].data
    except:
        ima = image

    if delta[0] == 0 and delta[1] == 0 :
       delta[0] = ima.shape[1]*0.5 ; delta[1] = ima.shape[0]*0.5

    if cent[0]  == 0 and cent[1]  == 0 :
       cent[0]  = ima.shape[1]*0.5 ; cent[1]  = ima.shape[0]*0.5
    
    x = delta[0]*scale
    y = delta[1]*scale

    if aextend == 'on':
        aextend = [-x*flipaxes[0], x*flipaxes[0], -y*flipaxes[1], y*flipaxes[1]]
    else:
        aextend = None

    l1 = int(cent[0]-delta[0])
    l2 = int(cent[0]+delta[0])
    l3 = int(cent[1]-delta[1])
    l4 = int(cent[1]+delta[1])

    # section image [y1:y2,x1:x2]
    ima1 = ima[l3:l4+1, l1:l2+1]

    if cont != 'none':

        temp = np.copy(ima1)
        if imax == 'no':
            imax = np.amax(temp)
        if imin == 'no':
            imin = np.amin(temp)
        if nivels is None:
            nivels = np.linspace(imin, imax, ncont)
        if sigmag != 0:
            if sys.version_info[0] == 3:
                kernel = Gaussian2DKernel(x_stddev=sigmag)
            else:
                kernel = Gaussian2DKernel(stddev=sigmag)
            smooth = convolve(temp, kernel)
            smooth[np.isnan(temp)]=np.nan
        else:
            smooth = np.copy(temp)
            print ('It was not performed a smoothing for contours')
        print('Contour intesities: ', nivels)
        CS = AX.contour(smooth, nivels, origin='lower', cmap=None,
                       extent=aextend, colors=contc, linestyles=contls)

        # Contour levels
        if contxt != None:
            fmt = {}
            strs = contxt
            for l,s in zip( CS.levels, strs ):
                fmt[l] = s
        else:
            fmt=contf

        if contl != 'no' :
            plt.clabel(CS, fmt=fmt, fontsize=contsz)

    # no user leves
    if limt[0] == 0  and limt[1] == 0 :
        limt[0] = np.nanmin(ima1)
        limt[1] = np.nanmax(ima1)

    if limt[2]==0.0:
        cax = AX.imshow(ima1, origin='lower', cmap=cmap, extent=aextend,
                   vmin=limt[0], vmax=limt[1], interpolation=interpolation,
	    		aspect=aspect, alpha=alpha)
    else:
        cax= AX.imshow(ima1, origin='lower', cmap=cmap, extent=aextend,
                   norm = colors.LogNorm(vmin=limt[0], vmax=limt[1]),
                   interpolation=interpolation, aspect=aspect, alpha=alpha)


    if cbaropt == 1:
        tbar = plt.colorbar(cax, orientation=cbar[0], shrink=cbar[1],
                            pad=cbar[2], format=cbar[3], ax=AX)

    if cbaropt == 2:
        tbar = plt.colorbar(cax, orientation=cbar[0], fraction=0.046,
                         pad=0.04, format=cbar[3], ax=AX)

    if cbaropt == 3:
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        divider = make_axes_locatable(AX)
        cax1 = divider.append_axes("right", size="5%", pad=0.05)
        tbar = plt.colorbar(cax, cax=cax1, format=cbar[3])

    if barinvt == 'yes':
       tbar.ax.invert_yaxis()

    if cbartk is not None:
        tbar.set_ticks(cbartk)
    if cbarlb is not None:
        tbar.set_ticklabels(cbarlb)
    if cbarl is not None:
        if sizeaxis is not None:
            tbar.set_label(cbarl, size=sizeaxis)
        else:
            tbar.set_label(cbarl)

    if nameaxis[0] != 'off':
        AX.set_xlabel('%s'%(nameaxis[0]) )#, size=sizeaxis)
    if nameaxis[1] != 'off':
        AX.set_ylabel('%s'%(nameaxis[1]) )#, size=sizeaxis)

    if pgrid[0] != 'off':
        AX.grid(pgrid[0], c=pgrid[1])
    if figtitle != 'none':
        AX.set_title(figtitle)
    if outima != 'none':
        plt.savefig(outima, format=outima.split('.')[-1], bbox_inches=bbox)

    return cax

def calcu(poly, ima_xy, ima_array, verbose='+'):

    try:
        from matplotlib import path
        pa = path.Path(poly)
        inside = path.Path.contains_points(pa,ima_xy)
    except:
        import matplotlib.nxutils as nx
        inside = nx.points_inside_poly(ima_xy, poly)

    insidepix = np.nonzero(inside)[0]
    skyv = np.array([ima_array[ima_xy[e,1],ima_xy[e,0]] for e in insidepix])
    skyv = skyv[np.where(skyv!=0.0)]
    if len(skyv)!=0:
        statsky = [np.nanmean(skyv), np.nanmedian(skyv), np.nanstd(skyv),
                         len(skyv), np.nanmin(skyv), np.nanmax(skyv),
                         np.nansum(skyv)]
        if verbose == '+':
            print ("\nSky mean : %s" %(np.round(statsky[0],2)))
            print ("Sky median : %s" %(np.round(statsky[1],2)))
            print ("Sky standard deviation : %s" %(np.round(statsky[2],2)))
            print ("Sky area (pix): %s"%(statsky[3]))
            print ("Sky Min: %s"%(np.round(statsky[4],2)))
            print ("Sky Max: %s"%(np.round(statsky[5],2)))
            print ("Sky flux Total: %s"%(statsky[6]))
    else :
        if verbose == '+':
            print ("No pixels")
        statsky = np.array([0,0,0,0,0,0,0])

    return statsky, skyv, ima_xy[insidepix]

def callf(image) :

    global ima_xy, ima_array

    ima_arrayn = fits.open(image)
    ima_array = ima_arrayn[0].data
    ly, lx = np.shape(ima_array)
    x = np.arange(lx)
    y = np.arange(ly)
    X, Y = np.meshgrid(x,y)
    X = np.reshape(X, (lx*ly))
    Y = np.reshape(Y, (lx*ly))
    ima_xy = np.column_stack((X, Y))

    return ima_xy, ima_array


def maskpoly(poly,points_xy,ima_array,ima_xy=None):

    # homogenization of elementes with NaN
    if np.isnan(points_xy[:,0]).any() or np.isnan(points_xy[:,1]).any():
        points_xy[:,1][isnan(points_xy[:,0])] = np.nan
        points_xy[:,0][isnan(points_xy[:,1])] = np.nan

    try :
        from matplotlib import path
        pa = path.Path(poly)
        inside = path.Path.contains_points(pa, points_xy)
    except :
        import matplotlib.nxutils as nx
        inside = nx.points_inside_poly(points_xy, poly)

    insidepix = np.nonzero(inside)[0]
    #print(insidepix)
    if ima_xy is None:
        ima_xy = points_xy
    for e in insidepix :
        ima_array[ima_xy[e, 1], ima_xy[e, 0]] = 0.0

    return ima_array


def histo(ax, data, nbin, outima=None, titlehist=None, xlab='Counts',
          ylab='Number of pixels', dist='gauss', data2=None, norm=False,
          weights = None, histtype='stepfilled', fc='green', alpha=0.5,
          color='green', rg=None, st=False, xlim=0, ylim=0):

    outhist= ax.hist(data, nbin, range=rg, density=norm, weights=weights,
                     align='mid', color=color,
                     histtype=histtype, facecolor=fc, alpha=alpha, stacked=st)

    if dist != 'none':
       if data2 is not None:
           data = data2

       cent = np.nanmean(data)
       sig= np.nanstd(data, ddof=1)
       mindata = np.nanmin(data)
       maxdata = np.nanmax(data)
       N = float(len(data))
       dbin = ((maxdata-mindata)/nbin)
       if weights is None:
          Area = N*dbin
       else:
          Area = np.sum(weights)*dbin

       x = np.linspace(mindata, maxdata, 100)
       if dist == 'gauss':
            gauss_norm = (1./(sig*np.sqrt(2.0*np.pi)))*np.exp((((x-cent)/sig)**2)*-0.5)
            if norm:
                y=gauss_norm
            else:
                y = Area*gauss_norm
            ax.plot(x, y, c=fc, ls='--', linewidth=1)

       if dist == 'uniform':
            if norm:
               yh = 1./(maxdata-mindata)
            else:
               yh = Area/(maxdata-mindata)
            ax.hlines(yh, mindata, maxdata, colors=fc, linestyles='--')
            #ax.vlines(cent, 0, yh, colors=fc, linestyles='--')
            ax.vlines(mindata, 0, yh, colors=fc, linestyles='--')
            ax.vlines(maxdata, 0, yh, colors=fc, linestyles='--')

    if xlim != 0:
        ax.set_xlim(xlim[0],xlim[1])
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    plt.minorticks_on()
    if titlehist:
         ax.set_title(titlehist)
    if outima:
         plt.savefig(outima, format=outima.split('.')[-1], bbox_inches='tight')

    return outhist

def maskinv(mask):
    '''
    This function makes a inversion of a given mask. The pixels with zero value
    now have NaN value, and viceversa.
    '''
    cmask = np.copy(mask)

    cmask[np.isnan(cmask)] = 1.0
    cmask[cmask==0.0] = np.nan
    cmask[cmask==1.0] = 0.0

    return cmask

def masklevel(imagemask, intlevel):
    '''
    This function creates a mask using as criterio a limit intensity
    (intlevel); The pixels < intlevel are replaced by NaN value the
    other ones are replaced by zero.

    '''
    cimagemask = np.copy(imagemask)
    cimagemask[ cimagemask < intlevel] = np.nan

    return cimagemask*0.0


def maskcorona(imagemask, intlevel_0, intlevel_1):
    '''
    This function creates a corona mask; Pixels inside the corona
    have zero value, pixels outside have NaN value.
    '''

    mask_ext = masklevel(imagemask, intlevel_0)
    mask_int_inv = maskinv(masklevel(imagemask, intlevel_1))

    mask_corona = mask_ext + mask_int_inv

    return mask_corona
