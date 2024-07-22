import glob
import os
import shutil

opdir = 'MID_r0p0_beams'

beams = sorted(glob.glob('*/beams'))

for beam in beams:
	op = opdir+'/'+beam.replace('/','_')
	print(beam,op)
	if not os.path.isdir(op): os.mkdir(op)
	ff = glob.glob(beam+'/*')
	for ii in ff:
		shutil.copyfile(ii,op+'/'+ii.split('/')[-1])
