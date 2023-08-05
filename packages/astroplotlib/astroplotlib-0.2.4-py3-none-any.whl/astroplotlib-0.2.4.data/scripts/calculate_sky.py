#!python

from __future__ import print_function
import sys
import sky

try:
     finput=open(sys.argv[1]).read().splitlines()

except:

     print ('\nThis script plots the regions used to measure sky value (mean, ') 
     print ('std, etc. The input paramters to run this program are:\n' )
     print ('     # image')
     print ('     # numbers of regions')
     print ('     # Regions (xcoord,ycoord,width,heigth,ang)')
     print ('     # Phot Paramters (scale ima(1.), texp(1.), csky(0.), zp(0.))')
     print ('     # numbers of bins for histogram (recommended 50)')
     print ('     # scale,units')
     print ("     # (length bar (pix), text, position) or 'none' to no show ")
     print ("    # (Position north-east, legth arrow, margen axis y) or 'none'" 
            + "to no show ") 
     print ('     # x,y center')
     print ('     # dx,dy image')
     print ('     # z1,z2, scale (1 to log, 0 to normal) for each image')
     print ('     # Color map (1 to inv, 0 to normal)')
     print ('     # (0,cmin,cmax,cnumb,cor,lab) or (0,no,no,cnumb,cor,lab) or' +
            ' (1,n1,n2,...nf,cor or no(cmap),lab) or none ')
     print ('     # Output image  ')
     print ("     # size image in inch (width,heigth) or 'none' by default")  
     print ('\n')
     print ("There are 4 option to location '1' left-bottom,  '2' right-bottom," 
            + "'3' right-top, '4' left-top.\n ")
     print ('Notation for the option of the contours:\n')
     print (' cmax: maximum nivel intesity  for the contour\n')
     print (' cmin: minimum nivel intesity  for the contour\n')
     print (' cnumb: Number of the contour\n')
     print (" cor: Contour Colors ('k','r','b')\n")
     print (' when then option 1, user choose the contour nivels' + 
           '(n1,n2,n3,...,nf)\n')

     sys.exit()

i = 0
image = finput[i].split()[0].split(',');i+=1   
nhist  = int(finput[i].split()[0]);i+=1      
regs   = [float(s) for s in finput[i].split()[0].split(',')];i+=1
parphot = [float(s) for s in finput[i].split()[0].split(',')];i+=1 
nbin  =  float(finput[i].split()[0]);i+=1                       
scale  = float(finput[i].split()[0].split(',')[0])              
units = finput[i].split()[0].split(',')[1];i+=1              
barscale =' '.join(finput[i].split('#')[0].split());i+=1      
parr   = finput[i].split()[0].split(',');i+=1                
cent   = [float(s) for s in finput[i].split()[0].split(',')];i+=1   
delta  = [float(s) for s in finput[i].split()[0].split(',')];i+=1  
limt   = [float(s) for s in finput[i].split()[0].split(',')];i+=1 
cmap   = finput[i].split()[0];i+=1                      
cont   = finput[i].split()[0].split(',');i+=1                       
outima = finput[i].split()[0];i+=1                              
sizeima = finput[i].split()[0].split(','); i+=1                 

barscale = barscale.split(',')

sky.sky_calculation(image[0], nhist, regs, parphot, nbin, scale, units, 
                    barscale, parr, cent, delta, limt, cmap, cont, outima, 
                    sizeima)

