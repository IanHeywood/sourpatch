import glob
import os

ptgs = sorted(glob.glob('*/out*'))

for ptg in ptgs:
	ff = glob.glob(ptg+'/*fits')
	nf = len(ff)
	if nf == 0:
		os.system('rm -rf '+ptg)
		print(ptg,len(ff))
