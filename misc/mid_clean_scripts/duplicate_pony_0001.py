import glob
import os
import shutil

xx = sorted(glob.glob('*/output_*/pony.out*/filtered/*-0001-*.fits'))

for ii in xx:
	jj = ii.replace('-0001-','-0000-')
	print(ii)
	print(jj)
	print('')
	shutil.copyfile(ii,jj)
