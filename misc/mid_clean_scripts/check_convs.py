#!/usr/bin/env python
# ian.heywood@physics.ox.ac.uk


# Requires:
# https://github.com/ludwigschwardt/katbeam
# https://pypi.org/project/scikit-ued/


import glob
import os

chunks = sorted(glob.glob('*/out*'))

cwd = os.getcwd()

for chunk in chunks:
    os.chdir(chunk)
    fitslist = []
    xx = glob.glob('*image.fits')
    for ii in xx:
        conv = ii.replace('image.fits','image.conv.fits')
        if os.path.isfile(conv):
            fitslist.append(conv)
        else:
            fitslist.append(ii)
            print(ii)
    os.chdir('../../')
