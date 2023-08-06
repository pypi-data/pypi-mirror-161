# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['manim_meshes', 'manim_meshes.models']

package_data = \
{'': ['*'], 'manim_meshes': ['shaders/mesh/*']}

install_requires = \
['ManimPango>=0.4.1,<0.5.0',
 'decorator>=5.0.9,<6.0.0',
 'manim>=0.15.2,<0.16.0',
 'manimgl>=1.6.1,<2.0.0',
 'numpy',
 'trimesh>=3.12.5,<4.0.0']

entry_points = \
{'manim.plugins': ['manim_meshes = module:object.attr']}

setup_kwargs = {
    'name': 'manim-meshes',
    'version': '0.0.4a0',
    'description': '2D and 3D Meshes for manim for displaying and educational Purposes.',
    'long_description': '[![Python Test and Lint](https://github.com/bmmtstb/manim-meshes/actions/workflows/python_ci_test.yaml/badge.svg)](https://github.com/bmmtstb/manim-meshes/actions/workflows/python_ci_test.yaml)\n# Manim for Meshes\n\n> ⚠️ Work in progress\n> \n> Most of the code will be rearranged or changed to use OpenGL, but OpenGL is not yet used throughout manim-ce. Stay tuned.\n\nManim-Trimeshes implements manim functionalities for different types of meshes using either basic node-face data structures or for importing the python [trimesh](https://pypi.org/project/trimesh/ "trimesh on pypi") library.\n\nIt is mainly developed as a Project for Interactive Graphics Systems Group (GRIS) at TU Darmstadt, but is publicly available for everyone interested in rendering and animating meshes.\n\n## Installation\n\nIf published to pypi, can be installed using:\n\n``pip install manim-meshes``\n\n## Usage\n\n``from manim_meshes import *``\n\n[//]: #  (TODO create basic use-case with code)\n\n\n## Example\n\n[//]: # (TODO create working example + video)\n\nIn venv Run one of the minimal test examples: `manim tests/test_scene.py ConeScene`.\nMultiple other examples can be found in the `tests/test_scene.py` file.\n\n\n## Development\nSet `./src/`-folder as project sources root and `./tests/`-folder as tests sources root if necessary.\n\nActivate venv: `cd ./manim_meshes/`, then `poetry shell`\n\nInstall: `poetry install`\n\nUpdate packages and .lock file: `poetry update`\n\nIf you implemented some features, update version using poetry: `poetry version prerelease|patch|minor|major`\nSee the Poetry [Documentation](https://python-poetry.org/docs/cli/#version).\n\nEven though if CI works properly, Publish is automatically, it can be done manually with: `poetry publish --build`\n\n[//]: # (TODO decide which git to use)\n',
    'author': 'Brizar',
    'author_email': 'martin.steinborn@stud.tu-darmstadt.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bmmtstb/manim-meshes',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.0,<3.9.0',
}


setup(**setup_kwargs)
