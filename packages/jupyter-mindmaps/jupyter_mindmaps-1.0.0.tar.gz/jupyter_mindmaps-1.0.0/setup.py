# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['jupyter_mindmaps']

package_data = \
{'': ['*'], 'jupyter_mindmaps': ['MindMaps/*', 'Templates/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0', 'requests>=2.28.1,<3.0.0', 'rich-click>=1.5.2,<2.0.0']

entry_points = \
{'console_scripts': ['jupyter_mindmaps = jupyter_mindmaps.script:run']}

setup_kwargs = {
    'name': 'jupyter-mindmaps',
    'version': '1.0.0',
    'description': 'Mindamps of Space',
    'long_description': '![Logo](/images/Jupyter.png)\n# Jupyter\n\nMind Maps of Space\n\n![Planets](images/planets.png)\n\n![People In Space](images/people.png)\n\n## Introduction \n\nUsing various APIs Jupyter collects JSON data and then uses Jinja2 templates to create markdown files. Using the markmap VS Code extension these markdown files render as mind maps! \n\n## NASA API Key \n\nPlease visit [NASA](api.nasa.gov)\n\nAnd register for an API key. Once you have your key please add it to the .env file\n\n## Setup\n\nI recommend running Jupyter in a Python virtual environment. This will help keep your host system clean and allow you to have multiple environments to try new things. If you are not using a virtual environment, start at the download/clone step below.\n\nYou will also need Python 3 and venv installed on your host system.\n\nIn your project directory, create your virtual environment\n``` console\npython3 -m venv env\n```\nActivate (use) your new virtual environment (Linux):\n``` console\nsource env/bin/activate\n```\nPip Install the package using pip install jupyter_mindmaps:\n\n``` console\n(env)pip install jupyter_mindmaps\n```\n\n## Run the code help\n\n```console\n(env)jupyter_mindmaps --help\n```\n![Help](images/help.png)\n\n## Run the code passing the key\n\n```console\n(env)jupyter_mindmaps --token { your NASA token }\n```\n## Run the code interactively\n\n```console\n(env)jupyter_mindmaps\nNASA Token: { your NASA token }\n```\n## View the Mindmaps \n\nType code . to launch VS Code in the folder \n\nInstall the markmap VS Code Extension\n\n![Mark Map](images/markmap.png)\n\nOpen the markdown file and click the "Open as markmap" \n\n## API List\nThe following files are created from the various APIs. The Space.md file contains <b>all</b> APIs. \n\n![List](/images/API_List.png)\n\nOriginal background photo credit \n[Photo](https://www.nasa.gov/audience/forstudents/k-4/dictionary/Solar_System.html)\n',
    'author': 'John Capobianco',
    'author_email': 'ptcapo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
