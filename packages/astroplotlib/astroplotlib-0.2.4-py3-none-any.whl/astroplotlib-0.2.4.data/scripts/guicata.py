#!python

import tkinter
from tkinter import *
from tkinter.filedialog import *
from tkinter.messagebox import *
from os.path import expanduser
home = expanduser("~")
import os

#global variables
openkey = True
savekey = True

root = tkinter.Tk()
root.title('Plot star catalogues')
#top=Frame(root)
#top.pack(side='top')

rowl=1
Label(root, text='Pack Catalogue').grid(row=rowl,column=0)
rowl+=1
Label(root, text='').grid(row=rowl,column=0,columnspan=5)

exp=3
rowl+=1
Label(root, text="image").grid(row=rowl,column=0)
var1 = StringVar()
Entry(root, bd =5, textvariable=var1).grid(row=rowl,column=1,columnspan=2)
Label(root, text="Image to plot").grid(row=rowl,column=exp,sticky=W)

rowl+=1
Label(root, text="Catalogue").grid(row=rowl, column=0)
var2 = StringVar()
Entry(root, bd =5, textvariable=var2).grid(row=rowl, column=1, columnspan=2)
Label(root, text="(0,file,col_X,col_Y) or (1,file,col_RA,col_DEC) " +
      "or (2,gal_name,cat_outputname,rad_arcsec,cat_name=GSC2.3)").grid(row=rowl,
      column=exp, sticky=W)

rowl+=1
Label(root, text="Radius").grid(row=rowl,column=0)
var3 = StringVar()
Entry(root, bd =5, textvariable=var3).grid(row=rowl,column=1,columnspan=2)
Label(root, text="Radius of the circle, color format, and  linewidth," +
                 " offsetx (label on), offsety(label on)").grid(row=rowl,
                 column=exp,sticky=W)

rowl+=1
Label(root, text="coord").grid(row=rowl,column=0)
var4 = StringVar()
Entry(root, bd =5, textvariable=var4).grid(row=rowl,column=1,columnspan=2)
Label(root, text="wcs coord or pix coord or " +
                 "none (not print)").grid(row=rowl,column=exp,sticky=W)


rowl+=1
Label(root, text="scale").grid(row=rowl,column=0)
var11 = StringVar()
Entry(root, bd =5, textvariable=var11).grid(row=rowl,column=1,columnspan=2)
Label(root, text="image scale, xlabel, ylabel").grid(row=rowl,column=exp,
      sticky=W)


rowl+=1
Label(root, text="cent").grid(row=rowl,column=0)
var5 = StringVar()
Entry(root, bd =5, textvariable=var5).grid(row=rowl,column=1,columnspan=2)
Label(root, text="x, y image center").grid(row=rowl,column=exp,sticky=W)

rowl+=1
Label(root, text="delta").grid(row=rowl,column=0)
var6 = StringVar()
Entry(root, bd =5, textvariable=var6).grid(row=rowl,column=1,columnspan=2)
Label(root, text="image dx, dy ").grid(row=rowl,column=exp,sticky=W)

rowl+=1
Label(root, text="ima_sc").grid(row=rowl,column=0)
var7 = StringVar()
Entry(root, bd =5, textvariable=var7).grid(row=rowl,column=1,columnspan=2)
Label(root, text="zmin, zmax, scale (1 to log, 0 to linear)").grid(row=rowl,
      column=exp,sticky=W)



rowl+=1
Label(root, text="cmap").grid(row=rowl,column=0)
var8 = StringVar()
Entry(root, bd =5, textvariable=var8).grid(row=rowl,column=1,columnspan=2)
Label(root, text="Color map").grid(row=rowl,
      column=exp,sticky=W)



#rowl+=1
#Label(root, text="label").grid(row=rowl,column=0)
#optionList = ("jet", "gray","gray_r", "winter","hot", "spectral")
#var8 = StringVar()
#var8.set(optionList[0])
#OptionMenu (root, var8, *optionList ).grid(row=rowl,column=1)
#var8a = IntVar()
#Radiobutton(root, text="inv color", variable=var8a, value=1).grid(row=rowl,
#            column=2)
#Label(root, text="Color map").grid(row=rowl,column=exp,sticky=W)


rowl+=1
Label(root, text="format").grid(row=rowl,column=0)
var9=StringVar()
Entry(root, bd =5, textvariable=var9).grid(row=rowl,column=1,columnspan=2)
Label(root, text="Name image output (or none)").grid(row=rowl, column=exp,
      sticky=W)

rowl+=1
Label(root, text="label").grid(row=rowl,column=0)
var10 = IntVar()
Radiobutton(root, text="yes", variable=var10, value=1).grid(row=rowl,column=1)
Radiobutton(root, text="no", variable=var10, value=0).grid(row=rowl, column=2,
            sticky=W)
Label(root, text="Label for the objects?").grid(row=rowl, column=exp,
      sticky=W)


rowl+=1
Label(root, text="imasize").grid(row=rowl,column=0)
var12=StringVar()
Entry(root, bd =5, textvariable=var12).grid(row=rowl,column=1,columnspan=2)
Label(root, text="image size ([width,height,idfig]) (or none)").grid(row=rowl,
      column=exp, sticky=W)

#E1.config(textvariable=var)
#var1.set('enter here')


def quit(event=None):
    root.destroy()

