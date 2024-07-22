import glob
import os


sets = ['COSMOS_1',
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

for ss in sets:
	subsets = sorted(glob.glob(ss+'/output_*'))
	for subset in subsets:
		for suffix in ['residual.fitted_beam.fits','residual.kernel.log','residual.target_beam.fits','model.conv.fits']:
			kernels = sorted(glob.glob(subset+'/*'+suffix))
			for ff in kernels:
				print(ff)
				os.system('rm '+ff)

