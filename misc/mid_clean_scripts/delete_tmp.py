import glob
import os

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

for ii in xx:
	tmplist = glob.glob(ii+'/out*/SCRIPTS')
	for tmp in tmplist:
		syscall = 'rm '+tmp+'/*sh'
		os.system(syscall)