def go(event=None):

    image = var1.get().split()[0]
    catalog = var2.get().split()[0].split(',')
    r = var3.get().split()[0].split(',')#[0:3]
    starpix = var4.get().split()[0]
    scale = float(var11.get().split()[0].split(',')[0])
    nameaxis = (var11.get().split()[0].split(','))[1::]
    #print (nameaxis)
    cent = [float(s) for s in var5.get().split()[0].split(',')]
    delta = [float(s) for s in var6.get().split()[0].split(',')]
    limt = [float(s) for s in var7.get().split()[0].split(',')]
    #cmap = []
    #cmap.append(var8.get())
    #cmap.append(var8a.get())
    cmap = var8.get().split()[0]
    outima = var9.get().split()[0]
    label = var10.get()
    imasz = var12.get().split()[0]

    global savekey
    savekey = True
    fsave()

    var10.set(0)
#    var8a.set(0)

    import cata
    cata.catalog(image, catalog, r, starpix, cent, delta, limt, cmap, outima,
                 label, scale, nameaxis, imasz)


def fopen(event=None):

    global openkey
    if openkey:
        filename = '{}/.guiparm/cata.parm'.format(home)
        openkey = False

    else:
        filename = askopenfilename(filetypes=[("allfiles","*"),
                                ("pythonfiles","*.py")])

    try:
        finput=open(filename).read().splitlines()

        var1.set(finput[0].split()[0])
        var2.set(finput[1].split()[0])
        var3.set(finput[2].split()[0])
        var4.set(finput[3].split()[0])
        var11.set(finput[4].split()[0])
        var5.set(finput[5].split()[0])
        var6.set(finput[6].split()[0])
        var7.set(finput[7].split()[0])
        #var8.set(finput[8].split()[0].split(',')[0])
        #var8a.set(finput[8].split()[0].split(',')[1])
        var8.set(finput[8].split()[0])
        var9.set(finput[9].split()[0])
        var10.set(finput[10].split()[0])
        var12.set(finput[11].split()[0])

    except:
        showwarning("Open file","Cannot open this file")
    return



def fsave(event=None):

    global savekey
    if savekey:
        path = '{}/.guiparm/'.format(home)
        if not os.path.exists(path):
              os.mkdir(path)
        fileo = '{}/.guiparm/cata.parm'.format(home)
        savekey = False
    else:
        fs = asksaveasfile(mode='w')
        fileo = fs.name

    fs=open(fileo,'w')
    fs.write('%s          # Image to plot \n'%(var1.get()))
    fs.write(('%s          # Catalogue in pixels (x,y) (file,0) or ' +
             'in coord (ra, dec) (file,1)\n')%(var2.get()))
    fs.write(('%s          # Radius of the circle, color format, and' +
             ' linewidth \n')%(var3.get()))
    fs.write(('%s          # wcs coord or pix coord or no ' +
             '(not print) \n')%(var4.get()))
    fs.write('%s          # scale (arcsec/pix,kpc/pix), xlabel, ylabel\n'
             %(var11.get()))
    fs.write('%s          # x,y center image\n'%(var5.get()))
    fs.write('%s          # dx,dy image \n'%(var6.get()))
    fs.write(('%s          # z1,z2, scale (1 to log, 0 to ' +
             'normal) \n')%(var7.get()))
    #fs.write(('%s,%s       # Color map, invert color map (1) or ' +
    #         'normal(0) \n')%(var8.get(),var8a.get()))
    fs.write(('%s      # Color map, invert color map (1) or ' +
             'normal(0) \n')%(var8.get()))



    fs.write(('%s          # Output image and format (none for no ' +
             'outout) \n')%(var9.get()))
    fs.write('%s          # Label sources (yes=1 or no=0)\n'%(var10.get()))
    fs.write('%s          # image size ([width,heigth,idfig])\n'%(var12.get()))
    fs.close()



def unlearn() :

    var1.set('')         # Image to plot
    var2.set('')         #  0 (x,y) or  1 (rad,dec) or 2 (object)
                         # for O or 1:  filename, col1, col2
                         # for 2: namegalaxy, catalog (gsc2.3, usno-b1),
                         #        [boxsize_alpha, boxsize_delta] in arcmin,
                         #        constraint Fmag<22,jmag<22

    var3.set('')         # Radius of the circle, color format, and linewidth
    var4.set('')         # wcs coord or pix coord or no (not print)
    var11.set('1.0,pix,pix') # scale (arcsec/pix,kpc/pix), xlabel, ylabel
    var5.set('')         # x,y center image
    var6.set('')         # dx,dy image
    var7.set('')         # z1,z2, scale (1 to log, 0 to normal)
    #var8.set('gray')     # color map
    #var8a.set(0)         # inver color map
    var8.set('gray')
    var9.set('')         # Output image and format
    var10.set(0)         # Label sources (yes=1 or no=0)
    var12.set('10,10,1') # image size ([width,heigth,idfig])


rowl+=1
Label(root, text=" ").grid(row=rowl,column=1, columnspan=4)

rowl+=1
Button(root, text='close',command=quit).grid(row=rowl,column=0)
Button(root, text='go!!', command=go,background='yellow',
       foreground='blue').grid(row=rowl,column=1)
Button(root, text='open file', command=fopen, background='yellow',
       foreground='blue').grid(row=rowl,column=2)
Button(root, text='save file', command=fsave,background='yellow',
       foreground='blue').grid(row=rowl,column=3)
Button(root, text='unlearn', command=unlearn, background='yellow',
       foreground='blue').grid(row=rowl,column=4)

fopen()

root.mainloop()
