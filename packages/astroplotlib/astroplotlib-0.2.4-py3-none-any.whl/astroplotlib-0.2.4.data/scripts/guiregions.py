#!python
#Author : J. A. Hernandez-Jimenez

from tkinter import *
from tkinter.filedialog import *
from tkinter.messagebox import *
from numpy import *
from scipy.ndimage.filters import gaussian_filter
from astropy.io import fits
import matplotlib.pyplot as plt
from plot_functions import figure, callf, maskpoly, rect, circ
import os
from os.path import expanduser
home = expanduser("~")


root = Tk()
root.title('Regions ')


#global variables
openkey = True
savekey = True


def quit(event=None):
    import sys
    sys.exit()

def magstruc(event=None):

    image = var3.get().split()[0]
    # type of aperture circ or square
    aper = var2.get().split()[0].split(',')[0]
    if aper == 'square':
        cx, cy, dtx, dty, ang, contlev, sigma = [float(s) for s in
                                         var2.get().split()[0].split(',')[1:8]]
    if aper == 'circ':
        cx, cy, rad, contlev, sigma = [float(s) for s in
                                         var2.get().split()[0].split(',')[1:6]]



    # load image in matrix
    imagem = fits.open(image)[0].data
    # load image as pair coordinate
    imagep = callf(image)
    # region mask
    if aper == 'square':
        regmask = maskpoly(rect(cx, cy, dtx, dty, ang, 200,
                       plotr='no'), imagep[0], imagem*nan)
    if aper == 'circ':
        regmask = maskpoly(circ(cx, cy, rad, 200, plotr='no'),
                       imagep[0], imagem*nan)



    # smoothing the image
    if sigma != 0 :
       imagem=gaussian_filter(imagem,sigma)
    # masking the image by the region
    imagemask = imagem + regmask
    # masking the image by Intensity level
    imagemask[ imagemask < contlev] = nan

    # saving the mask image
    if aper == 'square':
        nmask = var2.get().split()[0].split(',')[8]
    if aper == 'circ':
        nmask = var2.get().split()[0].split(',')[6]

    print ("\nCreating the mask {}".format(nmask))
    print ("- nan for all pixels with Int_lev < Int_limit")
    print ("- 0   for all pixels with lnt_lev > Int_limit")
    fits.writeto(nmask, imagemask*0.0, overwrite=True)

    # calculating the flux and area of masked  region
    fluxt = nansum(imagemask)
    area  = len(imagemask[~isnan(imagemask)])



    try:
        # sky, texp, scpix, zp
        sky, texp, scpix, zp  = [float(s) for s in
                                              var9.get().split()[0].split(',')]

        print ("\nsky : {}, texp : {}, scpix : {}, zp : {}".format(sky,
                                                               texp, scpix, zp))
        magt  = -2.5*log10( (fluxt-area*sky)/texp ) + zp
        magt_arc = -2.5*log10( (fluxt-area*sky)/(texp*area*square(scpix)) )+zp

        print ("\nIntegrating from intensity level : {}".format(contlev))
        print ("Flux (Intens) : {}".format(round(fluxt,2)))
        print ("Area (N of pixels) : {}".format(area))
        print ("Magnitud  : {}".format(round(magt,2)))
        print ("Magnitud (arcsec^2)  : {}".format(round(magt_arc,2)))

    except:
        print ("\nIntegrating from intensity level : {}".format(contlev))
        print ("Flux (Intens) : {}".format(round(fluxt,2)))
        print ("Area (N of pixels) : {}".format(area))

    # Plotting the region masked
    plotima(imagemask,'yes')


def plotima (ima, mask='no'):

    # x,y center image
    cent=[float(s) for s in var4.get().split()[0].split(',')]
    # dx,dy image
    delta=[float(s) for s in var5.get().split()[0].split(',')]
    # z1,z2, scale (1 to log, 0 to normal)
    limt=[float(s) for s in var6.get().split()[0].split(',')]
    # color map
    cmap=var7.get().split()[0]
    # contours
    cont=var8.get().split()[0].split(',')

    # There are 3 options to plot contours:
    # * (0,cmin,cmax,cnumb,sigma,cor,label)
    # * (0,no,no,cnumb,sigma,cor,label)
    # * (1,n1,n2,...nf,sigma,cor,label)

    if cont != 'none' and mask=='no':

        # ption 1 and 2
        if cont[0]=='0':
            imax=float(cont[2]); imin=float(cont[1]);
            ncont=int(cont[3]); sigmag=float(cont[-3]);
            contc=cont[-2]; contl=cont[-1]
        # option 3
        else:
            nivels=[float(s) for s in cont[1:-3]];
            sigmag=float(cont[-3]); contc=cont[-2]; contl=cont[-1]


        fig = plt.figure(num=1)
        AX = fig.add_subplot(1, 1, 1)
        figure(ima, cent, delta, limt, cmap, cont='yes', nivels=nivels,
               sigmag=sigmag, contc=contc, contl=contl, contf='%3.2f',
               aextend='none', AX=AX)
    else:
        fig = plt.figure(num=2)
        plt.clf()
        AX = fig.add_subplot(1, 1, 1)
        figure(ima, cent, delta, limt, cmap, aextend='none', AX=AX)

    plt.show()

def go(event=None):
    image = var3.get().split()[0]
    plotima(image)

    global savekey
    savekey = True
    fsave()

