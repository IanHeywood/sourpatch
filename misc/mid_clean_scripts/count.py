import glob

xx = sorted(glob.glob('*'))

total = 0

for dd in xx:
	yy = sorted(glob.glob(dd+'/output_*/'))
	for ee in yy:
		files = glob.glob(ee+'/*image.conv.pbcor.fits')
		count = len(files)
		print(ee,count)
		total += count

print(total)
