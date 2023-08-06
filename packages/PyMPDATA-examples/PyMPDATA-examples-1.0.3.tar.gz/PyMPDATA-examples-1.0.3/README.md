[![Copyright](https://img.shields.io/static/v1?label=Copyright&color=249fe2&message=Jagiellonian%20University&)](https://en.uj.edu.pl/)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![DOI](https://zenodo.org/badge/366746474.svg)](https://zenodo.org/badge/latestdoi/366746474)

[![Github Actions Build Status](https://github.com/atmos-cloud-sim-uj/PyMPDATA-examples/workflows/tests+pypi/badge.svg?branch=main)](https://github.com/atmos-cloud-sim-uj/PyMPDATA-examples/actions)    
[![GitHub issues](https://img.shields.io/github/issues-pr/atmos-cloud-sim-uj/PyMPDATA-examples.svg?logo=github&logoColor=white)](https://github.com/atmos-cloud-sim-uj/PyMPDATA-examples/pulls?q=)
[![GitHub issues](https://img.shields.io/github/issues-pr-closed/atmos-cloud-sim-uj/PyMPDATA-examples.svg?logo=github&logoColor=white)](https://github.com/atmos-cloud-sim-uj/PyMPDATA-examples/pulls?q=is:closed)    
[![PyPI version](https://badge.fury.io/py/PyMPDATA-examples.svg)](https://pypi.org/project/PyMPDATA-examples)
[![API docs](https://img.shields.io/badge/API_docs-pdoc3-blue.svg)](https://atmos-cloud-sim-uj.github.io/PyMPDATA-examples/)


This repository stores example files for `PyMPDATA` depicting usage of `PyMPDATA` from Python via Jupyter.
For information on the `PyMPDATA` package itself and examples of usage from Julia and Matlab, 
see [PyMPDATA README.md](https://github.com/atmos-cloud-sim-uj/PyMPDATA/blob/master/README.md) file.

Please use the [PyMPDATA issue-tracking](https://github.com/atmos-cloud-sim-uj/PyMPDATA/issues) and [dicsussion](https://github.com/atmos-cloud-sim-uj/PyMPDATA/discussions) infrastructure for `PyMPDATA-examples` as well.

Each of the examples listed below can either be executed using Jupyer after downaloding it (and installing
  the PySDM-examples package using ``pip install``) or executed in the cloud by clicking on one of the
  Mybinder or Colab badges below:
 
- [Smolarkiewicz 2006](http://doi.org/10.1002/fld.1071) Figs 3,4,10,11 & 12    
  [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/atmos-cloud-sim-uj/PyMPDATA-examples.git/main?urlpath=lab/tree/PyMPDATA_examples%2FSmolarkiewicz_2006_Figs_3_4_10_11_12/demo.ipynb) 
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/atmos-cloud-sim-uj/PyMPDATA-examples/blob/main/PyMPDATA_examples/Smolarkiewicz_2006_Figs_3_4_10_11_12/demo.ipynb)    
  (1D homogeneous cases depicting infinite-gauge and flux-corrected transport cases)
- [Arabas & Farhat 2020](https://doi.org/10.1016/j.cam.2019.05.023) (1D advection-diffusion example based on Black-Scholes equation):
  - Fig 1: 
    [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/atmos-cloud-sim-uj/PyMPDATA-examples.git/main?urlpath=lab/tree/PyMPDATA_examples%2FArabas_and_Farhat_2020/fig_1.ipynb) 
    [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/atmos-cloud-sim-uj/PyMPDATA-examples/blob/main/PyMPDATA_examples/Arabas_and_Farhat_2020/fig_1.ipynb)    
  - Fig 2: 
    [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/atmos-cloud-sim-uj/PyMPDATA-examples.git/main?urlpath=lab/tree/PyMPDATA_examples%2FArabas_and_Farhat_2020/fig_2.ipynb) 
    [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/atmos-cloud-sim-uj/PyMPDATA-examples/blob/main/PyMPDATA_examples/Arabas_and_Farhat_2020/fig_2.ipynb)    
  - Fig 3:
    [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/atmos-cloud-sim-uj/PyMPDATA-examples.git/main?urlpath=lab/tree/PyMPDATA_examples%2FArabas_and_Farhat_2020/fig_3.ipynb) 
    [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/atmos-cloud-sim-uj/PyMPDATA-examples/blob/main/PyMPDATA_examples/Arabas_and_Farhat_2020/fig_3.ipynb)    
  - Tab 1:
    [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/atmos-cloud-sim-uj/PyMPDATA-examples.git/main?urlpath=lab/tree/PyMPDATA_examples%2FArabas_and_Farhat_2020/tab_1.ipynb) 
    [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/atmos-cloud-sim-uj/PyMPDATA-examples/blob/main/PyMPDATA_examples/Arabas_and_Farhat_2020/tab_1.ipynb)    
- [Olesik et al. 2022](https://doi.org/10.5194/gmd-15-3879-2022)    
  [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/atmos-cloud-simm-uj/PyMPDATA-examples.git/main?urlpath=lab/tree/PyMPDATA_examples%2FOlesik_et_al_2022/)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/atmos-cloud-sim-uj/PyMPDATA-examples/blob/main/PyMPDATA_examples/Olesik_et_al_2022/demo_make_plots.ipynb)   
  (1D particle population condensational growth problem with coordinate transformations)
- [Shipway and Hill 2012 (KiD-1D)](https://doi.org/10.1002/qj.1913) (analysis discussed in [Olesik et al. 2022](https://arxiv.org/abs/2011.14726))    
  [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/atmos-cloud-simm-uj/PyMPDATA-examples.git/main?urlpath=lab/tree/PyMPDATA_examples%2FShipway_and_Hill_2012/)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/atmos-cloud-sim-uj/PyMPDATA-examples/blob/main/PyMPDATA_examples/Shipway_and_Hill_2012/fig_1.ipynb)    
  (2D spectral-spatial problem of droplet condensational growth in a column of air)    
![animation](https://github.com/atmos-cloud-sim-uj/PyMPDATA/wiki/files/KiD-1D_PyMPDATA_n_iters=1.gif)
![animation](https://github.com/atmos-cloud-sim-uj/PyMPDATA/wiki/files/KiD-1D_PyMPDATA_n_iters=3.gif)
- Molenkamp 2D solid-body rotation test (as in [Jaruga et al. 2015](https://doi.org/10.5194/gmd-8-1005-2015), Fig. 12)    
  [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/atmos-cloud-sim-uj/PyMPDATA-examples.git/main?urlpath=lab/tree/PyMPDATA_examples%2FMolenkamp_test_as_in_Jaruga_et_al_2015_Fig_12/demo.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/atmos-cloud-sim-uj/PyMPDATA-examples/blob/main/PyMPDATA_examples/Molenkamp_test_as_in_Jaruga_et_al_2015_Fig_12/demo.ipynb)
- 1D advection-diffusion example with animation    
  [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/atmos-cloud-sim-uj/PyMPDATA-examples.git/main?urlpath=lab/tree/PyMPDATA_examples%2Fadvection_diffusion_1d/demo.ipynb) 
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/atmos-cloud-sim-uj/PyMPDATA-examples/blob/main/PyMPDATA_examples/advection_diffusion_1d/demo.ipynb)    
- 2D shallow-water equations (3D elliptic drop spreading on 2D plane under gravity example from [Jarecka et al. 2015](https://doi.org/10.1016/j.jcp.2015.02.003))   
  - Fig 6: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/atmos-cloud-sim-uj/PyMPDATA-examples.git/main?urlpath=lab/tree/PyMPDATA_examples/Jarecka_et_al_2015/fig_6.ipynb)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/atmos-cloud-sim-uj/PyMPDATA-examples/blob/main/PyMPDATA_examples/Jarecka_et_al_2015/fig_6.ipynb)
- 2D advection on a sphere (setup depicting coordinate transformation based on [Williamson and Rasch 1989](https://doi.org/10.1175/1520-0493(1989)117%3C0102:TDSLTW%3E2.0.CO;2))  
  [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/atmos-cloud-sim-uj/PyMPDATA-examples.git/main?urlpath=lab/tree/PyMPDATA_examples%2FWilliamson_and_Rasch_1989_as_in_Jaruga_et_al_2015_Fig_14/demo_over_the_pole.ipynb) 
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/atmos-cloud-sim-uj/PyMPDATA-examples/blob/main/PyMPDATA_examples/Williamson_and_Rasch_1989_as_in_Jaruga_et_al_2015_Fig_14/demo_over_the_pole.ipynb)    
![animation](https://github.com/atmos-cloud-sim-uj/PyMPDATA/wiki/files/sphere_upwind.gif) 
- 3D advection (spherical signal revolving in a box, based on [Smolarkiewicz 1984](https://doi.org/10.1016/0021-9991(84)90121-9))    
  [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/atmos-cloud-sim-uj/PyMPDATA-examples.git/main?urlpath=lab/tree/PyMPDATA_examples%2FSmolarkiewicz_1984/figs_13-14.ipynb) 
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/atmos-cloud-sim-uj/PyMPDATA-examples/blob/main/PyMPDATA_examples/Smolarkiewicz_1984/figs_13-14.ipynb)    
