# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['py_gs1_barcode_engine', 'py_gs1_barcode_engine._pyinstaller']

package_data = \
{'': ['*'], 'py_gs1_barcode_engine': ['build_artifacts/*']}

install_requires = \
['pydantic==1.9.1']

entry_points = \
{'console_scripts': ['build-c-lib = compile_and_test_lib:main']}

setup_kwargs = {
    'name': 'py-gs1-barcode-engine',
    'version': '0.0.17',
    'description': 'A thin Python wrapper of https://github.com/gs1/gs1-barcode-engine.',
    'long_description': '# GS1 Library wrapper\n\n[![Documentation Status](https://readthedocs.org/projects/gs1-barcode-engine-python-wrapper/badge/?version=latest)](https://gs1-barcode-engine-python-wrapper.readthedocs.io/en/latest/?badge=latest)\n\nA thin Python wrapper of https://github.com/gs1/gs1-barcode-engine.\n\nDocs: https://gs1-barcode-engine-python-wrapper.readthedocs.io/en/latest/\n\nPypi: https://pypi.org/project/py-gs1-barcode-engine/\n\nSource: https://bitbucket.org/stolmen/gs1-wrapper\n\n## Installation\n\n`pip install py-gs1-barcode-engine`\n\n## Example usage\n\n```\nimport py_gs1_barcode_engine\n\nINCHES_PER_MM = 0.0393701\ndpi = 157.35\nmodule_x_dim_mm = 7\nmodule_x_dim_inches = module_x_dim_mm * INCHES_PER_MM\n\nbmp_data = py_gs1_barcode_engine.generate_gs1_datamatrix(\n    "(01)94210325403182(30)2(3922)0460(93)TQ",\n    dm_rows=22,\n    dm_cols=22,\n    x_undercut=0,\n    y_undercut=0,\n    scaling={"resolution": dpi, "target_x_dim": module_x_dim_inches},\n)\n\nwith open("barcode.bmp", "wb") as f:\n    f.write(bmp_data)\n        \n```\n\n## Running tests\n\n```\npip install -r requirements.txt\npython compile_and_test_lib.py\npytest\n```\n\n\n## Packaging\n\nTo package this project, run:\n```\npoetry run build-c-lib\npoetry build\n```\n\nTo package and upload a new version of this, update the version numnber in pyproject.toml, then run\n```\n./build_and_publish.sh\n```\n\nNote that only an sdist distribution is built and uploaded. No wheel is uploaded.\n\nOutput is copied into the `dist/` folder.\n\n## License\n\nCopyright (c) 2022 Edward Ong\n\nCopyright (c) 2000-2021 GS1 AISBL\n\nLicensed under the Apache License, Version 2.0 (the "License"); you may not use\nthis library except in compliance with the License.\n\nYou may obtain a copy of the License at:\n\n<http://www.apache.org/licenses/LICENSE-2.0>\n\nUnless required by applicable law or agreed to in writing, software distributed\nunder the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR\nCONDITIONS OF ANY KIND, either express or implied. See the License for the\nspecific language governing permissions and limitations under the License.\n',
    'author': 'Edward Ong',
    'author_email': 'edward93@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1',
}


setup(**setup_kwargs)
