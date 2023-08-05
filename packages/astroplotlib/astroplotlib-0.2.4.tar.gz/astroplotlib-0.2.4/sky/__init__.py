#!/usr/bin/env python

import sys
import  numpy as np
import matplotlib.pyplot as plt
import plot_functions as pfunc

def clipping(ivector, sigl=3.0, sigu=3.0, niteration=3, grow=0, verbose='-'):
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
    ToT_remove_l = 0
    ToT_remove_u = 0

    v_mean = np.nanmean(vector)
    v_std  = np.nanstd(vector, ddof=1)
    if verbose == '+':
        print (('\nPrevius values before the sigma-clipping: mean={:.4} std= '+
                '{:.4}').format(v_mean, v_std))
        print (('Setup of the parameters:\nsigl={}, sigu={}, niteration={}, ' +
                'grow={}').format(sigl, sigu, niteration, grow))
    for i in range(int(niteration)):

        if sigl != 0.0:

           prev_nan = vector[np.isnan(vector)].size
           ind_sigl = np.where(vector < (v_mean-sigl*v_std))[0]
           vector[ind_sigl] = np.nan
           remove_l = vector[np.isnan(vector)].size - prev_nan

           j=0
           while j < grow:
               j+=1
               prev_nan = vector[np.isnan(vector)].size
               del_ind = np.copy(ind_sigl)+j
               del_ind = del_ind[(del_ind>-1) & (del_ind<vector.size)]
               vector[del_ind] = np.nan

               del_ind = np.copy(ind_sigl)-j
               del_ind = del_ind[(del_ind>-1) & (del_ind<vector.size)]
               vector[del_ind] = np.nan

               remove_l+=   vector[np.isnan(vector)].size - prev_nan

        else:
            remove_l = 0

        if sigu != 0.0:
            prev_nan = vector[np.isnan(vector)].size
            ind_sigu = np.where(vector > (v_mean+sigu*v_std))[0]
            vector[ind_sigu] = np.nan

            remove_u =  vector[np.isnan(vector)].size - prev_nan

            j=0
            while j < grow:
               j+=1
               prev_nan = vector[np.isnan(vector)].size
               del_ind = np.copy(ind_sigu)+j
               del_ind = del_ind[(del_ind>-1) & (del_ind<vector.size)]
               vector[del_ind] = np.nan

               del_ind = np.copy(ind_sigu)-j
               del_ind = del_ind[(del_ind>-1) & (del_ind<vector.size)]
               vector[del_ind] = np.nan

               remove_u+= vector[isnan(vector)].size - prev_nan

        else:
            remove_u = 0
        v_mean = np.nanmean(vector)
        v_std  = np.nanstd(vector, ddof=1)
        if verbose == '+':
            print (('itera: {} mean: {:.4} std: {:.4}  ToT_Nout {} ' +
                   'Nout_lower: {} Nout_upper: {}' +
                   '').format(i+1, v_mean, v_std, remove_l + remove_u,
                    remove_l, remove_u))

        ToT_remove_l += remove_l
        ToT_remove_u += remove_u
    if verbose == '+':
        print (('All_data: {} ToT_Nout: {} ToT_Nout_lower: {}' +
               ' ToT_Nout_upper: {}').format(vector.size,
                vector[np.isnan(vector)].size, ToT_remove_l, ToT_remove_u))
    return vector

