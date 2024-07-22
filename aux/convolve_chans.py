#!/usr/bin/env python
# ian.heywood@physics.ox.ac.uk

import glob
import logging
import numpy
import os
import scipy.signal
import shutil
import sys
import time

from astropy.convolution import convolve,Gaussian2DKernel
from astropy.io import fits
from multiprocessing import Pool
from optparse import OptionParser
from shutil import copyfile


def deg2rad(xx):
    return numpy.pi*xx/180.0


def get_psf(infits):
    psf_fits = infits.replace('/pbcor','/psfs').replace('image.pbcor','psf')
    input_hdu = fits.open(psf_fits)[0]
    hdr = input_hdu.header
    bmaj = hdr.get('BMAJ')
    bmin = hdr.get('BMIN')
    bpa = hdr.get('BPA')
    pixscale = hdr.get('CDELT2')
    return bmaj,bmin,bpa,pixscale


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


def conv(infits,beam,scale,opdir,proc):

    proc = str(proc).zfill(2)

    convolved_fits = opdir+'/'+infits.split('/')[-1].replace('.fits','.conv.fits')

    if os.path.isfile(convolved_fits):
        logging.info(f'[Process {proc}] Skipping {infits}')
    else:       
        logging.info(f'[Process {proc}] Convolving {infits}')

        cropsize = 51
        template_fits = 'beam_template_HI.fits'
        target_beam_fits = opdir+'/'+infits.split('/')[-1].replace('.fits','_target_beam.fits')
        restoring_beam_fits = opdir+'/'+infits.split('/')[-1].replace('.fits','_restoring_beam.fits')
        scaled_restoring_beam_fits = opdir+'/'+infits.split('/')[-1].replace('.fits','_scaled_conv_beam.fits')
        kernel_fits = opdir+'/'+infits.split('/')[-1].replace('.fits','_kernel.fits')

        shutil.copyfile(template_fits,target_beam_fits)
        shutil.copyfile(template_fits,restoring_beam_fits)
        shutil.copyfile(template_fits,scaled_restoring_beam_fits)
        shutil.copyfile(infits,convolved_fits)

        # The target beam
        target_bmaj = scale*beam[0]
        target_bmin = scale*beam[1]
        target_bpa = beam[2]
        
        # The existing fitted beam and pixel size
        fitted_bmaj, fitted_bmin, fitted_bpa, pixscale = get_psf(infits)
        fitted_bmaj = scale*fitted_bmaj
        fitted_bmin = scale*fitted_bmin

        logging.info(f'[Process {proc}] Fitted beam: {fitted_bmaj} {fitted_bmin} {fitted_bpa}')

        # Generate and flush image of target beam
        target_xstd = target_bmin/(2.3548*pixscale)
        target_ystd = target_bmaj/(2.3548*pixscale)
        target_theta = deg2rad(target_bpa)
        target_gaussian = Gaussian2DKernel(x_stddev=target_xstd,y_stddev=target_ystd,theta=target_theta,x_size=cropsize,y_size=cropsize,mode='center')
        target_beam_image = target_gaussian.array
        target_beam_image = target_beam_image / numpy.max(target_beam_image)
        flush_fits(target_beam_image,target_beam_fits)

        # Generate and flush image of fitted beam
        fitted_xstd = fitted_bmin/(2.3548*pixscale)
        fitted_ystd = fitted_bmaj/(2.3548*pixscale)
        fitted_theta = deg2rad(fitted_bpa)
        restoring = Gaussian2DKernel(x_stddev=fitted_xstd,y_stddev=fitted_ystd,theta=fitted_theta,x_size=cropsize,y_size=cropsize,mode='center')
        restoring_beam_image = restoring.array
        restoring_beam_image = restoring_beam_image / numpy.max(restoring_beam_image)
        flush_fits(restoring_beam_image,restoring_beam_fits)

        # Generate and flush image of scaled fitted beam
        scaled_fitted_xstd = scale*fitted_bmin/(2.3548*pixscale)
        scaled_fitted_ystd = scale*fitted_bmaj/(2.3548*pixscale)
        scaled_fitted_theta = deg2rad(fitted_bpa)
        scaled_restoring = Gaussian2DKernel(x_stddev=scaled_fitted_xstd,y_stddev=scaled_fitted_ystd,theta=scaled_fitted_theta,x_size=cropsize,y_size=cropsize,mode='center')
        scaled_restoring_beam_image = scaled_restoring.array
        scaled_restoring_beam_image = scaled_restoring_beam_image / numpy.max(scaled_restoring_beam_image)
        flush_fits(scaled_restoring_beam_image,scaled_restoring_beam_fits)


        # Run pypher to generate homogenisation kernel
        os.system('pypher '+restoring_beam_fits+' '+target_beam_fits+' '+kernel_fits)

        # Open channel image and convolve with homogenisation kernel
        input_image = get_image(infits)
        homogenisation_kernel = get_image(kernel_fits)
        input_conv_image = scipy.signal.fftconvolve(input_image, homogenisation_kernel, mode='same')
        logging.info(f'[Process {proc}] Writing {convolved_fits}')
        flush_fits(input_conv_image,convolved_fits)

        # Generate and flush image of scaled fitted beam convolved with homogenisation kernel
        scaled_fitted_xstd = scale*fitted_bmin/(2.3548*pixscale)
        scaled_fitted_ystd = scale*fitted_bmaj/(2.3548*pixscale)
        scaled_fitted_theta = deg2rad(fitted_bpa)
        scaled_restoring = Gaussian2DKernel(x_stddev=scaled_fitted_xstd,y_stddev=scaled_fitted_ystd,theta=scaled_fitted_theta,x_size=cropsize,y_size=cropsize,mode='center')
        scaled_restoring_beam_image = scaled_restoring.array
        scaled_restoring_beam_image = scaled_restoring_beam_image / numpy.max(scaled_restoring_beam_image)
        scaled_restoring_beam_conv_image = scipy.signal.fftconvolve(scaled_restoring_image, homogenisation_kernel, mode='same')
        flush_fits(scaled_restoring_beam_conv_image,scaled_restoring_beam_fits)


        # logging.info(f'[Process {proc}] Cleaning up')
        # for ii in [target_beam_fits,restoring_beam_fits,kernel_fits]:
        #   os.remove(ii)


