#!/usr/bin/env python
# ian.heywood@physics.ox.ac.uk


import datetime
import glob
import logging
import numpy
import os
import re
import scipy.ndimage
import scipy.special
import shutil
import sys
import time
from astropy.io import fits
from datetime import datetime
from optparse import OptionParser
from multiprocessing import Pool
from scipy.ndimage import binary_dilation, binary_fill_holes, binary_erosion
from scipy.ndimage import label, find_objects
from scipy.ndimage import minimum_filter
from scipy.ndimage import sum as ndi_sum


date_time = datetime.now()
timestamp = date_time.strftime('%d%m%Y_%H%M%S')


# ------------------------------------------------------------------
# Setup logger

logfile = 'pony_'+timestamp+'.log'
#logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(asctime)s:: %(levelname)-5s :: %(message)s %(funcName)s', datefmt='%d/%m/%Y %H:%M:%S ')
logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(asctime)s:: %(levelname)-5s :: %(message)s', datefmt='%d/%m/%Y %H:%M:%S ',force=True)
logging.getLogger().addHandler(logging.StreamHandler())


def hello():
    logging.info('                       .oPYo.   .oPYo.   odYo.   o    o        ')
    logging.info("                       8    8   8    8   8' `8   8    8        ")
    logging.info('                       8    8   8    8   8   8   8    8        ')
    logging.info("                       8YooP'   `YooP'   8   8   `YooP8        ")
    logging.info('                       8                              8        ')
    logging.info("                       8                           ooP'   v0.1 ")


def spacer():
    logging.info('')
    logging.info('-'*80)
    logging.info('')


def natural_sort(l):
    """
    Natural sort
    """
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def get_image(fits_file):
    """
    Get the 2D image data from fits_file and return as a numpy array
    """
    input_hdu = fits.open(fits_file,ignore_missing_simple=True)[0]
    if len(input_hdu.data.shape) == 2:
            image_data = numpy.array(input_hdu.data[:,:])
    elif len(input_hdu.data.shape) == 3:
            image_data = numpy.array(input_hdu.data[0,:,:])
    else:
            image_data = numpy.array(input_hdu.data[0,0,:,:])
    return image_data


def flush_image(image_data,fits_file):
    """
    Write 2D image_data array to fits_file
    """
    f = fits.open(fits_file,mode='update')
    input_hdu = f[0]
    if len(input_hdu.data.shape) == 2:
            input_hdu.data[:,:] = image_data
    elif len(input_hdu.data.shape) == 3:
            input_hdu.data[0,:,:] = image_data
    elif len(input_hdu.data.shape) == 4:
            input_hdu.data[0,0,:,:] = image_data
    f.flush()


def load_cube(fits_list):
    """
    Loads a sequence of FITS images into 3D numpy array
    Images must be in frequency order
    """
    temp = []
    for fits_file in fits_list:
        img = get_image(fits_file)
        temp.append(img)
    cube = numpy.dstack(temp)
    return cube


def get_mask_and_noise(input_image,threshold,boxsize,dilate):
    """
    Kentoc'h mervel eget bezan saotret
    Return boolean array of islands above threshold and array of local noise estimation
    """
    box = (boxsize,boxsize)
    n = boxsize**2.0
    x = numpy.linspace(-10,10,1000)
    f = 0.5 * (1.0 + scipy.special.erf(x / numpy.sqrt(2.0)))
    F = 1.0 - (1.0 - f)**n
    ratio = numpy.abs(numpy.interp(0.5, F, x))
    noise_image = -minimum_filter(input_image, box) / ratio
    negative_mask = noise_image < 0.0
    noise_image[negative_mask] = 1.0e-10
    median_noise = numpy.median(noise_image)
    median_mask = noise_image < median_noise
    noise_image[median_mask] = median_noise
    mask_image = input_image > threshold * noise_image
    if dilate > 0:
        mask_image = binary_dilation(mask_image,iterations = dilate)
    return mask_image, noise_image


