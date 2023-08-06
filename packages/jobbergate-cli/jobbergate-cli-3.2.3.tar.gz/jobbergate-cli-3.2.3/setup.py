# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jobbergate_cli',
 'jobbergate_cli.subapps',
 'jobbergate_cli.subapps.applications',
 'jobbergate_cli.subapps.clusters',
 'jobbergate_cli.subapps.job_scripts',
 'jobbergate_cli.subapps.job_submissions']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'boto3>=1.18.64,<2.0.0',
 'click>=8.0.1,<9.0.0',
 'httpx>=0.22.0,<0.23.0',
 'importlib-metadata>=4.2,<5.0',
 'inquirer>=2.7.0,<3.0.0',
 'loguru>=0.6.0,<0.7.0',
 'pendulum>=2.1.2,<3.0.0',
 'pep562>=1.1,<2.0',
 'py-buzz>=3.1.0,<4.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'pyperclip>=1.8.2,<2.0.0',
 'python-dotenv>=0.19.0,<0.20.0',
 'python-jose>=3.3.0,<4.0.0',
 'rich>=11.2.0,<12.0.0',
 'sentry-sdk>=1.4.3,<2.0.0',
 'typer>=0.4.0,<0.5.0',
 'yarl>=1.7.2,<2.0.0']

entry_points = \
{'console_scripts': ['jobbergate = jobbergate_cli.main:app']}

setup_kwargs = {
    'name': 'jobbergate-cli',
    'version': '3.2.3',
    'description': 'Jobbergate CLI Client',
    'long_description': "================\n Jobbergate CLI\n================\n\nJobbergate CLI client\n\n\n\nUsage\n-----\n\n.. code-block:: console\n\n    jobbergate --help\n\n.. note::\n\n   It is possible to use raw sbatch parameters in create-job-script\n\n   Use the `--sbatch-params` multiple times to use as many parameters as needed in the\n   following format ``--sbatch-params='-N 10'`` or\n   ``--sbatch-params='--comment=some_comment'``\n\n\nRelease Process & Criteria\n--------------------------\n\nRun automated tests\n...................\n\nRun:\n\n.. code-block:: console\n\n   make qa\n\nThis will run unit tests and linter.\n\n\nIntegration testing\n...................\n\nYou should verify that each of the functions of the CLI work as expected.\n\nFirst, prepare your environment:\n\n.. code-block:: console\n\n   JOBBERGATE_API_ENDPOINT=https://jobbergate-api-staging.omnivector.solutions\n\nThen, run the following tests:\n- ``jobbergate --version`` (confirm new version number)\n- ``create-application``\n- ``create-job-script``\n- ``create-job-submission``\n- ``update-application``\n- ``update-job-script``\n- ``update-job-submission``\n- ``list-job-submissions``\n\n(FIXME: most of the above should be covered by automated system tests.)\n\n\nCreate a release\n................\n\nFirst, decided on the scope of the release:\n* major - Significant new features added and/or there are breaking changes to the app\n* minor - New features have been added or major flaws repaired\n* patch - Minor flaws were repaired or trivial features were added\n\nNext, make the release with the selected scope:\n\n.. code-block:: console\n\n   make release-<scope>\n\nSo, for example, to create a minor release, you would run:\n\n.. code-block:: console\n\n   make relase-minor\n\nYou must have permission to push commits to the main branch to create a release.\n\nIf the release script fails, contact a maintainer to debug and fix the release.\n\n\nLicense\n-------\n* `MIT <LICENSE>`_\n\n\nCopyright\n---------\n* Copyright (c) 2020-2021 OmniVector Solutions <info@omnivector.solutions>\n",
    'author': 'Omnivector Solutions',
    'author_email': 'info@omnivector.solutions',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/omnivector-solutions/jobbergate',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
