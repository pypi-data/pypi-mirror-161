#!/usr/bin/python

from tkinter import *
from tkFileDialog import *
from tkMessageBox import *
from os.path import expanduser
home = expanduser("~")
import os

import matplotlib.pyplot as plt

task = {'YXL':'1,1', 'YL':'1,0', 'XL':'0,1', 'YXS':'1,1','YS':'1,0','XS':'0,1'}


def add(even=None):
    """
    This function is to add the specification for each subplot of the
    output parameters.
    """
    prev = var15.get()

    if prev == 0:
       act = (var9.get() + ',' + var9a.get() + ',' + task[var9b.get()] + ',' +
             task[var9c.get()] + ',' + var16.get())
       var15.set(act)
    else:
       act = (prev + ',' + var9.get() + ',' + var9a.get() + ',' +
              task[var9b.get()] + ',' + task[var9c.get()] + ',' + var16.get())
       var15.set(act)


root = Tk()
root.title('Plot output parameters from ellipse/Package astroplotlib')

global savekey, openkey
savekey = True; openkey= True

Label(root, text=' ').grid(row=1, column=0, columnspan=5)
rowl=4
Label(root, text=' ').grid(row=rowl, column=0, columnspan=5)

span=6
exp=7
sizentry=50
rowl+=1
Label(root, text="image").grid(row=rowl, column=0)
global var1
var1 = StringVar()
e1 = Entry(root, bd =5, textvariable=var1,width=sizentry)
e1 = e1.grid(row=rowl,column=1,columnspan=span)
Label(root, text="Image to plot").grid(row=rowl, column=exp, sticky=W)

rowl+=1
Label(root, text="table").grid(row=rowl, column=0)
global var2
var2 = StringVar()
Entry(root, bd =5, textvariable=var2,width=sizentry).grid(row=rowl,
      column=1,columnspan=span)
Label(root, text="Table output Ellipse").grid(row=rowl, column=exp, sticky=W)

rowl+=1
Label(root, text="radius").grid(row=rowl, column=0)
global var3
var3 = StringVar()
Entry(root, bd =5, textvariable=var3,width=sizentry).grid(row=rowl,
      column=1, columnspan=span)
text = "radmin, radmax, step, color"
Label(root, text=text).grid(row=rowl, column=exp, sticky=W)


rowl+=1
Label(root, text="rad_user").grid(row=rowl, column=0)
global var13
var13 = StringVar()
Entry(root, bd =5, textvariable=var13,width=sizentry).grid(row=rowl,
      column=1, columnspan=span)
text = "radmin, radmax, step, color (graph limits)"
Label(root, text=text).grid(row=rowl, column=exp, sticky=W)


rowl+=1
Label(root, text="refer").grid(row=rowl, column=0)
global var11
var11 = StringVar()
Entry(root, bd =5, textvariable=var11,width=sizentry).grid(row=rowl,
      column=1, columnspan=span)
text = "mag zero(0.0), pix/scale (arcsec)(1.0), v. sky(0.0), exp. time(1.0)"
Label(root, text=text).grid(row=rowl,column=exp,sticky=W)

rowl+=1
Label(root, text="nameaxes").grid(row=rowl, column=0)
global var12
var12 = StringVar()
Entry(root, bd =5, textvariable=var12,width=sizentry).grid(row=rowl,
      column=1, columnspan=span)
text = "xlabel , ylabel"
Label(root, text=text).grid(row=rowl, column=exp, sticky=W)

rowl+=1
Label(root, text="cent").grid(row=rowl, column=0)
global var4
var4 = StringVar()
Entry(root, bd =5, textvariable=var4,width=sizentry).grid(row=rowl,
      column=1, columnspan=span)
Label(root, text="x,y center image").grid(row=rowl, column=exp, sticky=W)

rowl+=1
Label(root, text="delta").grid(row=rowl, column=0)
global var5
var5 = StringVar()
Entry(root, bd =5, textvariable=var5,width=sizentry).grid(row=rowl,
      column=1, columnspan=span)
