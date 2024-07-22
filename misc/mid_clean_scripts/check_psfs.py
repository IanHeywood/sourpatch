
import numpy
from astropy.io import fits
import glob
import os
from multiprocessing import Pool


def getbeam(chan):
    chan = str(chan).zfill(4)
    fitsfile = glob.glob('*/out*/*-'+chan+'-image.fits')[0]
    conv = fitsfile.replace('image.fits','image.conv.fits')
    if os.path.isfile(conv):
        fitsfile = conv
    input_hdu = fits.open(fitsfile)[0]
    hdr = input_hdu.header
    bmaj = hdr.get('BMAJ')
    bmin = hdr.get('BMIN')
    bpa = hdr.get('BPA')
    print(chan,fitsfile,bmaj,bmin,bpa)

check = []

f = open('psfs.dat','r')
line = f.readline()
while line:
    cols = line.split()
    bmaj = float(cols[2])
    if bmaj == 0.0:
        check.append(int(cols[0]))
    line = f.readline()
f.close()

#chans = numpy.arange(1,8804).tolist()
chans = check

j = 16
pool = Pool(processes = j)
pool.map(getbeam,chans)


