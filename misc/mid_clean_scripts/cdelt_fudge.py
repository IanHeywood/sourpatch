from astropy.io import fits
import numpy
import sys

infile =  sys.argv[1]

inphdu = fits.open(infile,mode='update')
inphdr = inphdu[0].header

inphdr.set('CDELT1',-0.00222222222222222)
inphdr.set('CDELT2',0.00222222222222222)


inphdu.flush()