Label(root, text="dx,dy image").grid(row=rowl, column=exp, sticky=W)

rowl+=1
Label(root, text="ima_scale").grid(row=rowl,column=0)
global var6
var6 = StringVar()
Entry(root, bd =5, textvariable=var6,width=sizentry).grid(row=rowl,
      column=1, columnspan=span)
text = "z1, z2, scale (1 to log, 0 to normal)"
Label(root, text=text).grid(row=rowl, column=exp, sticky=W)

rowl+=1
Label(root, text="cmap").grid(row=rowl, column=0)
#optionList = ("jet", "gray", "cool","hot", "spectral","cubehelix","b")
#var7 = StringVar()
#var7.set(optionList[0])
#OptionMenu (root, var7, *optionList ).grid(row=rowl,column=1)
#global var7a
#var7a = IntVar()
#Radiobutton(root, text="norm", variable=var7a, value=0).grid(row=rowl,column=2)
#Radiobutton(root, text="inv color", variable=var7a, value=1).grid(row=rowl,column=3)
global var7
var7 = StringVar()
Entry(root, bd =5, textvariable=var7,width=sizentry).grid(row=rowl,
      column=1, columnspan=span)
Label(root, text="Color map").grid(row=rowl, column=exp, sticky=W)

rowl+=1
Label(root, text="color").grid(row=rowl,column=0)
global var8
var8 = StringVar()
Entry(root, bd =5, textvariable=var8,width=sizentry).grid(row=rowl, column=1,
      columnspan=span)
text = ("(Color ellipses (k or none), color countours (r or none), smoothness" +
        " (7) and grid (0 or 1)")
Label(root, text=text).grid(row=rowl, column=exp, sticky=W)


rowl+=1
Label(root, text="subplot").grid(row=rowl,column=0)
global var17
var17 = StringVar()
Entry(root, bd =5, textvariable=var17,width=sizentry).grid(row=rowl,
      column=1, columnspan=span)
Label(root, text="numrow, numcol").grid(row=rowl, column=exp, sticky=W)

rowl+=1
Label(root, text="param").grid(row=rowl,column=0)
optionList2 = ("SMA", "RSMA", "R_eq_E","R_eq_T","LOG_SMA")
var9 = StringVar()
var9.set(optionList2[0])
OptionMenu (root, var9, *optionList2 ).grid(row=rowl,column=1)

optionList3 = ("INTENS", "PA", "ELLIP", "MAG", "MAG2", "A4", "TFLUX_E",
               "TFLUX_C", "TFLUX_T","TMAG_E", "TMAG_C", "TMAG_T")
var9a = StringVar()
var9a.set(optionList3[0])
OptionMenu (root, var9a, *optionList3 ).grid(row=rowl,column=2)


optionList4 = ("YXL", "YL","XL")
var9b = StringVar()
var9b.set(optionList4[0])
OptionMenu (root, var9b, *optionList4 ).grid(row=rowl,column=3)

optionList5 = ("YXS", "YS","XS")
var9c = StringVar()
var9c.set(optionList5[0])
OptionMenu (root, var9c, *optionList5 ).grid(row=rowl,column=4)



global var16
var16 = StringVar()
Entry(root, bd =5, textvariable=var16,width=6).grid(row=rowl,column=5)
Button(root, text='add',command=add).grid(row=rowl,column=6)
text = "Params for each subplot (x,f(x),label(x-y),stick(x-y),space(h,w)"
Label(root, text=text).grid(row=rowl, column=exp, sticky=W)

rowl+=1
Label(root, text="listplot").grid(row=rowl,column=0)
global var15
var15 = StringVar()
Entry(root, bd =5, textvariable=var15,width=sizentry).grid(row=rowl,
      column=1, columnspan=span)
Label(root, text="Params for each subplot ").grid(row=rowl, column=exp,
      sticky=W)


