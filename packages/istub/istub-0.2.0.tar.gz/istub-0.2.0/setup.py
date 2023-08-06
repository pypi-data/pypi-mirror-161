# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['istub', 'istub.checks']

package_data = \
{'': ['*']}

install_requires = \
['pip', 'pyyaml']

entry_points = \
{'console_scripts': ['istub = istub.main:main']}

setup_kwargs = {
    'name': 'istub',
    'version': '0.2.0',
    'description': 'Validator for type annotations',
    'long_description': "# iStub\n\nValidator for type annotations.\n\n- [ ] Stubs generation\n- [x] Code style checking with `flake8`\n- [x] Type checking with `mypy` and `pyright`\n- [x] Type consistency checking with `mypy.stubtest`\n\n## Usage\n\n### Basic usage\n\nLet's assume that you want to check `mylib-stubs` package against `mylib`\n\nCreate a file `istub.yml` in your project root:\n\n```yaml\npackages:\n  - name: mylib\n    path: ./mylib-stubs\n    checks:\n      mypy: true\n      stubtest: true\n```\n\nRun checker:\n\n```bash\npython -m istub\n```\n\nYou can create a whitelist of acceptable errors:\n\n```bash\npython -m istub --update\n```\n\n### Custom configuration\n\n```yaml\npackages:\n  - name: mylib\n    path: ./mylib-stubs\n    checks:\n      mypy: true\n      stubtest: true\n      flake8: false\n      pyright: false\n    pip_install:\n      - pypi_dependency\n      - pypi_dependency2\n    pip_uninstall:\n      - dependency_to_uninstall\n    build:\n      - ./build_cmd.sh\n```\n\n## Latest changes\n\nFull changelog can be found in [Releases](https://github.com/youtype/istub/releases).\n\n## Versioning\n\n`istub` version follows\n[PEP 440](https://www.python.org/dev/peps/pep-0440/) format.\n\n## Support and contributing\n\nPlease reports any bugs or request new features in\n[istub](https://github.com/youtype/istub/issues/) repository.\n",
    'author': 'Vlad Emelianov',
    'author_email': 'vlad.emelianov.nz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://youtype.github.io/istub/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
