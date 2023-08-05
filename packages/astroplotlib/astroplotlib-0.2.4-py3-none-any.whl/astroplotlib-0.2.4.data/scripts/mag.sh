#!/bin/bash

echo " "
echo "-the outfile the daophot (file.mag) :"
read inputfile

echo "-What is the image, aperture, outputfile  :"
read image aper outf

cat $inputfile | awk 'BEGIN{}
                       {
                        if($1 == "'$image'")
                          {
                           pass=1;
                           id=$4;
                           i=0;
                          }
                        if(pass==1 && i==1)
                          {
                          printf("%g\t%g\t",$1,$2);
                          pass=0;
                          pass0=1;
                          i=0;
                          }
                        if(pass0==1 && i==1)
                            {
                            printf("%g\t",$1);
                            pass0=0;
                            pass1=1;
                            i=0;
                            }
                        if(pass1==1 && i==1)
                            {
                            printf("%g\t",$1);
                            pass1=0;
                            i=0;
                            }
                        if($1 =='$aper')
                          {
                          printf("%g\t%g\t%g\t%g\t%g\t%g\n",$2,$3,$4,$5,$6,id)
                          }
                        if(i==0)
                          {
                            i=1;
                          }
                        }'>$outf

sed -i '1s/^/#XCENTER YCENTER MSKY ITIME SUM AREA FLUX MAG MERR ID\n/' $outf
echo ""
echo "-Done!-"
echo ""