rowl+=1
Label(root, text="sizeima").grid(row=rowl,column=0)
global var14
var14 = StringVar()
Entry(root, bd =5, textvariable=var14,width=sizentry).grid(row=rowl,
      column=1, columnspan=span)
Label(root, text="figsize (w,h,w,h) in inches").grid(row=rowl,
      column=exp, sticky=W)

rowl+=1
Label(root, text="format").grid(row=rowl,column=0)
global var10
var10 = StringVar()
Entry(root, bd =5, textvariable=var10,width=sizentry).grid(row=rowl,
      column=1, columnspan=span)
text = "Outputs: table (none), image (none), parameters (none) "
Label(root, text=text).grid(row=rowl,column=exp,sticky=W)


def quit(event=None):
    root.destroy()

def go(event=None):

    image=var1.get().split()[0]                                       # Image to plot
    table=var2.get().split()[0]                                       # table output elipse task
    rad=[int (s) for s in var3.get().split()[0].split(',')[0:-1]]     # Radius min, max, step
    cora=var3.get().split()[0].split(',')[-1]                         # Color and format of the points
    rad2=[int (s) for s in var13.get().split()[0].split(',')[0:-1]]   # Radius min, max, step limits for graphs
    corp=var13.get().split()[0].split(',')[-1]                        # Color and format of the points
    magzp=float(var11.get().split()[0].split(',')[0])                 # Magnitud point zero
    pixscale=float(var11.get().split()[0].split(',')[1])              # pix scale arcsec
    sky=float(var11.get().split()[0].split(',')[2])                   # sky in IDU
    ref=float(var11.get().split()[0].split(',')[3])                   # reference point
    nameaxis=var12.get().split()[0].split(',')                        # xlabel, ylabel
    cent=[float(s) for s in var4.get().split()[0].split(',')]         # x,y center image
    delta=[float(s) for s in var5.get().split()[0].split(',')]        # dx,dy image
    limt=[float(s) for s in var6.get().split()[0].split(',')]         # z1,z2, scale (1 to log, 0 to normal)
    cmap = var7.get()                                                 # Color map
    elicon=var8.get().split()[0].split(',')                           # (Color ellip, or none, color count. or none,smoothness (7),0 no grid or 1 grid)
    subp=[int(s) for s in var17.get().split()[0].split(',')]          # numrow, numcol
    parm=var15.get().split()[0].split(',')                            # subplots parameters
    figs=[float(s) for s in var14.get().split()[0].split(',')]        # figsize (w,h,w,h) in inches
    outima=var10.get().split()[0].split(',')                          # Output image and format
    var16.set('0,0')

    global savekey
    savekey = True
    fsave()
    import plot_ellipse
    plot_ellipse.ellip(image, table, rad, cora, rad2, corp, cent, delta, limt,
                       cmap, elicon, subp, parm, figs, outima, magzp, pixscale,
                       sky, ref, nameaxis)
    plt.show()
def fopen(event=None):

   global openkey

   if openkey:
      filename = '{}/.guiparm/graph.parm'.format(home)
      openkey = False

   else :
      filename =askopenfilename(filetypes=[("allfiles","*")])

   try:
      finput=open(filename).read().splitlines()
      k=0
      var1.set(finput[k].split()[0]);k+=1                # Image to plot
      var2.set(finput[k].split()[0]);k+=1                # Table output Ellipse
      var3.set(finput[k].split()[0]);k+=1                # radmin, radmax, step,color
      var13.set(finput[k].split()[0]);k+=1               # radmin, radmax, step,color  limits for graphs
      var11.set(finput[k].split()[0]);k+=1               # magzp, pixscale
      var12.set(finput[k].split()[0]);k+=1               # xlabel, ylabel
      var4.set(finput[k].split()[0]);k+=1                # x,y center image
      var5.set(finput[k].split()[0]);k+=1                # dx,dy image
      var6.set(finput[k].split()[0]);k+=1                # z1,z2, scale (1 to log, 0 to normal)
      var7.set(finput[k].split()[0]);k+=1                # Color map
      var8.set(finput[k].split()[0]);k+=1                # (Color ellip, or none, color count. or none,smoothness (7),0 no grid or 1 grid)
      var17.set(finput[k].split()[0]);k+=1               # numrow, numcol
      var15.set(finput[k].split()[0]);k+=1               # subplots parameters
      var14.set(finput[k].split()[0]);k+=1               # figsize (w,h,w,h) in inches
      var10.set(finput[k].split()[0])                    # Output image and format
      var16.set('0,0')

   except:
      showwarning("Open file","Cannot open this file")
      return

