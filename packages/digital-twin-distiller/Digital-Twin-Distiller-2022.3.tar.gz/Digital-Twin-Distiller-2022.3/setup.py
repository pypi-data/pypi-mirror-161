# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['digital_twin_distiller',
 'digital_twin_distiller.platforms',
 'digital_twin_distiller.resources.model_template']

package_data = \
{'': ['*'],
 'digital_twin_distiller': ['resources/doc_template/*',
                            'resources/doc_template/docs/*',
                            'resources/doc_template/docs/images/*']}

install_requires = \
['Jinja2>3.0.1',
 'Shapely>1.8.0',
 'aiofiles>0.7.0',
 'ezdxf>0.16.5',
 'fastapi>0.70.0',
 'gmsh>4.8.4',
 'importlib-resources>5.4.0',
 'matplotlib>3.5.1',
 'mkdocs-git-revision-date-plugin>0.3.1',
 'mkdocs-material>7.3.6',
 'mkdocs>1.2.3',
 'mkdocstrings[python]>0.16.2',
 'networkx>2.6.3',
 'numpy>1.21.0',
 'pydantic>1.8.2',
 'pygmsh>7.1.13',
 'python-markdown-math>=0.8,<0.9',
 'requests>=2.27.1',
 'scipy>1.7.0',
 'setuptools>61.2.0',
 'svgpathtools>1.4.2',
 'uvicorn>0.15.0']

entry_points = \
{'console_scripts': ['digital-twin-distiller = '
                     'digital_twin_distiller.cli:optimize_cli']}

setup_kwargs = {
    'name': 'digital-twin-distiller',
    'version': '2022.3',
    'description': 'Python project for creating a long-lasting, encapsulated version of your numerical simulation or your machine-learning-based project.',
    'long_description': None,
    'author': 'MONTANA Knowledge Management ltd.',
    'author_email': 'info@distiller.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
