import numpy
import glob
import os
import subprocess
from multiprocessing import Pool
from astropy.io import fits
import numpy

def get_image(fitsfile):
        input_hdu = fits.open(fitsfile)[0]
        if len(input_hdu.data.shape) == 2:
                image = numpy.array(input_hdu.data[:,:])
        elif len(input_hdu.data.shape) == 3:
                image = numpy.array(input_hdu.data[0,:,:])
        elif len(input_hdu.data.shape) == 4:
                image = numpy.array(input_hdu.data[0,0,:,:])
        else:
                image = numpy.array(input_hdu.data[0,0,0,:,:])
        return image


def flush_fits(newimage,fitsfile):
        f = fits.open(fitsfile,mode='update')
        input_hdu = f[0]
        if len(input_hdu.data.shape) == 2:
                input_hdu.data[:,:] = newimage
        elif len(input_hdu.data.shape) == 3:
                input_hdu.data[0,:,:] = newimage_
        elif len(input_hdu.data.shape) == 4:
                input_hdu.data[0,0,:,:] = newimage
        else:
                input_hdu.data[0,0,0,:,:] = newimage
        f.flush()


def fix_zeros(infits):
    img = get_image(infits)
    mask = img == 0.0
    img[mask] = numpy.nan
    flush_fits(img,infits)


if __name__ == '__main__':

    j = 28

    fitslist = sorted(glob.glob('COSMOS*fits'))
    pool = Pool(processes=j)
    pool.map(fix_zeros,fitslist)
