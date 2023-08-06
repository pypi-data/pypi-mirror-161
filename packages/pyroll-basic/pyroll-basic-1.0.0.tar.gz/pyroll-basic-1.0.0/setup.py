# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['basic']
install_requires = \
['pyroll-freiberg-flow-stress>=1.1.1,<2.0.0',
 'pyroll-hensel-power-and-labour>=1.0.0,<2.0.0',
 'pyroll-hitchcock-roll-flattening>=1.0.0,<2.0.0',
 'pyroll-integral-thermal>=1.1.0,<2.0.0',
 'pyroll-wusatowski-spreading>=1.1.0,<2.0.0',
 'pyroll-zouhar-contact>=1.0.0,<2.0.0',
 'pyroll>=1.0.1,<2.0.0']

setup_kwargs = {
    'name': 'pyroll-basic',
    'version': '1.0.0',
    'description': 'A meta package for installing quickly the PyRolL core and a set of basic plugins.',
    'long_description': '# PyRolL Basic Meta Package\n\nThis package does not introduce any new functionality, it works just as a meta-package to simplify the installation of\nthe PyRolL core and a couple of basic plugins through its dependencies.\n\nThe following packages are installed alongside their own dependencies:\n\n- `pyroll`\n- `pyroll-integral-thermal`\n- `pyroll-hensel-power-and-labour`\n- `pyroll-wusatowski-spreading`\n- `pyroll-zouhar-contact`\n- `pyroll-freiberg-flow-stress`\n- `pyroll-hitchcock-roll-flattening`\n\nBy importing this package with `import pyroll.basic`, all listed packages are imported and thus registered as active\nplugins.\nThe public API of this package is the union of all those packages.\nSo with `import pyroll.basic as pr` one has access to all public APIs of those packages under one single alias.',
    'author': 'Max Weiner',
    'author_email': 'max.weiner@imf.tu-freiberg.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pyroll-project.github.io',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>3.9,<3.11',
}


setup(**setup_kwargs)
