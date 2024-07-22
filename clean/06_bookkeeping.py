import numpy
import glob
import os

cwd = os.getcwd()
rootdir = '/'.join(cwd.split('/')[:-1])
sets = sorted(glob.glob(rootdir+'/conv_*'))

suffixes = ['psf.fits','model.fits','dirty.fits','residual.fits','image.conv.fits']

# DO NOT USE on 0001
# 0000 ---> 0001, then 0001 --> 0002, etc. until only the final file remains
# use temporary destination folder and cp 

for ss in sets:
	ch0 = int(ss.split('_')[-1].split('-')[0])
	ch1 = int(ss.split('_')[-1].split('-')[1])
#	chans = numpy.arange(ch0,ch1+1)
#	print(ss,chans)
	subsets = sorted(glob.glob(ss+'/output_*'))
	for subset in subsets:
		subset_chans = []
		fitslist = sorted(glob.glob(subset+'/*image.fits'))
		for fitsfile in fitslist:
			fitschan = int(fitsfile.split('r0p0-')[-1].split('-')[0])
			subset_chans.append(fitschan)
		subset_chans = numpy.array(subset_chans)+ch0
		for i in range(0,len(fitslist)):
			newimgname = fitslist[i].split('r0p0')[0]+'r0p0-'+str(subset_chans[i]).zfill(4)+'-image.fits'
			syscall = 'mv '+fitslist[i]+' '+newimgname
			print(syscall)
			os.rename(fitslist[i],newimgname)
			for suffix in suffixes:
				ff = fitslist[i].replace('image.fits',suffix)
				if os.path.isfile(ff):
					newname = ff.split('r0p0')[0]+'r0p0-'+str(subset_chans[i]).zfill(4)+'-'+suffix
					syscall = 'mv '+ff+' '+newname
					print(syscall)
					os.rename(ff,newname)
				# else:
				# 	syscall = 'mv '
				# 	print(i,subset_chans[i],ff)

		print('')
