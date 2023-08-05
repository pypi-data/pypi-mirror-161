# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ecs_files_composer', 'ecs_files_composer.jinja2_filters']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'PyYAML>=6.0,<7.0',
 'boto3>=1.23.2,<2.0.0',
 'certbot-aws-store>=0.2.2,<0.3.0',
 'compose-x-common>=1.0,<2.0',
 'jsonschema>=4.5.1,<5.0.0',
 'pyOpenSSL>=22,<23',
 'pydantic[email]>=1.9.0,<2.0.0',
 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['ecs_files_composer = ecs_files_composer.cli:main',
                     'files_composer = ecs_files_composer.cli:main']}

setup_kwargs = {
    'name': 'ecs-files-composer',
    'version': '0.9.0',
    'description': 'Files and configuration handler to inject configuration files into volumes for ECS containers',
    'long_description': ".. meta::\n    :description: ECS Files Composer input config\n    :keywords: AWS, AWS ECS, Docker, Compose, docker-compose, AWS S3, AWS SSM, Secrets, Configuration\n\n===================\nECS Files Composer\n===================\n\n\n.. image:: https://img.shields.io/pypi/v/ecs_files_composer.svg\n        :target: https://pypi.python.org/pypi/ecs_files_composer\n\n\n.. image:: https://codebuild.eu-west-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiRWk3VUhxUi9peEdZRGs2cGFiTk5XM0VDK1FEQTBMN2JTdHh5b091NTVVdFd3RmpoM1lpdGkrTGtTZDJzVCt5dDBCc3Zsc0dXWHI5RHJRSG82UFJNdUJzPSIsIml2UGFyYW1ldGVyU3BlYyI6InJlYXlBWStNMDVZNEoyMnQiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=main\n\n\nWhat does it do?\n=================\n\nECS Files Composer, although can be used in EKS and other Docker context, is a small program that will allow users\nto define files they need pulled out of AWS Services, such as AWS S3 or AWS SSM Parameter Store, and load the content\nto a given location, adding builtin capabilities to set file ownership, mode, and other handy features.\n\nThe configuration of the job to perform can be written in YAML or JSON (see examples), so long as they comply to a given\nschema.\n\nWhy use it?\n============\n\nHaving your core application, when reliant on configuration files, can be tricky to start in a way that the configuration\nneeds to be pulled first and then started. This can add un-necessary complexity and logic to the application.\nAnd some docker images you might pull off the shelves from DockerHub do not necessarily allow for configuration override\nfrom environment variables.\n\nBy using a sidecar that handles all of that logic, you delegate all of these activities to it. And with the ability to define\nwhich container to start first with success criteria, you also ensure that your application won't start without the configuration\nfiles it needs.\n\n.. hint::\n\n    This app / docker image can be used in any context, locally, on-premise, with Docker, on AWS ECS / EKS or in other cloud platforms.\n\nHow to use it ?\n=================\n\n`Full official documentation <https://docs.files-composer.compose-x.io/index.html>`__\n\n\nDocker\n----------------\n\n.. code-block:: bash\n\n    docker run public.ecr.aws/compose-x/ecs-files-composer:${VERSION:-latest} -h\n    docker run -v $PWD:/ /var/tmp,:/public.ecr.aws/compose-x/ecs-files-composer:${VERSION:-latest} -f files.yaml\n\n.. attention::\n\n    The default user is root to avoid running into issues when using chmod/chown and other commands.\n    Change behaviour at your own risks.\n\n\nCLI\n------------\n\n.. code-block:: bash\n\n\n    usage: ecs_files_composer [-h] [-f FILE_PATH | -e ENV_VAR | --from-ssm SSM_CONFIG | --from-s3 S3_CONFIG] [--role-arn ROLE_ARN] [_ ...]\n\n    optional arguments:\n      -h, --help            show this help message and exit\n      -f FILE_PATH, --from-file FILE_PATH\n                            Configuration for execution from a file\n      -e ENV_VAR, --from-env-var ENV_VAR\n                            Configuration for execution is in an environment variable\n      --from-ssm SSM_CONFIG\n                            Configuration for execution is in an SSM Parameter\n      --from-s3 S3_CONFIG   Configuration for execution is in an S3\n      --role-arn ROLE_ARN   The Role ARN to use for the configuration initialization\n",
    'author': 'John Preston',
    'author_email': 'john@compose-x.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