def fsave(event=None):

    global savekey
    if savekey:
        path = '{}/.guiparm/'.format(home)
        if not os.path.exists(path):
              os.mkdir(path)
        filename = '{}/.guiparm/graph.parm'.format(home)
        savekey = 0
    else :
        fileo = asksaveasfile(mode='w')
        filename = fileo.name

    fs = open(filename,'w')
    fs.write('%s             # Image to plot \n'		                           %(var1.get()))
    fs.write('%s             # Table output Ellipse\n'                             %(var2.get()))
    fs.write('%s             # radmin, radmax, step, color  \n'	                   %(var3.get()))
    fs.write('%s             # radmin, radmax, step, color  limits for graphs \n'  %(var13.get()))
    fs.write('%s             # magzp, pixscale (arcsec)\n'                         %(var11.get()))
    fs.write('%s             # xlabel, ylabel \n'                                  %(var12.get()))
    fs.write('%s             # x,y center image\n'		                           %(var4.get()))
    fs.write('%s             # dx,dy image \n'		                               %(var5.get()))
    fs.write('%s             # z1,z2, scale (1 to log, 0 to normal) \n'            %(var6.get()))
    fs.write('%s             # Color map \n'%(var7.get()))
    fs.write('%s             # (Color ellip, or none, color count. or none,smoothness (7),0 no grid or 1 grid)\n' %(var8.get()))
    fs.write('%s             # numrow, numcol \n'                                  %(var17.get()))
    fs.write('%s             # subplot parameters \n'                              %(var15.get()))
    fs.write('%s             # figsize (w,h,w,h) in inches \n'                     %(var14.get()))
    fs.write('%s             # Outputs (table,image,parameters) '		           %(var10.get()))
    fs.close()

def unlearn() :

    var1.set('')                # Image to plot
    var2.set('')                # Table output Ellipse
    var3.set('')                # radmin, radmax, step, color
    var13.set('')               # radmin, radmax, step, color limits for graphs
    var11.set('')               # magzp, pixscale
    var12.set('')               # xlabel, ylabel
    var4.set('')                # x,y center image
    var5.set('')                # dx,dy image
    var6.set('')                # z1,z2, scale (1 to log, 0 to normal)
    var7.set('gray')            # color map
    var8.set('none,none,7,0')   # (Color ellip, or none, color count. or none,smoothness (7),0 no grid or 1 grid)
    var16.set('0,0')            # subplots_adjust(hspace,wspace) in inches
    var9.set('SMA')             # Abscissa (SMA,RSMA,etc.)
    var9a.set('INTENS')         # Ordinate (MAG,PA,etc.)
    var9b.set('YXL')            # Active on (1) axis label (Y,X)
    var9c.set('YXS')            # Active on (1) stick lable (Y,X)
    var14.set('6,6,8,6')        # figsize (w,h,w,h) in inches
    var10.set('')               # Outrowl+=2puts (table,image,parameters)


rowl+=1
Label(root, text=" ").grid(row=rowl,column=1, columnspan=4)

rowl+=1
Button(root, text='go!', command=go,background='yellow',
       foreground='blue', width=10).grid(row=rowl,column=2, columnspan=2)
Button(root, text='close',command=quit).grid(row=rowl,column=0)

Button(root, text='open file', command=fopen).grid(row=2,column=0)
Button(root, text='save file', command=fsave).grid(row=2,column=1)
Button(root, text='unlearn', command=unlearn).grid(row=2,column=2)

fopen()

root.mainloop()
