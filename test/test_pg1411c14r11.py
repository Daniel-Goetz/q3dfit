# Make quasar template
# from q3dfit.common.makeqsotemplate import makeqsotemplate
# volume = '/Users/drupke/Box Sync/q3d/pg1411/'
# outpy = volume + 'pg1411qsotemplate.npy'
# infits = volume + 'pg1411rb1.fits'
# makeqsotemplate(infits, outpy, dataext=None, dqext=None, waveext=None)

import numpy as np
from q3dfit.common.q3df import q3df
from q3dfit.common.q3da import q3da

# Dave:
initproc = np.load('/Users/drupke/specfits/gmos/pg1411/rb3/initproc.npy',
                   allow_pickle=True)
# Hadley:
# initproc = np.load('/Users/hadley/Desktop/research/q3dfit/jnb/initproc.npy',
#                    allow_pickle = "True")

q3df(initproc[()], cols=14, rows=11, quiet=False)
q3da(initproc[()], cols=14, rows=11, quiet=False)
