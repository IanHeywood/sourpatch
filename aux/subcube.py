import glob
import numpy
import os
import subprocess 
from astLib import astCoords as ac

# NGC 895
# start_chan = 150
# end_chan = 220
# ra = '02:21:36.1959564888'
# dec = '-05:31:10.2453452681'

#
# start_chan = 165
# end_chan = 200
# ra = '02:23:50.6385955329'
# dec = '-04:37:08.3208359710'

# Natasha's Dwarf group

# ras = ['150.8143',
# 	'150.6130',
# 	'150.4742',
# 	'150.3666',
# 	'150.1315',  
# 	'150.0243',   
# 	'149.9954',  
# 	'149.6951',   
# 	'149.6212']  

# decs = ['2.0952',  
# 	'2.1668', 
# 	'2.4137',  
# 	'2.3404',  
# 	'3.2053',  
# 	'1.9110',  
# 	'2.1096',  
# 	'2.3475',  
# 	'1.6940'] 

# start_chan = 4583
# end_chan = 4695

# Conv Test XI

start_chan = 3600
end_chan = 3699

ras = ['150.995198299',
	'150.922477393',
	'150.713911746',
	'150.003768818',
	'149.768455864',
	'149.811832855',
	'150.679694370',
	'150.347541298',
	'150.347166003',
	'150.059834028',
	'149.965460562']

decs = ['2.420996972',
	'2.426766019',
	'2.713395341',
	'2.633316171',
	'2.254567339',
	'2.192874054',
	'1.993270132',
	'1.952136219',
	'1.794087910',
	'1.866368946',
	'1.706207804']

# ra = '10:02:19.9'
# dec = '01:51:24'
# ra_d = ac.hms2decimal(ra,delimiter=':')
# dec_d = ac.dms2decimal(dec,delimiter=':')
# start_chan = 4583
# end_chan = 4695

imsize = 10.0/60.0
chans = numpy.arange(start_chan,end_chan+1)

for i in range(0,len(ras)):
	ra = ras[i]
	dec = decs[i]
	opdir = 'subcube_'+str(ra)+'_'+str(dec)
	os.mkdir(opdir)

	for chan in chans:
		chan = str(chan).zfill(4)
    	inp_fits = glob.glob('zoom4200_MID_convtest_'+chan+'.fits')[0]
		op_fits = opdir+'/subcube_'+chan+'_'+str(ra)+'_'+str(dec)+'.fits'
		op_png = op_fits.replace('.fits','.png')
		op_gif = 'subcube_'+str(ra)+'_'+str(dec)+'.gif'
		syscall = 'mSubimage -d '+inp_fits+' '+op_fits+' '+str(ra)+' '+str(dec)+' '+str(imsize)
		syscall = syscall.split()
		result = subprocess.run(syscall,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
#		os.system(syscall)
		syscall = 'mViewer -ct 0 -gray '+op_fits+' -0.0005 0.001 -out '+op_png
		syscall = syscall.split()
		result = subprocess.run(syscall,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
	os.chdir(opdir)
	syscall = 'convert-im6 -loop 0 -delay 10 *png '+op_gif
	os.system(syscall)
	os.chdir('../')