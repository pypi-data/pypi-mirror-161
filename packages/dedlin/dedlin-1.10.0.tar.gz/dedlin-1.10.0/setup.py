# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dedlin', 'dedlin.utils']

package_data = \
{'': ['*']}

install_requires = \
['art',
 'docopt-ng',
 'html2text',
 'icontract',
 'pydantic',
 'pygments',
 'pyspellchecker',
 'questionary',
 'requests',
 'rich',
 'textstat']

extras_require = \
{':sys_platform == "win32"': ['pywin32'], 'webapi': ['fastapi', 'uvicorn']}

entry_points = \
{'console_scripts': ['dedlin = dedlin.__main__:main']}

setup_kwargs = {
    'name': 'dedlin',
    'version': '1.10.0',
    'description': 'Line editor, edlin clone with many improvements',
    'long_description': "# dedlin\n\nDedlin is an interactive line-by-line text editor and a DSL. Line editors\nsuck, but they are easy to write and the DSL is mildly interesting.\n\nThis is not intended to be backwards compatible with anything. I have made\nchanges to make the app less user hostile, but there is a `--vim` mode\nwhere all help, warnings, feedback will be suppressed.\n\n\n## Installation\n```bash\npip install dedlin\n```\n\n## Usage\nLaunch and edit file_name.txt\n```bash\npython -m dedlin file_name.txt\n```\n\nCommand line help\n```\n> python -m dedlin --help\nDedlin.\n\nAn improved version of the edlin.\n\nUsage:\n  dedlin <file> [options]\n  dedlin (-h | --help)\n  dedlin --version\n\nOptions:\n  -h --help          Show this screen.\n  --version          Show version.\n  --macro=<macro>    Run macro file.\n  --echo             Echo commands.\n  --halt_on_error    End program on error.\n  --promptless_quit  Skip prompt on quit.\n```\n\nSample session\n```\n   _          _  _  _\n __| | ___  __| || |(_) _ _\n/ _` |/ -_)/ _` || || || ' \\\n\\__,_|\\___|\\__,_||_||_||_||_|\n\n\nEditing /home/mmartin/github/dedlin/sample.txt\n? * 1i\n1 INSERT\nControl C to exit insert mode\n?    1 :  cabbage\n?    2 :  bread\n?    3 :  carrots\n?    4 :  ghost peppers\n?    5 :  coffee\n?    6 :  tortillas\n?    7 :\n\nExiting insert mode\n\n? * SORT\n SORT\nSorted\n? * LIST\n1,6 LIST\n   1 : bread\n   2 : cabbage\n   3 : carrots\n   4 : coffee\n   5 : ghost peppers\n   6 : tortillas\n\n? * EXIT\n1,6 EXIT\n```\n\n\n# Documentation\n- [User Manual](https://github.com/matthewdeanmartin/dedlin/blob/main/docs/user_manual.md)\n- [Developer roadmap](https://github.com/matthewdeanmartin/dedlin/blob/main/docs/TODO.md)\n- [Prior Art](https://github.com/matthewdeanmartin/dedlin/blob/main/docs/prior_art.md)\n",
    'author': 'Matthew Martin',
    'author_email': 'matthewdeanmartin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/matthewdeanmartin/dedlin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
