# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sfctools',
 'sfctools.automation',
 'sfctools.bottomup',
 'sfctools.core',
 'sfctools.datastructs',
 'sfctools.gui',
 'sfctools.gui.attune',
 'sfctools.gui.attune.src',
 'sfctools.misc']

package_data = \
{'': ['*'],
 'sfctools.gui': ['attune/src/files/.gitkeep',
                  'attune/src/files/.gitkeep',
                  'attune/src/files/mystyle.css',
                  'attune/src/files/mystyle.css']}

install_requires = \
['cattrs==1.0.0',
 'graphviz>=0.19,<0.20',
 'matplotlib>=3.4,<4.0',
 'networkx>=2.6.3,<3.0.0',
 'numpy>=1.20.1,<2.0.0',
 'pandas>=1.4,<2.0',
 'pdflatex>=0.1,<0.2',
 'poetry>=1.1.6,<2.0.0',
 'pydot>=1.4,<2.0',
 'pyperclip>=1.8,<2.0',
 'pyyaml>=6.0,<7.0',
 'seaborn>=0.11.2,<0.12.0',
 'setuptools>=60.0.0,<61.0.0',
 'wheel>=0.36.2,<0.37.0']

setup_kwargs = {
    'name': 'sfctools',
    'version': '0.9.1',
    'description': 'Framework for stock-flow consistent agent-based modeling, being developed at the German Aerospace Center (DLR) for and in the scientific context of energy systems analysis, however, it is widely applicable in other scientific fields.',
    'long_description': '# sfctools - A toolbox for stock-flow consistent, agent-based models\n\nSfctools is a lightweight and easy-to-use Python framework for agent-based macroeconomic, stock-flow consistent (ABM-SFC) modeling. It concentrates on agents in economics and helps you to construct agents, helps you to manage and document your model parameters, assures stock-flow consistency, and facilitates basic economic data structures (such as the balance sheet).\n\n\n## Installation \n\nIn a terminal of your choice, type: \n\n    pip install sfctools \n\nsee https://pypi.org/project/sfctools/\n\n\n## Usage\n\n```console\nfrom sfctools import Agent,World\nclass MyAgent(Agent):\n    def __init__(self, a):\n        super().__init__(self)\n        self. = a \nmy_agent = MyAgent()\nprint(my_agent)\nprint(World().get_agents_of_type("MyAgent"))\n```\n\n\n| Author Thomas Baldauf, German Aerospace Center (DLR), Curiestr. 4 70563 Stuttgart | thomas.baldauf@dlr.de | version: 0.5 (Beta) | date: February 2022\n',
    'author': 'Thomas Baldauf, Benjamin Fuchs',
    'author_email': 'thomas.baldauf@dlr.de, benjamin.fuchs@dlr.de',
    'maintainer': 'Thomas Baldauf',
    'maintainer_email': 'thomas.baldauf@dlr.de',
    'url': 'https://gitlab.com/dlr-ve/esy/sfctools/framework',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