if __name__ == '__main__':

    # Command line options
    parser = OptionParser(usage = '%prog [options]')
    parser.add_option('--fitspath', dest = 'fits_path', default = '', help = 'Path to input FITS files')
    parser.add_option('--bmaj', dest = 'target_bmaj', default = '', help = 'Major axis of target beam in arcsec')
    parser.add_option('--bmin', dest = 'target_bmin', default = '', help = 'Minor axis of target beam in arcsec')
    parser.add_option('--bpa', dest = 'target_bpa', default = '', help = 'Position angle of target beam in degrees')
    parser.add_option('--scale', dest = 'scale', default = 1.0, help = 'Scale factor, use at own risk')
    parser.add_option('--opdir', dest = 'opdir', default = '', help = 'Output directory')
    parser.add_option('-j', dest = 'j', default = 12, help = 'Number of parallel worker processes (default = 12)')

    (options,args) = parser.parse_args()
    fits_path = options.fits_path
    target_bmaj = options.target_bmaj
    target_bmin = options.target_bmin
    target_bpa = options.target_bpa
    scale = float(options.scale)
    opdir = options.opdir
    j = int(options.j)


    # Make sure all required options are specified
    if '' in [fits_path,target_bmaj,target_bmin,target_bpa,opdir]:
        print('Please specify all required inputs')
        sys.exit()

    # Check that a beam template FITS file is present
    if not os.path.isfile('beam_template_HI.fits'):
        print('Beam template FITS file not found')
        sys.exit()

    # Make output folder if it doesn't exist
    if not os.path.isdir(opdir):
        os.mkdir(opdir)

    # Setup logger
    logfile = opdir+'/convolve_chans.log'
    logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(asctime)s |  %(message)s', datefmt='%d/%m/%Y %H:%M:%S ')
    logging.getLogger().addHandler(logging.StreamHandler())

    # Log the inputs 
    logging.info(f'Using output folder {opdir}')
    logging.info(f'{j} worker processes will be spawned')
    logging.info(f'Target beam shape is {target_bmaj}" {target_bmin}" {target_bpa}deg')

    # Get the input FITS list
    fitslist = sorted(glob.glob(fits_path+'/img*fits'))
    nfits = len(fitslist)
    logging.info(f'Found {nfits} FITS files')

    target_bmaj = float(target_bmaj)/3600.0
    target_bmin = float(target_bmin)/3600.0
    target_bpa = float(target_bpa)
    beam = [target_bmaj,target_bmin,target_bpa] 

    ibeams = [beam]*nfits
    iscale = [scale]*nfits
    iopdirs = [opdir]*nfits
    iproc = numpy.arange(0,nfits)

    pool = Pool(processes=j)
    pool.starmap(conv,zip(fitslist,ibeams,iscale,iopdirs,iproc))


