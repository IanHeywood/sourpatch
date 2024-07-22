from astropy.io import fits
import datetime
import numpy
import sys
import glob
from multiprocessing import Pool


def getfreq(fitsfile):
    input_hdu = fits.open(fitsfile)[0]
    hdr = input_hdu.header
    freq = hdr.get('CRVAL3')
    chanwidth = hdr.get('CDELT3')
    return freq,chanwidth

def getImage(fitsfile):
    input_hdu = fits.open(fitsfile)[0]
    if len(input_hdu.data.shape) == 2:
            image = numpy.array(input_hdu.data[:,:])
    elif len(input_hdu.data.shape) == 3:
            image = numpy.array(input_hdu.data[0,:,:])
    else:
            image = numpy.array(input_hdu.data[0,0,:,:])
    return image


def getbeam(chan):
    beams = glob.glob('/scratch3/users/ianh/MID_clean/*/beams/*-'+chan+'-*')
    for beam in beams:
        parts = beam.split('_')


def fix_hdr(myfits,freq,chanwidth):
    img = getImage(myfits)
    new_image = (numpy.expand_dims(numpy.expand_dims(img, axis=0), axis=0))
    new_image[new_image==0.0] = numpy.nan
    print(myfits,freqs,chanwidth)
    outhdu = fits.open(myfits,mode='update')
    outhdr = outhdu[0].header
    outhdr.set('CTYPE3','FREQ',after='CTYPE2')
    outhdr.set('CRVAL3',freq,after='CRVAL2')
    outhdr.set('CRPIX3',1,after='CRPIX2')
    outhdr.set('CDELT3',chanwidth,after='CDELT2')
    outhdr.set('CTYPE4','STOKES',after='CTYPE3')
    outhdr.set('CRVAL4',1,after='CRVAL3')
    outhdr.set('CRPIX4',1,after='CRPIX3')
    outhdr.set('CDELT4',1,after='CDELT3')
    fits.writeto(myfits,new_image,outhdr,overwrite=True)


xx = sorted(glob.glob('COSMOS*fits'))
chan0 = xx[0].split('_')[-1].replace('.fits','')
# Need to somehow select a consistent pointing here, field name will do for now
freq0,chanwidth0 = getfreq('/idia/projects/mightee/ianh/HI/img_COSMOS_MID_dirty_mosaics/COSMOS_MID_x15_140323_0001.fits')
nchan = len(xx)
chans = numpy.arange(int(chan0),int(chan0)+nchan)-int(chan0)
df = chans*chanwidth0
freqs = freq0+df
chanwidths = chanwidth0 * numpy.ones(len(xx))

/idia/projects/mightee/ianh/HI/img_COSMOS_MID_dirty_mosaics/

j = 30
pool = Pool(processes = j)
pool.starmap(fix_hdr,zip(xx,freqs,chanwidths))