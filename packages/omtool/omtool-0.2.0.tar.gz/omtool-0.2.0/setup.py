# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['omtool',
 'omtool.actions_after',
 'omtool.actions_before',
 'omtool.core',
 'omtool.core.configs',
 'omtool.core.creation',
 'omtool.core.datamodel',
 'omtool.core.integrators',
 'omtool.core.models',
 'omtool.core.tasks',
 'omtool.core.utils',
 'omtool.io_service',
 'omtool.visualizer']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'amuse-framework>=2022.6.0,<2023.0.0',
 'astropy>=5.1,<6.0',
 'marshmallow-jsonschema>=0.13.0,<0.14.0',
 'marshmallow>=3.17.0,<4.0.0',
 'matplotlib>=3.5.2,<4.0.0',
 'numpy>=1.23.1,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pyzerolog>=0.3.0,<0.4.0']

extras_require = \
{'tasks': ['py-expression-eval>=0.3.14,<0.4.0']}

setup_kwargs = {
    'name': 'omtool',
    'version': '0.2.0',
    'description': 'Package and program that models N-Body problem in galactic evolution application.',
    'long_description': "Open Modeling Tool\n***********************\n\nDescription\n###############\nOMT (Open Modeling Tool) is used to numerically solve and visualize N-body problem with huge number of particles. Primary application is galactic evolution. \n\nPrerequisites\n###############\nIt requires following packages to work:\n\n.. code-block:: bash\n\n   pip install marshmallow marshmallow_jsonschema matplotlib pandas pyyaml argparse astropy py_expression_eval amuse-framework\n\nYou also need to install `pyfalcon <https://github.com/GalacticDynamics-Oxford/pyfalcon>`__ module which makes integration possible.\n\nYou might also need:\n\n.. code-block:: bash\n\n   pip install flake8 isort mypy black types-pyyaml\n\nUsage\n###############\nProgram has three modes: creation, integration and analysis. The semantical difference between them is as follows:\n\n* ``[data -> Snapshot]`` Creation mode creates snapshot from data. This data might be particles specified by their position, velocity and mass or the whole files with particle parameters inside them. \n* ``[Snapshot -> Snapshot]`` Integration mode alters existing snapshot. It takes some existing snapshot and performs some operation on it, then takes result and performs operation again and again until some specified condition is not met. \n* ``[Snapshot -> data]`` Analysis mode creates data from snapshot. It takes some snapshot and extracts some data (position, velocities, potentials, energies, etc.) then saves it to some form of file (image or log file).\n\nCreation\n==============\nThis module is responsible for initialization of snapshots. You can create `configuration YAML file <https://github.com/Kraysent/OMTool/blob/main/examples/creation_config.yaml>`__ which describes list of objects in the snapshot (single objects and ``*.csv`` files are supported for now).\n\nThe output is single FITS file which has two HDUs: empty primary one (it is required by FITS standard) and binary table with positions, velocities and masses of each particle in the system. It also stores timestamp T = 0 in the header. \n\nYou can start it with\n\n.. code-block:: bash\n\n   python main.py create /path/to/config/file.yaml\n\nIntegration\n==============\nThis module is responsible for actual integration of the model from previous module. It operates similarly: you create `configuration file <https://github.com/Kraysent/OMTool/blob/main/examples/integration_config.yaml>`__ with all the data necessary. Next step is to launch \n\n.. code-block:: bash\n\n   python main.py integrate /path/to/config/file.yaml\n\nIt will print some info into console and gradually produce output FITS file. Each HDU of this file would contain timestamp in the ``TIME`` header and table with fields ``[x, y, z, vx, vy, vz, m]``. Be aware that depending on number of particles it can take quite a lot of disk space.\n\nAnalysis\n==============\n\nThis module is responsible for the visualization of file with snapshots (for example, one from previous module). As always, you should create `configuration file <https://github.com/Kraysent/OMTool/blob/main/examples/analysis_config.yaml>`__. The biggest part of it is description of matplotlib's plots layout. Launch command:\n\n.. code-block:: bash\n\n   python main.py analize /path/to/config/file.yaml\n\nIf done right it should produce a lot of pictures (the same amount as number of timestamps in the input file) similar to this one: \n\n.. image:: docs/source/images/image.png\n\n**This program is under heavy development so some things (or all of them) might work not as expected or not work at all.**",
    'author': 'Artyom Zaporozhets',
    'author_email': 'kraysent@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Kraysent/OMTool',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
