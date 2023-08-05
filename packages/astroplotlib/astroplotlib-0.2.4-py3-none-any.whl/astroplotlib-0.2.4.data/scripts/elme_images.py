#!python

# This script plot the elmegreen image for any kind of configuration. An input
# file should be supplied.

import sys
import plot_functions as pfunc

import matplotlib as mpl
#mpl.rcParams['axes.labelsize']= 15
#mpl.rcParams['legend.fontsize']= 15
mpl.rcParams['xtick.major.size']= 8
mpl.rcParams['xtick.minor.size']= 4
mpl.rcParams['ytick.major.size']= 8
mpl.rcParams['ytick.minor.size']= 4
mpl.rcParams['xtick.labelsize']=15
mpl.rcParams['ytick.labelsize']= 15

# To avoid font3 in pdf files
#mpl.rcParams['ps.useafm'] = True
#mpl.rcParams['pdf.use14corefonts'] = True
#mpl.rcParams['text.usetex'] = True

try:
    finput=open(sys.argv[1]).read().splitlines()

except:
    # The input program are:
    print '\nPlot a  set the elmegreen image for any kind of configuration'
    print "\nFor run this programm you need provide the following parameter:\n"
    print '      # list images (.fits)     '
    print "      # list titles ('none' for no title)     "
    print "      # numrow, numcol   "
    print "      # label names for each image (e.g., X,Y,X,Y)    "
    print '      # scale image units/pix (e.g, 0.146 arcsec/pix) '
    print ("      # length bar (scale image), text, location image  " +
           "('none' to no show)")
    print '      # location of the arrow north-east		     '
    print '      # center of the image (x,y'
    print '      # dx,dy image'
    print '      # z1,z2, scale (1 to log, 0 to normal) for each image'
    print '      # Color map (1 to inv, 0 to normal) '
    print ('      # plot contour 4 options: (0,cmin,cmax,cnumb,cor) or ' +
           '(0,no,no,cnumb,cor) or  (1,n1,n2,...nf,cor) or none ')
    print '      # Outputs image (e.g figure.png, figure.eps)'
    print '      # size image in inch (width,heigth)                     '
    print '\n'
    print ("There are 4 option to location '1' left-bottom,  " +
           "'2' right-bottom, '3' right-top, '4' left-top.\n ")
    print 'Notation for the option of the contours:\n'
    print ' cmax: maximum nivel intesity  for the contour\n'
    print ' cmin: minimum nivel intesity  for the contour\n'
    print ' cnumb: Number of the contour\n'
    print " cor: Contour Colors ('k','r','b')\n"
    print (' when then option 1, user choose the contour nivels ' +
           '(n1,n2,n3,...,nf)\n')

    sys.exit()

##########################
# Loading the input file #
##########################

i=0

image  = finput[i].split()[0].split(',');i+=1          # list images
titleg = finput[i].split('#')[0].split(',');i+=1       # list titles
titleg[-1]  =' '.join(titleg[-1].split())
subp   = [float(s) for s in finput[i].split()[0].split(',')];i+=1  # numrow, numcol
print(finput[i])
labaxi = finput[i].split('#')[0].split(',');i+=1       # label axis ('0' to no or '1' to yes) for each image
scale1  = float(finput[i].split()[0]);i+=1             # scale
barscale =' '.join(finput[i].split('#')[0].split());i+=1  # (length bar (pix), text, perct post y), 'none' to no show
parr   = finput[i].split()[0];i+=1                        # Position of the arrow north-east
cent   = [int(s) for s in finput[i].split()[0].split(',')];i+=1   # x,y center
delta  = [int(s) for s in finput[i].split()[0].split(',')];i+=1   # dx,dy image
limt   = [float(s) for s in finput[i].split()[0].split(',')];i+=1   # z1,z2, scale (1 to log, 0 to normal) for each image
cmap   = finput[i].split()[0];i+=1                     # Color map (1 to inv, 0 to normal)
cont= finput[i].split()[0].split(',');i+=1             # (0,cmin,cmax,cnumb,cor,lab) or (0,no,no,cnumb,cor,lab) or  (1,n1,n2,...nf,cor or no(cmap),lab) or none
outima1 = finput[i].split()[0];i+=1                    # Output image
sizeima = [float(s) for s in finput[i].split()[0].split(',')];i+=1  # size image in inch (width,heigth)

###################
# Plotting images #
###################

fig = plt.figure(figsize=(sizeima[0],sizeima[1]))

for i in arange(len(image)-1):
    ax = fig.add_subplot(subp[0], subp[1],i+1)
    #if i==0 :
        #568 pc/arcsec =  0.568 kpc/arcsec
        #17.6,'10 kpc'
        #zetas(image[0], delta, scale1, parr='2', larrow=5.0, nx=1.1, ny=1.1,
        #      lhat=1.16, postxtn=1.5, postxte=1.5, carr='k', ctex='k',
        #      linew=2)
        #bar(delta, scale1, 8.8, '5 kpc', parr='1', larrow=5.0, nx=0.8, ny=1.0,
        #    postxt=1.2, cbar='k-', ctex='k', linew=2)

    pfunc.figure(image[i], cent, delta, [limt[i*3], limt[i*3+1], limt[i*3+2]],
                 cmap, scale=scale1, figtitle=titleg[i],
                 nameaxis=[labaxi[i*2], labaxi[i*2+1]], pgrid=[True,'k'], AX=ax)

ax = fig.add_subplot(subp[0], subp[1],len(image))

pfunc.figure(image[-1], cent,delta, [limt[-3], limt[-2], limt[-1]], cmap,
             scale=scale1, outima=outima1, figtitle=titleg[-1],
             nameaxis=[labaxi[-2],labaxi[-1]], pgrid=[True,'k'],
             AX=ax)