def sky_calculation(image, nhist, regs, parphot, nbin, scale, nameaxis,
                    barscale, parr, cent, delta, limt, cmap, cont, outima,
                    sizeima, vclipping=['no',3,3,3,0,'-']):
     """
     The functions calculates the sky statistics  for given regions on the image

     Parameters
     ----------
      image: str,
          Image name
      nhist: float,
          Numbers of regions')
      regs: array,
          Regions (xcoord,ycoord,width,heigth,ang)
      parphot: array,
          Phot Paramters (scale ima(1.), texp(1.), csky(0.), zp(0.))')
      nbin: float,
          numbers of bins for histogram (recommended 50)
      scale: float,
          Image scale
      nameaxis: array,
          [xlabel, ylabel]
      barscale: array,
          Length bar (pix), text, position) or 'none' to no show "
      parr: array,
          (Position north-east, legth arrow, margen axis y) or 'none'"
      cent: array,
          Image center (cx, cy)
      celta: array,
          Delta image (dx, dy)
      limt: array,
          z1,z2, scale (1 to log, 0 to normal) for each image')
      cmap: str,
          Color map
      cont: array,
          (0,cmin,cmax,cnumb,cor,lab) or (0,no,no,cnumb,cor,lab) or
         (1,n1,n2,...nf,cor or no(cmap),lab) or none
     outimage: str,
         Ouput image name
     sizeima: array,
         Image size in inch (width,heigth) or 'none' by default")

     Notes
     -----
     There are 4 option to location '1' left-bottom,  '2' right-bottom,
     '3' right-top, '4' left-top.

     Notation for the option of the contours:
         cmax: maximum nivel intesity  for the contour\n')
         cmin: minimum nivel intesity  for the contour\n')
         cnumb: Number of the contour\n')
         cor: Contour Colors ('k','r','b')\n")
     When then option 1, user choose the contour nivels (n1,n2,n3,...,nf)
     """

     ima_xy, ima_array = pfunc.callf(image)

     for i in np.arange(nhist):

         polyrec = pfunc.rect(regs[i*5],regs[i*5+1],regs[i*5+2],regs[i*5+3],
                          regs[i*5+4],plotr='no')

         iman='r' + str(i+1) + '.png'
         itit='\nReg. ' + str(i+1)
         print (itit)
         print ('=========')
         sk, skyv, imav = pfunc.calcu(polyrec,ima_xy, ima_array)

         if vclipping[0] == 'yes':
               print ("clipping")
               tskyv = clipping(skyv,*vclipping[1::])
               skyv  = skyv[~np.isnan(tskyv)]

         fig = plt.figure()
         ax = fig.add_subplot(111)
         pfunc.histo(ax, skyv, int(nbin), iman, itit, norm=False)

         skymag  = -2.5*np.log10((sk[-1]-sk[3]*parphot[2])/parphot[1]) + parphot[3]
         skyarea = np.square(parphot[0])*sk[3]
         skymag2 = (-2.5*np.log10((sk[-1]-sk[3]*parphot[2])/(skyarea*parphot[1])) +
                   parphot[3])
         print ("Sky Mag: %s" %(np.round(skymag,2)))
         print ("Sky Mag^2: %s" %(np.round(skymag2,2)))

         if i==0 : skytot=skyv
         else : skytot=np.concatenate((skytot,skyv))

     print ("\nTotal Sky")
     print ("===========")
     print ("\nSky mean total: %s" %(np.round(np.mean(skytot),2)))
     print ("Sky median total: %s" %(np.round(np.median(skytot),2)))
     print ("Sky standard deviation total: %s" %(np.round(np.std(skytot),2)))
     print ("Sky area total: %s"%(len(skytot)))
     print ("Sky Min: %s"%(np.round(np.amin(skytot),2)))
     print ("Sky Max: %s"%(np.round(np.amax(skytot),2)))

     fig = plt.figure()
     ax = fig.add_subplot(111)
     pfunc.histo(ax, skytot, int(nbin), 'skytot.png', 'Total sky', norm=False)

     if sizeima[0] == 'none':
         fig = plt.figure()
     else:
         fig = plt.figure(figsize=(float(sizeima[0]), float(sizeima[1])))
     AX = fig.add_subplot(1, 1, 1)


     if cent[0] == 0 and cent[1] == 0:
         cent[0] = ima_array.shape[1]*0.5
         cent[1] = ima_array.shape[0]*0.5


     # plot of the sky regions
     for i in np.arange(nhist):
         r1 = regs[i*5]*scale
         r2 = regs[i*5+1]*scale
         c1 = cent[0]*scale
         c2 = cent[1]*scale
         l  = regs[i*5+2]*scale
         w  = regs[i*5+3]*scale
         a  = regs[i*5+4]
         pfunc.rect(r1-c1, r2-c2, l, w, a, linef='k-', linew=2)
         plt.text(r1-c1,r2-c2+w+w*0.5, 'Reg ' + str(i+1))


     if parr[0] != 'none':
         pfunc.zetas(image, delta, scale, parr[0], larrow=parr[1], ny=parr[2],
                     AX=AX)

     if barscale[0] != 'none':
         pfunc.bar(delta, scale, barscale[0], barscale[1], barscale[2], AX=AX)

     pfunc.figure(image, cent, delta, limt, cmap, scale, outima,
                  nameaxis=nameaxis, AX=AX)