def make_mask(input_fits,threshold,boxsize,dilate,invert,opdir,masktag,noisetag,savenoise,overwrite,idx):
    """
    Function called by multiprocessing pool to create mask (and noise) images
    """
    idx = str(idx).zfill(5)
    mask_fits = opdir+'/'+masktag+'/'+input_fits.replace('.fits','.'+masktag+'.fits')
    if os.path.isfile(mask_fits) and not overwrite:
        logging.info(f'[M{idx}] Skipping {input_fits} (overwrite disabled)')
    else:
        logging.info(f'[M{idx}] Reading {input_fits}')
        input_image = get_image(input_fits)
        if invert:
            logging.info(f'[M{idx}] Inverting {input_fits}')
            input_image = input_image * -1.0
        logging.info(f'[M{idx}] Finding islands')
        mask_image, noise_image = get_mask_and_noise(input_image,threshold,boxsize,dilate)
        logging.info(f'[M{idx}] Writing {mask_fits}')
        shutil.copyfile(input_fits,mask_fits)
        flush_image(mask_image,mask_fits)
        if savenoise:
            noise_fits = opdir+'/'+noisetag+'/'+input_fits.replace('.fits','.'+noisetag+'.fits')
            shutil.copyfile(input_fits,noise_fits)
            logging.info(f'[M{idx}] Writing {noise_fits}')
            flush_image(noise_image,noise_fits)


