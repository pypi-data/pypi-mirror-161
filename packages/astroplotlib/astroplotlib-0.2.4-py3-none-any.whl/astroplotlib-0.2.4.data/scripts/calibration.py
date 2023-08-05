# Import Modules

import pyfits
import numpy as np
from astLib import *
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy import *
from scipy import optimize
import sys

def clipping(ivector, sigl=3.0, sigu=3.0, niteration=3, verbose='-'):
    '''
    Given an array this function does a clipping for lower and higher outliner 
    points in the array.
 
    Parameters
    ----------
    vetor : array_like, 
        Array containg elements to clip
    sigl : float, 
        Sigma-clip criterion for upper deviant points, 0 for no clip
    sigu : float, 
        Sigma-clip criterion for lower deviant points, 0 for no clip
    niteration : float, 
        Number of sigma-clip iterations
    
    Return 
    ------
    clipvector : ndarray,
        An array with the same size that input array, all elements clipped
        were assined NaN 

    '''
    vector = np.copy(ivector)

    v_mean = np.nanmean(vector)
    v_std  = np.nanstd(vector, ddof=1)
    if verbose == '+':
        print 'previus mean: {:.4} std: {:.4}'.format(v_mean, v_std)
    for i in range(int(niteration)):
                
        if sigl != 0.0:
           remove_l = np.where(vector < (v_mean-sigl*v_std))[0].size
           vector[vector < (v_mean-sigl*v_std)] = nan
        else:
            remove_l = 0
        if sigu != 0.0:
            remove_u = np.where(vector > (v_mean+sigu*v_std))[0].size
            vector[vector > (v_mean+sigu*v_std)] = nan
        else:
            remove_u = 0
        v_mean = np.nanmean(vector)
        v_std  = np.nanstd(vector, ddof=1)
        if verbose == '+':
            print ('itera: {} mean: {:.4} std: {:.4} all data: {} ' + 
                'Nout_lower: {} Nout_upper: {}').format(i, v_mean, v_std, 
                vector.size, remove_l, remove_u)
  
    return vector

finput=open(sys.argv[1]).read().splitlines()

i=0

arqv =  finput[i].split()[0];i+=1  
cata = finput[i].split()[0];i+=1  
filt = finput[i].split()[0];i+=1  
mag_i =  int(finput[i].split()[0]);i+=1         
mag_J = int(finput[i].split()[0]);i+=1        
mag_F = int(finput[i].split()[0]);i+=1         
outima =  finput[i].split()[0];i+=1  

mag_i      = np.loadtxt(arqv, unpack=True, usecols=[mag_i])
mag_J,mag_F= np.loadtxt(arqv, unpack=True, usecols=(mag_J, mag_F))


print ("{} (J)".format(cata))
print (mag_J)
print ("{} (F)".format(cata))
print (mag_F)

if cata == 'gsc':
    # http://www.astro.umd.edu/~ssm/ASTR620/mags.html 
    # (Windhorst, R. W., et al. 1991, ApJ, 380, 362)
    #Gunn g to Photographic J: 	J = g + 0.39 + 0.37*(g-r) 	[1]
    #Gunn r to Photographic F: 	F = r - 0.25 + 0.17*(g-r) 	[1] 
    
    #J-F = (g-r) + 0.64 + 0.20*(g-r)
    
    #J-F   = +0.64  + 1.20*(g-r)
    
    #(g-r) = -0.533 + 0.833*(J-F)
        
    #r = F + 0.341 - 0.142*(J-F)
    if filt == 'r':
        mag_f = mag_F + 0.341 - 0.142*(mag_J - mag_F)

if cata == 'usno':
  
    if filt == 'r':
        mag_f = mag_F + 0.076 + 0.092*(mag_J - mag_F)
    if filt == 'g':
        mag_f = mag_J - 0.050 - 0.066*(mag_J - mag_F)



print ('calibrated magnitude {} '.format(filt))
print (np.round(mag_f,2))

print ('instrumental magnitude {}'.format(filt, mag_i))
print (np.round(mag_i,2))

Zc = clipping(mag_f - mag_i,3,3,10, '+')

mag_i[np.isnan(Zc)] =  nan
mag_f[np.isnan(Zc)] = nan

print ('The star removed were: ')
print (where(isnan(mag_i))[0] + 1)

mag_i = mag_i[np.isnan(mag_i)==False]
mag_f = mag_f[np.isnan(mag_f)==False]

Z = np.round(np.nanmean(Zc),2)


## Fit the first set
fitfunc = lambda p, x: p[0]*x + p[1] # Target function
errfunc = lambda p, x, y: fitfunc(p, x) - y # Distance to the target function
p0 = [1.0, Z] # Initial guess for the parameters
p1, success = optimize.leastsq(errfunc, p0[:], args=(mag_i, mag_f))

print ("Equation ")
print ("{} = {:2.2f}*{} + {:2.2f}".format(filt, p1[0], filt, p1[1]))


print ('Diference between calibrated and intrumetal magnitudes:')
print (np.round(mag_f-mag_i,2))
print ('mean:')
print (Z)
print ('standard desviation:')
print (np.round(np.std(mag_f-mag_i),2))

plt.plot(mag_i,mag_f,'b.')
plt.plot(mag_i,fitfunc(p1,mag_i),'r-')
plt.ylabel('Calibrated Mag')
plt.xlabel('Instrumental Mag')
plt.minorticks_on()
plt.savefig(outima, format=outima.split('.')[-1], bbox_inches='tight')
plt.show()




