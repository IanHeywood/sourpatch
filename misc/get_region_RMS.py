
from astropy.io import fits
from astropy.wcs import WCS
from multiprocessing import Pool
import scipy.special
import scipy.ndimage

import glob
import numpy
import os
import shutil

def get_image(fitsfile):
    """
    Reads FITS file, returns tuple of image_array, header
    """
    input_hdu = fits.open(fitsfile)[0]
    if len(input_hdu.data.shape) == 2:
        image = numpy.array(input_hdu.data[:, :])
    elif len(input_hdu.data.shape) == 3:
        image = numpy.array(input_hdu.data[0, :, :])
    else:
        image = numpy.array(input_hdu.data[0, 0, :, :])
    hdr = input_hdu.header
    freq = hdr.get('CRVAL3')
    return image,freq


def flush_fits(newimage,fitsfile):
    f = fits.open(fitsfile,mode='update')
    input_hdu = f[0]
    if len(input_hdu.data.shape) == 2:
        input_hdu.data[:,:] = newimage
    elif len(input_hdu.data.shape) == 3:
        input_hdu.data[0,:,:] = newimage
    else:
        input_hdu.data[0,0,:,:] = newimage
    f.flush()

def make_noise_map(restored_image, boxsize=100):
    # Cyril's magic minimum filter
    # Plundered from the depths of https://github.com/cyriltasse/DDFacet/blob/master/SkyModel/MakeMask.py
    box = (boxsize, boxsize)
    n = boxsize**2.0
    x = numpy.linspace(-10, 10, 1000)
    f = 0.5 * (1.0 + scipy.special.erf(x / numpy.sqrt(2.0)))
    F = 1.0 - (1.0 - f)**n
    ratio = numpy.abs(numpy.interp(0.5, F, x))
    noise = -scipy.ndimage.filters.minimum_filter(restored_image, box) / ratio
    negative_mask = noise < 0.0
    noise[negative_mask] = 1.0e-10
    median_noise = numpy.nanmedian(noise[mask[0]==1.0])
    median_mask = noise < median_noise
    noise[median_mask] = median_noise
    return median_noise

#fits_list = sorted(glob.glob('/scratch3/users/ianh/MID_clean/taper/zoom/contsub/contsub/COSMOS*fits'))
#fits_list = sorted(glob.glob('/scratch3/users/ianh/mosaic_low/repro/zoom/COSMOS_5200*fits'))
fits_list = sorted(glob.glob('/scratch3/users/ianh/HIGH_clean/dirty_mosaic_0p5/zoom/*fits'))

inreg = 'noise_region.reg'
template = fits_list[0]

noise_mask_fits = 'noise_mask.fits'
shutil.copyfile(template,noise_mask_fits)

image,freq = get_image(template)
image[numpy.isnan(image)] = 0.0
image = image*0.0
flush_fits(image,noise_mask_fits)
opmask = 'noise_mask_reg.fits'
os.system('breizorro -m noise_mask.fits -o noise_mask_reg.fits --merge '+inreg)
mask = get_image('noise_mask_reg.fits')

def get_noise(infits):#,mask):
    chanimg,chanfreq = get_image(infits)
#    chanimg[mask[0]==1.0] = numpy.nan
#    noise = numpy.nanstd(chanimg[mask[0]==1.0])
    noise = make_noise_map(chanimg,100)
    opfile = 'noise_'+infits.split('/')[-1]+'_'+str(chanfreq)+'_'+str(noise)
    os.system('touch '+opfile)

pool = Pool(processes = 24)

pool.map(get_noise,fits_list)


# reg_pix = regions.SkyRegion(reg).to_pixel(wcs)
