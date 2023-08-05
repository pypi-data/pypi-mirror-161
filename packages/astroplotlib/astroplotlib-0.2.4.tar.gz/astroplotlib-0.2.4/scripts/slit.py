#!/usr/bin/env python

import sys, os
from plot_slit import *

try:
    finput=open(sys.argv[1]).read().splitlines()

except: 
    print ("\nThis script plot a long-slit (with apertures) on the image.")
    print ("For run this program you need to provide the following " + 
           "parameter:\n")
    print ('      # slit size (width,length,color,linewidth) in arcsec or' + 
           'none for not plot')
    print ('      # (apertures name,color,lw,circ or sqrt,0) or ' + 
           '(start,end,step,color,lw,circ or swrt,1) ')
    print ('      # position in (RA,0) or in pix (x,1) of the center ' + 
           'of the long-slit')
    print ('      # position in (DEC,0) or in pix (y,1) of the center of ' + 
           'the long-slit')
    print ('      # angle of the long-slit in counterclockwise  relative ' + 
           'horizotal axis (x postive)')
    print '      # (center spectra bidimensional) or (cent length)'
    print '      # scale in arcsec for the bidimensional spectra'
    print '      # scale in arcsec for the imag'
    print '      # points on long-slit '
    print '      # points position (x,y,color,0 or 1(arrow)) or none'
    print '      # text for points (eg, [1,2,3,4] or [a,b,c,d])'
    print '      # photometry image name (.fits)'
    print '      # image scale (pix, arcsec,kpc), units'
    print '      # center of the image (ra,dec,0) or (x,y,1)' 
    print '      # dx,dy image'
    print '      # z1,z2, scale (1 to log, 0 to normal)'
    print '      # Color map (1 to inv, 0 to normal) '
    print ('      # Outputs (coord. in pix apert (.dat), profile ' + 
           'intense apert (.dat), profile (.png), image (.png)')
    print '\n'
    sys.exit()

i=0

slitsize1 = finput[i].split()[0];i+=1  
filein1 = finput[i].split()[0].split(',');i+=1   
ra1     = [float(s) for s in finput[i].split()[0].split(',')];i+=1 
dec1    = [float(s) for s in finput[i].split()[0].split(',')];i+=1
th1     = float(finput[i].split()[0]);i+=1 	 
centf1  = float(finput[i].split()[0]);i+=1 
scaper1 = float(finput[i].split()[0]);i+=1  
scimage1= float(finput[i].split()[0]);i+=1  
points1 = finput[i].split()[0];i+=1        
locpot1 = finput[i].split()[0];i+=1        
texpot1 = finput[i].split()[0];i+=1 
image1  = finput[i].split()[0];i+=1 
scale1  = float(finput[i].split()[0].split(',')[0])  
units1  = finput[i].split()[0].split(',')[1];i+=1  
cent1   = [float(s) for s in finput[i].split()[0].split(',')];i+=1                 
delta1  = [float(s) for s in finput[i].split()[0].split(',')];i+=1  
limt1   = [float(s) for s in finput[i].split()[0].split(',')];i+=1 
cmap1   = finput[i].split()[0].split(',');i+=1     
outima1 = finput[i].split()[0].split(',');i+=1   


fig = plt.figure()
AX = fig.add_subplot(1, 1, 1)

coorfenda(slitsize1, filein1, ra1, dec1, th1, centf1, scaper1, scimage1, 
          points1, locpot1, texpot1, image1, scale1, units1, cent1, 
          delta1, limt1, cmap1, outima1)

if outima1[3] != 'none':
    zetas(image1, delta1, scale1, '2', ny=1.8, nx=0.5, AX=AX)
    bar(delta1, scale1, 2.53, '1 kpc', AX=AX)
    figure(image1, cent1, delta1, limt1, cmap1, units1, scale1, outima1[3],
           cbar=['vertical',1.0,0.0,'%.1f'], AX=AX)