def make_averaged_mask(input_fits_subset,threshold,boxsize,dilate,opdir,masktag,noisetag,savenoise,averagetag,saveaverage,overwrite,idx):
    """
    Function called by multiprocessing pool to average sequence of images and create mask (and noise) images
    Central image in list is the target
    """
    idx = str(idx).zfill(5)
    nfits = len(input_fits_subset)
    input_fits = input_fits_subset[nfits//2]
    mask_fits = opdir+'/'+masktag+'/'+input_fits.replace('.fits','.'+masktag+'.fits')
    if os.path.isfile(mask_fits) and not overwrite:
        logging.info(f'[A{idx}] Skipping {mask_fits} (overwrite disabled)')
    else:
        logging.info(f'[A{idx}] Reading subset')
        cube = load_cube(input_fits_subset)
        mean_image = numpy.nanmean(cube,axis=2)
        if invert:
            logging.info(f'[M{idx}] Inverting subset')
            mean_image = mean_image * -1.0
        logging.info(f'[A{idx}] Finding islands')
        mask_image, noise_image = get_mask_and_noise(mean_image,threshold,boxsize,dilate)
        logging.info(f'[A{idx}] Writing {mask_fits}')
        shutil.copyfile(input_fits,mask_fits)
        flush_image(mask_image,mask_fits)
        if saveaverage:
            logging.info(f'[A{idx}] Writing {mean_fits}')
            mean_fits = opdir+'/'+averagetag+'/'+input_fits.replace('.fits','.'+averagetag+'.fits')
            shutil.copyfile(input_fits,mean_fits)
            flush_image(mean_image,mean_fits)
        if savenoise:
            noise_fits = opdir+'/'+noisetag+'/'+input_fits.replace('.fits','.'+noisetag+'.fits')
            shutil.copyfile(input_fits,noise_fits)
            logging.info(f'[A{idx}] Writing {noise_fits}')
            flush_image(noise_image,noise_fits)


def filter_mask(mask_subset,specdilate,masktag,filtertag,overwrite,idx):
    """
    Function called by multiprocessing pool to filter mask images for single channel islands
    """
    idx = str(idx).zfill(5)
    input_fits = mask_subset[1:1]
    template_fits = []
    output_fits = []
    exists = []
    for input_fits in mask_subset[1:-1]:
        filtered_fits = input_fits.replace(masktag,filtertag)
        template_fits.append(input_fits)
        output_fits.append(filtered_fits)
        exists.append(os.path.isfile(filtered_fits))
    if False not in exists and not overwrite:
        logging.info(f'[F{idx}] Subset is complete, skipping (overwrite disabled)')
    else:
        logging.info(f'[F{idx}] Reading subset')
        cube = load_cube(mask_subset)
        cube = cube != 0
        n_cuts = cube.shape[0]
        n_chans = cube.shape[2]
        recon_struct =  numpy.ones((3,3))
        logging.info(f'[F{idx}] Filtering image')
        for i in range(0,n_cuts):
            cut = binary_fill_holes(cube[i,:,:])
            eroded = binary_erosion(cut)
            dilated = binary_dilation(eroded, structure = recon_struct, iterations = specdilate)
            cube[i,:,:] = dilated
        for i in range(0,len(output_fits)):
            filtered_fits = output_fits[i]
            if exists[i] and not overwrite:
                logging.info(f'[F{idx}] Skipping {filtered_fits} (overwrite disabled)')   
            else:
                logging.info(f'[F{idx}] Writing {filtered_fits}')
                shutil.copyfile(template_fits[i],filtered_fits)
                flush_image(cube[:,:,i+1],filtered_fits)


def count_islands(input_fits,orig_fits,idx):
    """
    Count the number of islands in a mask to inform cleaning
    """
    idx = str(idx).zfill(5)
    input_image = get_image(input_fits)
    # ValueError: Big-endian buffer not supported on little-endian compiler
    # A scipy problem? Not seen this before with labelling...
    input_image = input_image.byteswap().newbyteorder() 
    labeled_mask_image, n_islands = label(input_image)
    orig_image = get_image(orig_fits)
    rms = numpy.std(orig_image)
    logging.info(f'[C{idx}] Clean parameters: {input_fits} {n_islands} {rms}')


def main():

    spacer()
    hello()
    spacer()

    # ------------------------------------------------------------------
    # Setup options

    parser = OptionParser(usage = '%prog [options] input_image(s)')

    parser.add_option('--threshold', 
        dest = 'threshold', 
        metavar = 'T',
        help = 'Sigma threshold for masking (default = 5.0)', 
        default = 5.0)
    parser.add_option('--boxsize', 
        dest = 'boxsize',
        metavar = 'B',
        help = 'Box size to use for background noise estimation (default = 80)', 
        default = 80)
    parser.add_option('--dilate', 
        dest = 'dilate', 
        metavar = 'D',
        help = 'Number of iterations of binary dilation in the spatial dimensions (default = 5, set to 0 to disable)', 
        default = 3)
    parser.add_option('--specdilate', 
        dest = 'specdilate', 
        metavar = 'S',
        help = 'Number of iterations of binary dilation in the spectral dimension (default = 2, set to 0 to disable, filtering must be enabled)', 
        default = 2)
    parser.add_option('--chanaverage', 
        dest = 'chanaverage', 
        metavar = 'N',
        help = 'Width sliding channel window to use when making masks (odd numbers preferred, default = 1, i.e. no averaging)', 
        default = 1)
    parser.add_option('--saveaverage',
        dest = 'saveaverage', 
        help = 'Save the result of the sliding average (default = do not save averaged image)', 
        action = 'store_true', 
        default = False)
    parser.add_option('--chanchunk', 
        dest = 'chanchunk', 
        metavar = 'M',
        help = 'Number of channels to load per worker when filtering single channel instances (default = 16)', 
        default = 16)
    parser.add_option('--nofilter', 
        dest = 'nofilter', 
        help = 'Do not filter detections for single channel instances (default = filtering enabled)', 
        action = 'store_true', 
        default = False)
    parser.add_option('--nocount',
        dest = 'nocount',
        help = 'Do not report island counts and input RMS in the log (default = report values)',
        action = 'store_true',
        default = False)
    parser.add_option('--savenoise', 
        dest = 'savenoise', 
        help = 'Enable to export noise images as FITS files (default = do not save noise images)', 
        action = 'store_true', 
        default = False)
    parser.add_option('--invert', 
        dest = 'invert', 
        help = 'Multiply images by -1 prior to masking (default = do not invert images)', 
        action = 'store_true', 
        default = False)
    parser.add_option('--opdir',
        dest = 'opdir',
        help = 'Name of folder for output products (default = auto generated)',
        default = '')
    parser.add_option('--masktag', 
        dest = 'masktag', 
        help = 'Suffix and subfolder name for mask images (default = mask)', 
        default = 'mask')
    parser.add_option('--noisetag', 
        dest = 'noisetag', 
        help = 'Suffix and subfolder name for noise images (default = noise)', 
        default = 'noise')
    parser.add_option('--averagetag',
        dest = 'averagetag', 
        help = 'Suffix and subfolder name for boxcar averaged images (default = avg)', 
        default = 'avg')
    parser.add_option('--filtertag', 
        dest = 'filtertag', 
        help = 'Suffix and subfolder name for filtered images (default = filtered)', 
        default = 'filtered')
    parser.add_option('-f', '--force',
        dest = 'overwrite', 
        help = 'Overwrite existing FITS outputs (default = do not overwrite)', 
        action = 'store_true')
    parser.add_option('-j', 
        dest = 'j',
        metavar = 'J',
        help = 'Number of worker processes (default = 24))', 
        default = 12)

    (options,args) = parser.parse_args()
    threshold = float(options.threshold)
    boxsize = int(options.boxsize)
    dilate = int(options.dilate)
    specdilate = int(options.specdilate)
    chanaverage = int(options.chanaverage)
    if chanaverage == 1:
        noaverage = True
    else:
        noaverage = False
    saveaverage = options.saveaverage
    chanchunk = int(options.chanchunk)
    nofilter = options.nofilter
    nocount = options.nocount
    savenoise = options.savenoise
    invert = options.invert
    opdir = options.opdir
    if opdir == '':
        opdir = 'pony.output.'+timestamp
    masktag = options.masktag
    noisetag = options.noisetag
    averagetag = options.averagetag
    filtertag = options.filtertag
    overwrite = options.overwrite
    j = int(options.j)
    pool = Pool(processes = j)


    # ------------------------------------------------------------------
    # Make folders for output products

    if not os.path.isdir(opdir):
        os.mkdir(opdir)
    if not os.path.isdir(opdir+'/'+masktag):
        os.mkdir(opdir+'/'+masktag)
    if savenoise and not os.path.isdir(opdir+'/'+noisetag):
        os.mkdir(opdir+'/'+noisetag)
    if saveaverage and not os.path.isdir(opdir+'/'+averagetag):
        os.mkdir(opdir+'/'+noisetag)
    if not nofilter and not os.path.isdir(opdir+'/'+filtertag):
        os.mkdir(opdir+'/'+filtertag)


    # ------------------------------------------------------------------
    # Get input FITS list

    if len(args) != 1:
        logging.error('Please specify an image pattern')
        sys.exit()
    else:
        pattern = args[0]
        fits_list = natural_sort(glob.glob('*image.fits'))
        if len(fits_list) == 0:
            logging.error('The specified pattern returns no files')
            sys.exit()
        else:
            nfits = len(fits_list)
            logging.info(f'                Number of input images : {nfits}')


    # Report options for log
    logging.info(f'            Number of worker processes : {j}')
    logging.info(f'                         Output folder : {opdir}')
    logging.info(f'                   Detection threshold : {threshold}')
    logging.info(f'                               Boxsize : {boxsize}')
    if dilate > 0:
        logging.info(f'         Spatial dilation iteration(s) : {dilate}')
    if noaverage:
        logging.info(f'                   Frequency averaging : No')
    else:
        logging.info(f'                   Frequency averaging : Yes')
        logging.info(f'           Average channels per worker : {chanaverage}')
        logging.info(f'             Sacrificial edge channels : {chanaverage//2}')
    if nofilter:
        logging.info(f'              Single channel filtering : No')
    else:
        logging.info(f'              Single channel filtering : Yes')
        logging.info(f'        Spectral dilation iteration(s) : {specdilate}')
        logging.info(f'            Filter channels per worker : {chanchunk}')
    if savenoise:
        logging.info(f'                       Save noise maps : Yes')
    else:
        logging.info(f'                       Save noise maps : No')
    if overwrite:
        logging.info(f'              Overwrite existing files : Yes')
    else:
        logging.info(f'              Overwrite existing files : No')



    # ------------------------------------------------------------------
    # Make masks

    spacer()
    t0 = time.time()

    if noaverage:
        # Make iterable arrays for starmap
        ithreshold = [threshold]*nfits
        iboxsize = [boxsize]*nfits
        idilate = [dilate]*nfits
        iinvert = [invert]*nfits
        iopdir = [opdir]*nfits
        imasktag = [masktag]*nfits
        inoisetag = [noisetag]*nfits
        ifiltertag = [filtertag]*nfits
        isavenoise = [savenoise]*nfits
        ioverwrite = [overwrite]*nfits
        idx = numpy.arange(0,nfits)
        pool.starmap(make_mask,zip(fits_list,ithreshold,iboxsize,idilate,iinvert,iopdir,imasktag,inoisetag,isavenoise,ioverwrite,idx))

    else:
        input_fits_subsets = []
        i = 0
        while i < (nfits - chanaverage):
            c0 = i
            c1 = numpy.min((i + chanaverage, nfits))
            subset = fits_list[c0:c1]
            input_fits_subsets.append(subset)
            i+=1 
        
        logging.info(f'Sliding average will result in {i} output images from {nfits} inputs')
        ithreshold = [threshold]*i
        iboxsize = [boxsize]*i
        idilate = [dilate]*i
        iinvert = [invert]*i
        iopdir = [opdir]*nfits
        imasktag = [masktag]*i
        inoisetag = [noisetag]*i
        ifiltertag = [filtertag]*i
        isavenoise = [savenoise]*i
        iaveragetag = [averagetag]*i
        isaveaverage = [saveaverage]*i
        ioverwrite = [overwrite]*i
        idx = numpy.arange(0,i)
        pool.starmap(make_averaged_mask,zip(input_fits_subsets,ithreshold,iboxsize,idilate,iinvert,iopdir,imasktag,inoisetag,isavenoise,iaveragetag,isaveaverage,ioverwrite,idx))

    t1 = time.time()
    elapsed = str(round((t1 - t0),2))
    logging.info(f'Mask making complete ({elapsed} seconds)')


    # ------------------------------------------------------------------
    # Filter masks

    if not nofilter:

        spacer()
        t0 = time.time()
        mask_list = natural_sort(glob.glob(opdir+'/'+masktag+'/*'+pattern+'*'))
        
        if len(mask_list) == 0:
            logging.error('No mask images found')
            sys.exit()

        else:
            nfits = len(mask_list)
            nchunks = nfits // chanchunk
            mask_subsets = []

            for i in range(0,nchunks):
                c0 = i*chanchunk
                c1 = (i+1)*chanchunk
                subset = mask_list[c0:c1+2]
                mask_subsets.append(subset)

            mask_subsets.append(mask_list[c1:])
            nsubsets = len(mask_subsets)
            logging.info(f'Filtering masks in {nsubsets} subsets')
            # Make iterable arrays for starmap
            ispecdilate = [specdilate]*nsubsets
            imasktag = [masktag]*nsubsets
            ifiltertag = [filtertag]*nsubsets
            ioverwrite = [overwrite]*nsubsets
            idx = numpy.arange(0,nsubsets)
            pool.starmap(filter_mask,zip(mask_subsets,ispecdilate,imasktag,ifiltertag,ioverwrite,idx))

        t1 = time.time()
        elapsed = str(round((t1 - t0),2))
        logging.info(f'Filtering complete ({elapsed} seconds)')


    # ------------------------------------------------------------------
    # Count islands

    if not nocount:

        spacer()
        t0 = time.time()
        
        orig_list = []

        if not nofilter:
            mask_list = natural_sort(glob.glob(opdir+'/'+filtertag+'/*'+pattern+'*'))
            for mask_fits in mask_list:
                orig_list.append(mask_fits.split('/')[-1].replace('.'+filtertag,''))
        else:
            mask_list = natural_sort(glob.glob(opdir+'/'+masktag+'/*'+pattern+'*'))
            for mask_fits in mask_list:
                orig_list.append(mask_fits.split('/')[-1].replace('.'+filtertag,''))

        idx = numpy.arange(0,len(mask_list))
        pool.starmap(count_islands,zip(mask_list,orig_list,idx))
        t1 = time.time()
        elapsed = str(round((t1 - t0),2))
        logging.info(f'Counting complete ({elapsed} seconds)')


    # ------------------------------------------------------------------

if __name__ == '__main__':

    main()


