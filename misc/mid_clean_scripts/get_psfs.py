
import numpy
from astropy.io import fits
import glob
import os
from multiprocessing import Pool


def getbeam(chan):
    chan = str(chan).zfill(4)
    fitsfile = glob.glob('*/out*/*-'+chan+'-image.fits')
    print(fitsfile)
    if len(fitsfile) != 0:
        fitsfile = fitsfile[0]
        conv = fitsfile.replace('image.fits','image.conv.fits')
        if os.path.isfile(conv):
           fitsfile = conv
        input_hdu = fits.open(fitsfile)[0]
        hdr = input_hdu.header
        bmaj = hdr.get('BMAJ')
        bmin = hdr.get('BMIN')
        bpa = hdr.get('BPA')
#        print(chan,fitsfile,bmaj,bmin,bpa)  
        opfile = fitsfile.split('/')[0]+'/beams/'+chan+'_'+fitsfile.split('/')[-1]+'_'+str(bmaj)+'_'+str(bmin)+'_'+str(bpa)
        print(chan)
        os.system('touch '+opfile)

chans = numpy.arange(1,8803).tolist()
#chans = numpy.arange(1,10).tolist()

j = 8
pool = Pool(processes = j)
pool.map(getbeam,chans)

