
import os
import glob


cwd = os.getcwd()
#rootdir = '/'.join(cwd.split('/')[:-1])
rootdir = cwd
sets = sorted(glob.glob(rootdir+'/*'))

#suffixes = ['psf.fits','model.fits','dirty.fits','residual.fits','image.conv.fits','image.fits']

# DO NOT USE on 0001
# 0000 ---> 0001, then 0001 --> 0002, etc. until only the final file remains
# use temporary destination folder and cp

for ss in sets:
	print(ss)
	subsets = sorted(glob.glob(ss+'/output_*'))
	for subset in subsets:
		for suffix in ['']:
			ff = sorted(glob.glob(subset+'/*.fits'))
			for ii in ff:
				os.remove(ii)