def fopen(event=None):

   global openkey
   if openkey:
        filename = '{}/.guiparm/guiregions.parm'.format(home)
        openkey = False

   else:
        filename = askopenfilename(filetypes=[("allfiles","*"),
                                ("pythonfiles","*.py")])


   try:
      finput=open(filename).read().splitlines()
      k=0
      var3.set(finput[k].split()[0]);k+=1
      var4.set(finput[k].split()[0]);k+=1
      var5.set(finput[k].split()[0]);k+=1
      var6.set(finput[k].split()[0]);k+=1
      var7.set(finput[k].split()[0]);k+=1
      var8.set(finput[k].split()[0]);k+=1
      var2.set(finput[k].split()[0]);k+=1
      var9.set(finput[k].split()[0])

   except:
      showwarning("Open file","Cannot open this file")
      return


def fsave(event=None):

      global savekey
      if savekey:
          path = '{}/.guiparm/'.format(home)
          if not os.path.exists(path):
              os.mkdir(path)
          fileo = '{}/.guiparm/guiregions.parm'.format(home)
          savekey = False
      else:
           fs = asksaveasfile(mode='w', defaultextension=".txt")
           fileo = fs.name

      fs = open(fileo,'w')
      fs.write('%s             # Image to plot \n'       %(var3.get()))
      fs.write('%s             # x,y center image\n'     %(var4.get()))
      fs.write('%s             # dx,dy image \n'         %(var5.get()))
      fs.write('%s             # z1,z2, scale (1 to log, 0 to normal) \n'
               %(var6.get()))
      fs.write('%s             # Color map, invert color map (1) or '
               'normal(0) \n' %(var7.get()))
      fs.write('%s             # 1,n1,n2,...nf,sigma,cor,label (yes or no)\n'
               %(var8.get()))
      fs.write('%s             # reg,cx,cy,dx,dy,iso_cont,ima.fits \n'
               %(var2.get()))
      fs.write('%s             # sky,texp,scpix,zp'      %(var9.get()))
      fs.close()



rowl=0
Label(root, text="       ").grid(row=rowl,column=0,sticky=W)
rowl+=1
Label(root, text="       ").grid(row=rowl,column=0,sticky=W)

sizentry=40
span=1
exp=2

rowl+=1
Label(root, text="image").grid(row=rowl,column=0)
global var3
var3 = StringVar()
Entry(root, bd =5, textvariable=var3,width=sizentry).grid(row=rowl,
      column=1,columnspan=span)
Label(root, text="Image to plot").grid(row=rowl,column=exp,sticky=W)

rowl+=1
Label(root, text="cent").grid(row=rowl,column=0)
global var4
var4 = StringVar()
Entry(root, bd =5, textvariable=var4,width=sizentry).grid(row=rowl,
           column=1,columnspan=span)
Label(root, text="x,y center image").grid(row=rowl,column=exp,sticky=W)

rowl+=1
l5 = Label(root, text="delta").grid(row=rowl,column=0)
global var5
var5 = StringVar()
Entry(root, bd =5, textvariable=var5,width=sizentry).grid(row=rowl,column=1,
      columnspan=span)
Label(root, text="dx,dy image").grid(row=rowl,column=exp,sticky=W)

rowl+=1
Label(root, text="scale").grid(row=rowl,column=0)
global var6
var6 = StringVar()
Entry(root, bd =5, textvariable=var6,width=sizentry).grid(row=rowl,column=1,
      columnspan=span)
Label(root, text="z1,z2, scale (1 to log, 0 to normal)").grid(row=rowl,
      column=exp,sticky=W)

rowl+=1
Label(root, text="cmap").grid(row=rowl,column=0)
global var7
var7 = StringVar()
Entry(root, bd =5, textvariable=var7,width=sizentry).grid(row=rowl, column=1,
      columnspan=span)
Label(root, text="color_map, 0 (normal) or 1 (inv)").grid(row=rowl,
      column=exp, sticky=W)

rowl+=1
Label(root, text="contours").grid(row=rowl,column=0)
global var8
var8 = StringVar()
Entry(root, bd =5, textvariable=var8, width=sizentry).grid(row=rowl,
      column=1,columnspan=span)
var8.set('1,n1,n2,...nf,sigma,cor,label (yes or no)')
Label(root, text="1,n1,n2,...nf,sigma,cor,label (yes or no)").grid(row=rowl,
      column=exp,sticky=W)


rowl+=1
Label(root, text="       ").grid(row=rowl,column=0,sticky=W)

rowl+=1
Label(root, text="region").grid(row=rowl,column=0)
global var2
var2 = StringVar()
Entry(root, bd =5, textvariable=var2,width=sizentry).grid(row=rowl,column=1)
var2.set('aper,cx,cy,dx,dy,ang,iso_cont,sig,ima.fits')
Label(root, text="aper (square or circ), cx, cy, dtx, dty, ang, "
      "intscontour, sigma, maskname.fits ").grid(row=rowl,column=exp,sticky=W)


rowl+=1
Label(root, text="       ").grid(row=rowl,column=0,sticky=W)

rowl+=1
Label(root, text="par_phot").grid(row=rowl,column=0)
global var9
var9 = StringVar()
Entry(root, bd =5, textvariable=var9,width=sizentry).grid(row=rowl,column=1)
var9.set('sky,texp,scpix,zp')
Label(root, text=" options: sky,texp,scpix,zp ").grid(row=rowl,
column=exp,sticky=W)

rowl+=1
Label(root, text="       ").grid(row=rowl,column=0,sticky=W)
rowl+=1
Label(root, text="       ").grid(row=rowl,column=0,sticky=W)

rowl+=1
Button(root, text='magstruc',command=magstruc).grid(row=rowl,column=0,)
Button(root, text='open file', command=fopen).grid(row=rowl,column=1,sticky=W)
Button(root, text='go',command=go).grid(row=rowl,column=2)
rowl+=1
Button(root, text='save file',command=fsave).grid(row=rowl,column=1,sticky=W)
Button(root, text='close',command=quit).grid(row=rowl,column=2)

fopen()

root.mainloop()
