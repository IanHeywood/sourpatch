
import os
import glob

xx = ['COSMOS_1',
	'COSMOS_2',
	'COSMOS_3',
	'COSMOS_4',
	'J0958+0201',
	'J0958+0222',
	'J0959+0151',
	'J0959+0212',
	'J0959+0233',
	'J1000+0151',
	'J1000+0212',
	'J1000+0233',
	'J1001+0151',
	'J1001+0212',
	'J1001+0233']

#cwd = os.getcwd()
#rootdir = '/'.join(cwd.split('/')[:-1])
#rootdir = cwd
#sets = sorted(glob.glob(rootdir+'/conv_*0001*'))



for ss in xx:
	subsets = sorted(glob.glob(ss+'/output_*'))
	for subset in subsets:
		ff = sorted(glob.glob(subset+'/sequence/*.fits'))
		for ii in ff:
			syscall = 'mv '+ii+' '+subset+'/'
			print(syscall)
			os.system(syscall)
