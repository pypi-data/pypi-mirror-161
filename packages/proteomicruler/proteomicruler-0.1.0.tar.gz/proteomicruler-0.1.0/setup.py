# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['proteomicruler']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.4.3,<2.0.0',
 'requests>=2.28.1,<3.0.0',
 'scipy>=1.9.0,<2.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'uniprotparser>=1.0.5,<2.0.0']

setup_kwargs = {
    'name': 'proteomicruler',
    'version': '0.1.0',
    'description': 'Estimate copy number from deep profile MS experiment using the Proteomic Ruler algorithm from Wiśniewski, J. R., Hein, M. Y., Cox, J. and Mann, M. (2014) A “Proteomic Ruler” for Protein Copy Number and Concentration Estimation without Spike-in Standards. Mol Cell Proteomics 13, 3497–3506.',
    'long_description': 'Proteomic Ruler\n--\n\nAn implementation of the same algorithm from Perseus `Wiśniewski, J. R., Hein, M. Y., Cox, J. and Mann, M. (2014) A “Proteomic Ruler” for Protein Copy Number and Concentration Estimation without Spike-in Standards. Mol Cell Proteomics 13, 3497–3506.` used for estimation of protein copy number from deep profile experiment.\n\n',
    'author': 'Toan K. Phung',
    'author_email': 'toan.phungkhoiquoctoan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/noatgnu/proteomicRuler',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.12',
}


setup(**setup_kwargs)
