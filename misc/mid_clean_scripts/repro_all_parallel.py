import numpy
import glob
import os
import sys
from multiprocessing import Pool

def repro(img):
    wt = img.replace('pbcor.fits','wt.fits')
    op = 'repro/'+img.split('/')[-1].replace('.fits','.repro.fits')
    if not os.path.isfile(op.replace('.repro.fits','.repro_area.fits')):
        os.system('mProjectPP -w '+wt+' '+img+' '+op+' template.hdr')
    else:
        print('Skipping',op)

if __name__ == '__main__':

    j = 20

    ptg = sys.argv[1]
    fitslist = sorted(glob.glob('../'+ptg+'/output*/*pbcor.fits'))

    pool = Pool(processes=j)
    pool.map(repro,fitslist)
