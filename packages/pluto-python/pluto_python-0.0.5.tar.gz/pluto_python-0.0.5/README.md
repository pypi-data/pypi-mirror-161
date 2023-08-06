[![Documentation Status](https://readthedocs.org/projects/pluto-python/badge/?version=latest)](https://pluto-python.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/mateczentye/pluto_python/branch/master/graph/badge.svg?token=46GL89W9G9)](https://codecov.io/gh/mateczentye/pluto_python)

Ducumentation available here: https://pluto-python.readthedocs.io/en/master/

Package was made to analyse the h5 output files from PLUTO

Package works with 2D and 3D data sets. PLUTO can output 2.5D data sets which is also handled in here.
    So Grid shapes of (X, Z), (X, Y, Z) can be analysed

pluto.py: contains the data reading and sorting methods to define all the variables that are used in other sub-classes to plot or calculate with.

mhd_jet.py: contains the subclass to py3Pluto to plot MHD simulation (no B-field splitting currently) data. This includes MHD shocks, space-time diagram and power/energy/energy density plots.

tools.py: contains the functions which are non-physics related and are present for data manipulation

calculator.py: Contains all the physics related functions and relations in PLUTO units