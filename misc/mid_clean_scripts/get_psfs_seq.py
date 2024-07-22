
import numpy
from astropy.io import fits
import glob
import os
from multiprocessing import Pool


fitsfiles = glob.glob('*-image.fits')
if len(fitsfiles) != 0:
    for fitsfile in fitsfiles:
        conv = fitsfile.replace('image.fits','image.conv.fits')
        if os.path.isfile(conv):
            fitsfile = conv
        chan = fitsfile.split('r0p5-')[-1].split('-')[0]
        input_hdu = fits.open(fitsfile)[0]
        hdr = input_hdu.header
        bmaj = hdr.get('BMAJ')
        bmin = hdr.get('BMIN')
        bpa = hdr.get('BPA')
#        print(chan,fitsfile,bmaj,bmin,bpa)  
        opfile = '../beams/'+chan+'_'+fitsfile+'_'+str(bmaj)+'_'+str(bmin)+'_'+str(bpa)
        os.system('touch '+opfile)
