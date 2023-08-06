# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pkai']

package_data = \
{'': ['*'], 'pkai': ['example/*', 'models/*']}

install_requires = \
['torch>=1.12.0,<2.0.0']

setup_kwargs = {
    'name': 'pkai',
    'version': '1.2.0',
    'description': 'A python module for flexible Poisson-Boltzmann based pKa calculations with proton tautomerism',
    'long_description': '[![PyPI version](https://badge.fury.io/py/pKAI.svg)](https://badge.fury.io/py/pKAI) [![PyPI - Downloads](https://img.shields.io/pypi/dm/pKAI)](https://badge.fury.io/py/pKAI)\n\n# pKAI\n\nA fast and interpretable deep learning approach to accurate electrostatics-driven pKa prediction\n\n```\n@article{pkai,\nauthor = {Reis, Pedro B. P. S. and Bertolini, Marco and Montanari, Floriane and Machuqueiro, Miguel and Clevert, Djork-Arné},\ntitle = {pKAI: A fast and interpretable deep learning approach to accurate electrostatics-driven pKa prediction},\nnote = {in preparation}\n}\n```\n\n### Installation & Basic Usage\n\nWe recommend installing pKAI on a conda enviroment. The pKAI+ model will be downloaded on the first execution and saved for subsequent runs.\n\n```\npython3 -m pip install pKAI\n\npKAI <pdbfile>\n```\n\nIt can also be used as python function,\n```\nfrom pKAI.pKAI import pKAI\n\npks = pKAI(pdb)\n```\nwhere each element of the returned list is a tuple of size 4. (chain, resnumb, resname, pk)\n\n## pKAI+ vs pKAI models\n\npKAI+ (default model) aims to predict experimental p<i>K</i><sub>a</sub> values from a single conformation. To do such, the interactions characterized in the input structure are given less weight and, as a consequence, the predictions are closer to the p<i>K</i><sub>a</sub> values of the residues in water. This effect is comparable to an increase in the dielectric constant of the protein in Poisson-Boltzmann models. In these models, the dielectric constant tries to capture, among others, electronic polarization and side-chain reorganization. When including conformational sampling explicitly, one should use a lower value for the dielectric constant of the protein. Likewise, one should use pKAI -- instead of pKAI+ -- as in this model there is no penalization of the interactions\' impact on the predicted p<i>K</i><sub>a</sub> values.\n\ntl;dr version\n- use pKAI+ for p<i>K</i><sub>a</sub> predictions arising from a single structure\n- use pKAI for p<i>K</i><sub>a</sub> predictions arising from multiple conformations\n\nChange the model to be used in the calculation by evoking the `model` argument:\n```\npKAI <pdbfile> --model pKAI\n```\n\n## Benchmark\n\nPerformed on 736 experimental values taken from the PKAD database<sup>1</sup>.\n\n| Method                | RMSE | MAE  | Quantile 0.9  | Error < 0.5 (%)  |\n|-----------------------|------|------|---------------|------------------|\n| Null<sup>2</sup>      | 1.09 | 0.72 |          1.51 |             52.3 |\n| PROPKA<sup>3</sup>    | 1.11 | 0.73 |          1.58 |             51.1 |\n| PypKa<sup>4</sup>     | 1.07 | 0.71 |          1.48 |             52.6 |\n| pKAI                  | 1.15 | 0.75 |          1.66 |             49.3 |\n| pKAI+                 | 0.98 | 0.64 |          1.37 |             55.0 |\n\n[1] Pahari, Swagata et al. "PKAD: a database of experimentally measured pKa values of ionizable groups in proteins." doi:<a href="https://doi.org/10.1093/database/baz024">10.1093/database/baz024</a>\n\n[2] Thurlkill, Richard L et al. “pK values of the ionizable groups of proteins.” doi:<a href="https://doi.org/10.1110/ps.051840806">10.1110/ps.051840806</a>\n\n[3] Olsson, Mats H M et al. “PROPKA3: Consistent Treatment of Internal and Surface Residues in Empirical pKa Predictions.” doi:<a href="https://doi.org/10.1021/ct100578z">10.1021/ct100578z</a>\n\n[4] Reis, Pedro B P S et al. “PypKa: A Flexible Python Module for Poisson-Boltzmann-Based pKa Calculations.” doi:<a href="https://doi.org/10.1021/acs.jcim.0c00718">10.1021/acs.jcim.0c00718</a>\n\n\n## License\n\nThis source code is licensed under the MIT license found in the LICENSE file in the root directory of this source tree.\n\n## Contacts\nPlease submit a github issue to report bugs and to request new features. Alternatively, you may <a href="pdreis@fc.ul.pt"> email the developer directly</a>.\n',
    'author': 'Pedro B.P.S. Reis',
    'author_email': 'pedro.reis@bayer.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.0,<4.0',
}


setup(**setup_kwargs)
