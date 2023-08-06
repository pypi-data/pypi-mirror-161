# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['edtools']

package_data = \
{'': ['*'], 'edtools': ['instrument/*']}

install_requires = \
['PyYAML>=5.4.1',
 'matplotlib>=3.2.1',
 'numpy>=1.18.2',
 'openpyxl>=3.0.10',
 'pandas>=1.0.3',
 'scipy>=1.4.1',
 'uncertainties>=3.1.2']

entry_points = \
{'console_scripts': ['edtools.autoindex = edtools.autoindex:main',
                     'edtools.cluster = edtools.cluster:main',
                     'edtools.extract_xds_info = edtools.extract_xds_info:main',
                     'edtools.find_beam_center = edtools.find_beam_center:main',
                     'edtools.find_cell = edtools.find_cell:main',
                     'edtools.find_rotation_axis = '
                     'edtools.find_rotation_axis:main',
                     'edtools.make_shelx = edtools.make_shelx:main',
                     'edtools.make_xscale = edtools.make_xscale:main',
                     'edtools.run_pointless = edtools.run_pointless:main',
                     'edtools.update_xds = edtools.update_xds:main']}

setup_kwargs = {
    'name': 'edtools',
    'version': '1.0.4',
    'description': 'Collection of tools for automated processing and clustering of electron diffraction data.',
    'long_description': '[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/instamatic-dev/edtools/build)](https://github.com/instamatic-dev/edtools/actions)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/edtools)](https://pypi.org/project/edtools/)\n[![PyPI](https://img.shields.io/pypi/v/edtools.svg?style=flat)](https://pypi.org/project/edtools/)\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/edtools)](https://pypi.org/project/edtools/)\n[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5727188.svg)](https://doi.org/10.5281/zenodo.5727188)\n\n# edtools\n\nCollection of tools for automated processing and clustering of batch 3-dimensional electron diffraction (3D ED) datasets.\n\n[The source for this project is available here][src].\n\n[src]: https://github.com/instamatic-dev/edtools\n\n## Installation\n\nInstall using `pip install edtools`. Installation should take less than 20 seconds on a normal desktop.\n\nFind the latest [releases](https://github.com/instamatic-dev/edtools/releases) for the versions that have been tested on.\n\n## OS Requirement\n\nWindows 10 or newer.\n\n## Software Requirements\n\n- Python 3.6+ including `numpy`, `scipy`, `matplotlib`, and `pandas` libraries\n- [`sginfo`](https://github.com/rwgk/sginfo) or [`cctbx.python`](https://cctbx.github.io/installation.html#installation) must be available on the system path for `edtools.make_shelx`\n- Access to [WSL](https://en.wikipedia.org/wiki/Windows_Subsystem_for_Linux)\n- XDS package must be installed properly under WSL\n\n## Package dependencies\n\nCheck [pyproject.toml](pyproject.toml) for the full dependency list and versions.\n\n## Documentation\n\nSee the documentation at https://edtools.readthedocs.io.\n\n## Pipeline tools\n\nAt any step, run *edtools.xxx -h* for help with possible arguments.\n\n### autoindex.py\n\nLooks for files matching `XDS.INP` in all subdirectories and runs them using `XDS`.\n\n\tIn:  XDS.INP\n\tOut: XDS data processing on all files\n\nUsage:\n\n```\nedtools.autoindex\n```\n\n### extract_xds_info.py\n\nLooks files matching `CORRECT.LP` in all subdirectories and extracts unit cell/integration info. Summarizes the unit cells in the excel file `cells.xlsx` and `cells.yaml`. XDS_ASCII.HKL files matching the completeness / CC(1/2) criteria are listed in `filelist.txt`. Optionally, gathers the corresponding `XDS_ASCII.HKL` files in the local directory. The `cells.yaml` file can be used as input for further processing.\n\n\tIn:  CORRECT.LP\n\tOut: cells.yaml\n\t     cells.xlsx\n\t     filelist.txt\n\nUsage:\n\n```\nedtools.extract_xds_info\n```\n\n### find_cell.py\n\nThis program a cells.yaml file and shows histogram plots with the unit cell parameters. This program mimicks [`CELLPARM`](http://xds.mpimf-heidelberg.mpg.de/html_doc/cellparm_program.html) and calculates the weighted mean lattice parameters, where the weight is typically the number of observed reflections (defaults to 1.0). For each lattice parameter, the mean is calculated in a given range (default range = median+-2). The range can be changed by dragging the cursor on the histogram plots.\n\nAlternatively, the unit cells can be clustered by giving the `--cluster` command, in which a dendrogram is shown. The cluster cutoff can be selected by clicking in the dendrogram. The clusters will be written to `cells_cluster_#.yaml`.\n\n\tIn:  cells.yaml\n\tOut: mean cell parameters\n\t     cells_*.yaml (clustering only)\n\nUsage:\n\n```\nedtools.find_cell cells.yaml --cluster\n```\n\n### make_xscale.py\n\nPrepares an input file `XSCALE.INP` for `XSCALE` and corresponding `XDSCONV.INP` for `XDSCONV`. Takes a `cells.yaml` file or a series of `XDS_ASCII.HKL` files as input, and uses those to generate the `XSCALE.INP` file.\n\n\tIn:  cells.yaml / XDS_ASCII.HKL\n\tOut: XSCALE.INP\n\nUsage:\n\n```\nedtools.make_xscale cells.yaml -c 10.0 20.0 30.0 90.0 90.0 90.0 -s Cmmm\n```\n\n### cluster.py\n\nParses the `XSCALE.LP` file for the correlation coefficients between reflection files to perform hierarchical cluster analysis (Giordano et al., Acta Cryst. (2012). D68, 649–658). The cutoff threshold can be selected by clicking in the dendrogram window. The program will write new `XSCALE.LP` files to subdirectories `cluster_#`, and run `XSCALE` on them, and (if available), pointless.\n\n\tIn:  XSCALE.LP\n\tOut: cluster_n/\n\t\tfilelist.txt\n\t\t*_XDS_ASCII.HKL\n\t\tXSCALE processing\n\t\tPointless processing\n\t\tshelx.hkl\n\t\tshelx.ins (optional)\n\nUsage:\n\n```\nedtools.cluster\n```\n\n\n## Helper tools\n\n### make_shelx.py\n\nCreates a shelx input file. Requires `sginfo` to be available on the system path to generate the SYMM/LATT cards.\n\n\tIn:  cell, space group, composition\n\tOut: shelx.ins\n\nUsage:\n\n```\nedtools.make_shelx -c 10.0 20.0 30.0 90.0 90.0 90.0 -s Cmmm -m Si180 O360\n```\n\n### run_pointless.py\n\nLooks for XDS_ASCII.HKL files specified in the cells.yaml, or on the command line and runs Pointless on them.\n\n\tIn:  cells.yaml / XDS_ASCII.HKL\n\tOut: Pointless processing\n\n### update_xds.py\n\nLooks files matching `CORRECT.LP` in all subdirectories, and updates the cell parameters / space group as specified.\n\n\tIn:  XDS.INP\n\tOut: XDS.INP\n\nUsage:\n\n```\nedtools.update_xds -c 10.0 20.0 30.0 90.0 90.0 90.0 -s Cmmm\n```\n\n### find_rotation_axis.py\n\nFinds the rotation axis and prints out the inputs for several programs (XDS, PETS, DIALS, Instamatic, and RED). Implements the algorithm from Gorelik et al. (Introduction to ADT/ADT3D. In Uniting Electron Crystallography and Powder Diffraction (2012), 337-347). The program reads `XDS.INP` to get information about the wavelength, pixelsize, oscillation angle, and beam center, and `SPOT.XDS` (generated by COLSPOT) for the peak positions. If the `XDS.INP` file is not specified, the program will try to look for it in the current directory.\n\n\tIn:  XDS.INP, SPOT.XDS\n\tOut: Rotation axis\n\nUsage:\n\n```\nedtools.find_rotation_axis [XDS.INP]\n```\n\n## Demo of using edtools to process batch 3D electron diffraction datasets\n\nSee the demo at https://edtools.readthedocs.io/en/latest/examples/edtools_demo.html.\n',
    'author': 'Stef Smeets',
    'author_email': 's.smeets@esciencecenter.nl',
    'maintainer': 'Stef Smeets',
    'maintainer_email': 's.smeets@esciencecenter.nl',
    'url': 'http://github.com/instamatic-dev/edtools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1',
}


setup(**setup_kwargs)
