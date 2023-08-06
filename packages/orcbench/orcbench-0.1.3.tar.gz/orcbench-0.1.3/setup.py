# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['orcbench', 'orcbench.internals']

package_data = \
{'': ['*'], 'orcbench': ['models/*']}

install_requires = \
['click>=8.1.3,<9.0.0', 'numpy>=1.23.1,<2.0.0']

setup_kwargs = {
    'name': 'orcbench',
    'version': '0.1.3',
    'description': 'OrcBench: A Representative Serverless Benchmark',
    'long_description': "\n    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣶⣧⣄⣉⣉⣠⣼⣶⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n    ⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⡿⣿⣿⣿⣿⢿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀\n    ⠀⠀⠀⠀⠀⠀⠀⣼⣤⣤⣈⠙⠳⢄⣉⣋⡡⠞⠋⣁⣤⣤⣧⠀⠀⠀⠀⠀⠀⠀\n    ⠀⢲⣶⣤⣄⡀⢀⣿⣄⠙⠿⣿⣦⣤⡿⢿⣤⣴⣿⠿⠋⣠⣿⠀⢀⣠⣤⣶⡖⠀\n    ⠀⠀⠙⣿⠛⠇⢸⣿⣿⡟⠀⡄⢉⠉⢀⡀⠉⡉⢠⠀⢻⣿⣿⡇⠸⠛⣿⠋⠀⠀\n    ⠀⠀⠀⠘⣷⠀⢸⡏⠻⣿⣤⣤⠂⣠⣿⣿⣄⠑⣤⣤⣿⠟⢹⡇⠀⣾⠃⠀⠀⠀\n    ⠀⠀⠀⠀⠘⠀⢸⣿⡀⢀⠙⠻⢦⣌⣉⣉⣡⡴⠟⠋⡀⢀⣿⡇⠀⠃⠀⠀⠀⠀\n    ⠀⠀⠀⠀⠀⠀⢸⣿⣧⠈⠛⠂⠀⠉⠛⠛⠉⠀⠐⠛⠁⣼⣿⡇⠀⠀⠀⠀⠀⠀\n    ⠀⠀⠀⠀⠀⠀⠸⣏⠀⣤⡶⠖⠛⠋⠉⠉⠙⠛⠲⢶⣤⠀⣹⠇⠀⠀⠀⠀⠀⠀\n    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⣶⣿⣿⣿⣿⣿⣿⣶⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀\n    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠛⠛⠛⠛⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀\n## OrcBench: A Representative Serverless Benchmark\nOrcBench generates a workload trace which can be consumed by serverless\nplatforms to test their service. The models used by OrcBench are modeled off of\nMicrosoft Azure and whos creation is outlined in our paper (referenced below).\n\n### Installation\n```\npip install orcbench\n```\n\n### Quick Start\n```\norcbench trace\n```\nThis will produce a standard trace (25% that of the original Microsoft\nWorkload, `--scale 0.25`). nd produces jobs which will sample for 10 models\n(`--N 10`). With a runtime (`--runtime 30`) of 30 minutes. The seed (`--seed`)\ncan be optionally set to produce deterministic workloads. The outputted\n(`--out`) trace is by default sent to `trace.out`. \n\n## Referencing Us \nIf you use this benchmark please make sure to cite us using the following citation\n\nPDF of the paper can be found - [OrcBench: A Representative Serverless Benchmark](https://rcs.uwaterloo.ca/~ryan/files/orcbench.pdf)\n\n```\n@inproceedings{hancock:benchmarking,\n  author    = {Ryan Hancock and\n               Sreeharsha Udayashankar and\n               Ali José Mashtizadeh and\n               Samer Al-Kiswany},\n  title     = {OrcBench: A Representative Serverless Benchmark},\n  booktitle = {Proceedings of the15th International Conference on Cloud Computing (CLOUD'22)}\n  publisher = {{IEEE}},\n  year      = {2022},\n  doi       = {10.1109/CLOUD55607.2022.00028},\n}\n```\n\n",
    'author': 'Ryan Hancock',
    'author_email': 'krhancoc@uwaterloo.ca',
    'maintainer': 'Ryan Hancock',
    'maintainer_email': 'krhancoc@uwaterloo.ca',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
