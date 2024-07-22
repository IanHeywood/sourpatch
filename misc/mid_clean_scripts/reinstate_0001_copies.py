import glob
import os

xx = sorted(glob.glob('*'))

rootdir = os.getcwd()

for dd in xx:
	yy = sorted(glob.glob(dd+'/output_*'))
	for ee in yy:
		if '0001-0384' in ee:
			print(ee)
			os.chdir(ee+'/copies')
			os.system('mv * ../')
			os.chdir(rootdir)
#			files = glob.glob(ee+'/copies/*image.conv.fits')
#			for file in files:
#				print(file)
