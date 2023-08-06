# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['tublub']

package_data = \
{'': ['*']}

install_requires = \
['tablib[all]>=3.2.1,<4.0.0']

entry_points = \
{'console_scripts': ['tublub = tublub.main:cli']}

setup_kwargs = {
    'name': 'tublub',
    'version': '0.2.0',
    'description': 'Convert tabular data files with Tablib.',
    'long_description': '# tublub\n\nConvert or view tabular data files using [Tablib](https://github.com/jazzband/tablib).\nTublub is just a simple CLI wrapper around Tablib.\n\n```text\n$ tublub --list\nAvailable formats: json xlsx xls yaml csv tsv ods dbf html jira latex df rst cli\n\n$ tublub input.json\nUsername |Identifier|First name|Last name\n---------|----------|----------|---------\nbooker12 |9012      |Rachel    |Booker\ngrey07   |2070      |Laura     |Grey\njenkins46|9346      |Mary      |Jenkins\njohnson81|4081      |Craig     |Johnson\nsmith79  |5079      |Jamie     |Smith\n\n$ tublub input.json output.xlsx\n\n$ file output.xlsx\noutput.xlsx: Microsoft Excel 2007+\n\n$ tublub input.json --format csv\nUsername,Identifier,First name,Last name\nbooker12,9012,Rachel,Booker\ngrey07,2070,Laura,Grey\njenkins46,9346,Mary,Jenkins\njohnson81,4081,Craig,Johnson\nsmith79,5079,Jamie,Smith\n```\n\n## News and Changes\n\nPlease see the [changelog](CHANGELOG.md) for more details.\n',
    'author': 'Fredrik Mellström',
    'author_email': '11281108+harkabeeparolus@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/harkabeeparolus/tublub',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
