# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ansys', 'ansys.fluent.parametric', 'ansys.fluent.parametric.local']

package_data = \
{'': ['*']}

install_requires = \
['ansys-fluent-core>=0.11.dev0,<1.0.0', 'h5py>=3.7.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.0,<5.0']}

setup_kwargs = {
    'name': 'ansys-fluent-parametric',
    'version': '0.5.dev0',
    'description': 'A python wrapper for Ansys Fluent parametric workflows',
    'long_description': 'PyFluent Parametric\n===================\n|pyansys| |pypi| |GH-CI| |MIT| |black|\n\n.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC\n   :target: https://docs.pyansys.com/\n   :alt: PyAnsys\n\n.. |pypi| image:: https://img.shields.io/pypi/v/ansys-fluent-parametric.svg?logo=python&logoColor=white\n   :target: https://pypi.org/project/ansys-fluent-parametric\n   :alt: PyPI\n\n.. |GH-CI| image:: https://github.com/pyansys/pyfluent-parametric/actions/workflows/ci_cd.yml/badge.svg\n   :target: https://github.com/pyansys/pyfluent-parametric/actions/workflows/ci_cd.yml\n   :alt: GH-CI\n\n.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg\n   :target: https://opensource.org/licenses/MIT\n   :alt: MIT\n\n.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat\n   :target: https://github.com/psf/black\n   :alt: Black\n\nOverview\n--------\nThe PyFluent Parametric project provides Pythonic access to Ansys Fluent\'s parametric\nworkflows.\n\nDocumentation and Issues\n------------------------\nPlease see the latest release `documentation <https://fluentparametric.docs.pyansys.com>`_\npage for more details.\n\nPlease feel free to post issues and other questions at `PyFluent Parametric Issues\n<https://github.com/pyansys/pyfluent-parametric/issues>`_.  This is the best place\nto post questions and code.\n\nInstallation\n------------\nThe ``ansys-fluent-parametric`` package currently supports Python 3.7 through Python\n3.10 on Windows and Linux.\n\nInstall the latest release from `PyPI\n<https://pypi.org/project/ansys-fluent-parametric/>`_ with:\n\n.. code:: console\n\n   pip install ansys-fluent-parametric\n\nAlternatively, install the latest from `pyfluent-parametric GitHub\n<https://github.com/pyansys/pyfluent-parametric>`_ via:\n\n.. code:: console\n\n   pip install git+https://github.com/pyansys/pyfluent-parametric.git\n\nIf you plan on doing local "development" of PyFluent with Git, then install\nwith:\n\n.. code:: console\n\n   git clone https://github.com/pyansys/pyfluent-parametric.git\n   cd pyfluent-parametric\n   pip install pip -U\n   pip install -e .\n\nDependencies\n------------\nYou will need a locally installed licensed copy of ANSYS to run Fluent, with the\nfirst supported version being Ansys 2022 R2.\n\nGetting Started\n---------------\n\nBasic Usage\n~~~~~~~~~~~\n\n.. code:: python\n\n   from ansys.fluent.parametric import ParametricStudy\n   study_1 = ParametricStudy(session.solver.root.parametric_studies).initialize()\n   input_parameters_update = study_1.design_points["Base DP"].input_parameters\n   input_parameters_update["inlet1_vel"] = 0.5\n   study_1.design_points["Base DP"].input_parameters = input_parameters_update\n   study_1.update_current_design_point()\n   print(study_1.design_points["Base DP"].output_parameters)\n\nAbove code assumes that a PyFluent session has already been created and a Fluent case\nwith input parameters has been set up. The `Defining Parametric Workflows\n<https://fluentparametric.docs.pyansys.com/users_guide/parametric_workflows.html>`_ in\nthe user guide has a complete example.\n\nLicense and Acknowledgments\n---------------------------\n``PyFluent Parametric`` is licensed under the MIT license.\n\nThis module, ``ansys-fluent-parametric`` makes no commercial claim over Ansys\nwhatsoever. This tool extends the functionality of ``Fluent`` by adding a Python\ninterface to the Fluent without changing the core behavior or license of the original\nsoftware.  The use of the interactive Fluent control of ``PyFluent Parametric`` requires\na legally licensed local copy of Ansys.\n\nTo get a copy of Ansys, please visit `Ansys <https://www.ansys.com/>`_.\n',
    'author': 'ANSYS, Inc.',
    'author_email': 'ansys.support@ansys.com',
    'maintainer': 'PyAnsys developers',
    'maintainer_email': 'pyansys.maintainers@ansys.com',
    'url': 'https://github.com/pyansys/pyfluent-parametric',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
