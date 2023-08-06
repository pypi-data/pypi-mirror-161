# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cosmoglobe',
 'cosmoglobe.data',
 'cosmoglobe.fits',
 'cosmoglobe.h5',
 'cosmoglobe.interface',
 'cosmoglobe.plot',
 'cosmoglobe.sky',
 'cosmoglobe.sky.components']

package_data = \
{'': ['*']}

install_requires = \
['astropy>=5.0.1',
 'click>=8.0.1,<9.0.0',
 'h5py>=3.0.0',
 'healpy>=1.15.2,<2.0.0',
 'numpy>=1.18,<=1.23',
 'setuptools<60.0',
 'tqdm>=4.62.3,<5.0.0']

extras_require = \
{':python_version >= "3.6" and python_version < "4"': ['cmasher>=1.6.3,<2.0.0'],
 ':python_version >= "3.8" and python_full_version < "4.0.0"': ['rich>=10.14.0,<11.0.0'],
 ':python_version >= "3.8" and python_version < "3.11"': ['numba>=0.55.1,<0.56.0'],
 ':python_version >= "3.8" and python_version < "3.12"': ['scipy>=1.9,<2.0']}

entry_points = \
{'console_scripts': ['cosmoglobe = cosmoglobe.__main__:cli']}

setup_kwargs = {
    'name': 'cosmoglobe',
    'version': '0.9.64',
    'description': 'A Python package for interfacing the Cosmoglobe Sky Model with commander3 outputs for the purpose of producing astrophysical sky maps.',
    'long_description': '\n\n<img src="imgs/Cosmoglobe-logo-horizontal-small.png">\n\n[![Documentation Status](https://readthedocs.org/projects/cosmoglobe/badge/?version=latest)](https://cosmoglobe.readthedocs.io/en/latest/?badge=latest)\n[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)\n\n<hr>\n\n*cosmoglobe* is a python package that interfaces the **Cosmoglobe Sky Model** with **[Commander](https://github.com/Cosmoglobe/Commander)** outputs for the purpose of producing astrophysical sky maps.\n\n<img src="imgs/sim.png">\n\n## Features\nSee the **[documentation](https://cosmoglobe.readthedocs.io/en/latest/)** for a more comprehensive guide.\n\n**Initialize the Cosmoglobe Sky Model (this downloads and caches a ~800 MB file with the sky model data)** \n```python\nimport cosmoglobe\n\nmodel = cosmoglobe.sky_model(nside=256)\n```\n\n**Simulate the sky at 150 GHz in units of MJy/sr, smoothed to 40 arcmin with a gaussian beam:** \n```python\nimport astropy.units as u\n\nemission = model(150*u.GHz, fwhm=40*u.arcmin, output_unit="MJy/sr")\n```\n\n**Integrate over a bandpass:** \n```python\nimport numpy as np\nimport healpy as hp\nimport matplotlib.pyplot as plt\n\n# Reading in WMAP K-band bandpass profile.\nbandpass_frequencies, bandpass_weights = np.loadtxt(wmap_bandpass.txt, unpack=True)\n\n# The units of the detector must be specified even if the bandpass is pre-normalized.\nbandpass_weights *= u.Unit("K_RJ") # Specify K_RJ or K_CMB\nbandpass_frequencies *= u.GHz\n\nmodel.remove_dipole() # Remove the dipole from the CMB component\nemission = model(\n    freqs=bandpass_frequencies, \n    weights=bandpass_weights, \n    fwhm=0.8*u.deg, \n    output_unit="mK_RJ",\n)\n\nhp.mollview(emission[0], hist="norm") # Plotting the intensity\nplt.show()\n```\n\n## Installation\n*cosmoglobe* can be installed via pip\n```bash\npip install cosmoglobe\n```\n\n## Funding\nThis work has received funding from the European Union\'s Horizon 2020 research and innovation programme under grant agreements No 776282 (COMPET-4; BeyondPlanck), 772253 (ERC; bits2cosmology) and 819478 (ERC; Cosmoglobe).\n\n<table align="center">\n    <tr>\n        <td><img src="./imgs/LOGO_ERC-FLAG_EU_.jpg" height="200"></td>\n        <td><img src="./imgs/horizon2020_logo.jpg" height="200"></td>\n    </tr>\n</table>\n\n## License\n\n[GNU GPLv3](https://github.com/Cosmoglobe/Commander/blob/master/COPYING)\n',
    'author': 'Metin San',
    'author_email': 'metinisan@gmail.com',
    'maintainer': 'Metin San',
    'maintainer_email': 'metinisan@gmail.com',
    'url': 'https://github.com/Cosmoglobe/Cosmoglobe',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
