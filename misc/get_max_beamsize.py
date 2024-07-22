from astropy.io import fits
from multiprocessing import Pool
import glob
import numpy
import os


fits_list = sorted(glob.glob('/scratch3/users/ianh/HIGH_clean/dirty_mosaic_0p5/zoom/*fits'))

def get_max_bmaj(chan):
    chan = str(chan).zfill(4)
    fitslist = sorted(glob.glob('img*'+chan+'*psf.fits'))
    beams = []
    for fitsfile in fitslist:
        input_hdu = fits.open(fitsfile)[0]
        hdr = input_hdu.header
        bmaj = hdr.get('BMAJ')
        beams.append(bmaj)
    bmax = numpy.max(numpy.array(beams))
    opfile = 'beam_'+fitslist[0].split('/')[-1]+'_'+str(bmaj)
    os.system('touch '+opfile)

pool = Pool(processes = 24)

chans = numpy.arange(0,1819)

pool.map(get_max_bmaj,chans)

