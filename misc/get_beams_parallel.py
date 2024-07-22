from astropy.io import fits
from multiprocessing import Pool
import glob
import numpy
import os


fits_list = sorted(glob.glob('/scratch3/users/ianh/HIGH_clean/dirty_mosaic_0p5/zoom/*fits'))

def get_psf(fitsfile):
    input_hdu = fits.open(fitsfile)[0]
    hdr = input_hdu.header
    bmaj = hdr.get('BMAJ')
    bmin = hdr.get('BMIN')
    bpa = hdr.get('BPA')
    opfile = 'beam_'+infits.split('/')[-1]+'_'+str(bmaj)+'_'+str(bmin)+'_'+str(bpa)
    os.system('touch '+opfile)

pool = Pool(processes = 24)

pool.map(get_psf,fits_list)

