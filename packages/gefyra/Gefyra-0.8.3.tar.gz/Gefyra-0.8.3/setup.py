# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gefyra',
 'gefyra.api',
 'gefyra.cluster',
 'gefyra.local',
 'gefyra.local.cargoimage']

package_data = \
{'': ['*']}

install_requires = \
['docker>=5.0.3,<6.0.0',
 'kubernetes>=19.15.0,<20.0.0',
 'tabulate>=0.8.10,<0.9.0']

entry_points = \
{'console_scripts': ['gefyra = gefyra.__main__:main',
                     'setversion = version:set_version']}

setup_kwargs = {
    'name': 'gefyra',
    'version': '0.8.3',
    'description': "Gefyra runs all developer machine side components of Gefyra's Kubernetes-based development infrastructure",
    'long_description': '<p align="center">\n  <img src="https://github.com/Schille/gefyra/raw/main/docs/static/img/logo.png" alt="Gefyra Logo"/>\n</p>\n\n# Gefyra\nGefyra gives Kubernetes-("cloud-native")-developers a completely new way of writing and testing their applications. \nGone are the times of custom Docker-compose setups, Vagrants, custom scrips or other scenarios in order to develop (micro-)services\nfor Kubernetes.  \n\n# Gefyra Client\nThe Gefyra client contains a library and a CLI to run Gefyra on a developmer machine. Its main tasks are installation of\nthe Gefyra Operator and the setup of the Docker network and the Cargo sidecar to prepare Gefyra\'s development \ninfrastructure. For more information please go to: https://gefyra.dev\n\n## Commands\n- `up`: setup local development infrastructure\n- `run`: deploy a new app container into the cluster\n- `bridge`: intercept the traffic to a container that\'s running in the cluster and send it to the development container\n- `unbridge`: remove active traffic intercepts and reset the cluster to its original state\n- `down`: remove Gefyra\'s development infrastructure\n- `list`: list running containers and active bridges\n- `check`: check local system dependencies \n- `version`: print the current version and exit\n\n## Run new app container in cluster\nThe Gefyra client can run a new app container in the Kubernetes cluster with `gefyra run ...`. \nA typical use case is a completely new application that doesn\'t have any deployed containers in the cluster yet.\n\nRequirements:\n- running local cluster or available remote cluster\n- `kubectl` connection to development cluster is active\n- a successful `gefyra up`\n\n## Bridge a container\nThe Gefyra client can bridge (i.e. intercept) a container that is already running in the Kubernetes cluster with `gefyra bridge`.\nThe container needs to be specified and can be any deployed container of any pod.\n\nRequirements:\n- running local cluster or available remote cluster\n- `kubectl` connection to development cluster is active\n- successful `gefyra up`\n- successful `gefyra run ...`\n\n# More Information\nFind more information and issues on Github: https://github.com/gefyrahq/gefyra',
    'author': 'Michael Schilonka',
    'author_email': 'michael@unikube.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gefyra.dev',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
