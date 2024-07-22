import glob

fitslist = sorted(glob.glob('COSMOS*fits'))

beams = []

for i in range(0,len(fitslist)):
	ia.open(fitslist[i])
	beam = ia.restoringbeam()
	beams.append((i,fitslist[i],beam))
	ia.done()

inp_cube = glob.glob('*im')[0]
ia.open(inp_cube)

for i in range(0,len(beams)):
	ia.setrestoringbeam(channel=beams[i][0],beam=beams[i][2])

ia.done()

exportfits(imagename=inp_cube,fitsimage=inp_cube.replace('.im','.fits'),dropdeg=True)