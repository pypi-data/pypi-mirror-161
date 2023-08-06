# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['canvas_api_cli']

package_data = \
{'': ['*']}

install_requires = \
['arc-cli>=7.0.0,<8.0.0',
 'requests>=2.28.1,<3.0.0',
 'result>=0.8.0,<0.9.0',
 'rich>=12.5.1,<13.0.0',
 'toml>=0.10.2,<0.11.0',
 'xdg>=5.1.1,<6.0.0']

entry_points = \
{'console_scripts': ['canvas = canvas_api_cli.cli:cli']}

setup_kwargs = {
    'name': 'canvas-api-cli',
    'version': '0.1.0',
    'description': 'Canvas LMS API wrapper',
    'long_description': '## Canvas API Wrapper\n\nThis is a CLI wrapper around the [Canvas LMS API](https://canvas.instructure.com/doc/api/index.html)\n\n## Installation\nInstallation requires Python 3.10\n\n```\n$ pip install canvas-api-cli\n```\n\n```\n$ canvas --help\n```\n\n## Configuration\nThe config file should be located at `$HOME/.config/canvas.toml`, and look something like this:\n```toml\n[instance]\ndefault="<nickname>"\n\n[instance.<nickname>]\ndomain="domain.instructure.com"\ntoken="<API TOKEN>"\n```\n\nTo test that it\'s configured properly you can execute\n\n```\n$ canvas get users/self\n```\n\nAnd confirm that the output is for your user\n\n### Canvas Instances\nEach customer or entity that Instructure deals with is given their own Canvas instance with a unique domain name. Each instance is added to your configuration like so:\n```toml\n[instance.<nickname>]\ndomain="domain.instructure.com"\ntoken="<API TOKEN>"\n```\n\nThe Canvas instance to use can then be selected when running a query\n```\n$ canvas get users/self -i <nickname>\n```\n\nIf no instance is specified then the default will be used. If the configuration does not have a default, then you must specific an instance with every query\n```toml\n[instance]\ndefault="<nickname>"\n\n[instance.<nickname>]\ndomain="domain.instructure.com"\ntoken="<API TOKEN>"\n```\n\n## Usage\nYou can query Canvas endpoints using the `query` subcommand and it\'s aliases (`get`, `post`, `put` and `delete`)\n\n```\n$ canvas get <endpoint>\n```\n\nThe `endpoint` parameter will simply be the unique part of the API url.\nFor example: The URL: `https://canvas.instructure.com/api/v1/accounts/:account_id/users` would be queried as\n```\n$ canvas get accounts/:account_id/users\n```\n### Query Parameters\nQuery Parameters are added using the `-q` option\n\n```\n$ canvas get :course_id/assignments -q include[]=submission -q all_dates=true\n```\n\n### Request Body\nThe request body for POST or PUT requests is passed in via the `-d` option\n\nEither as a JSON string:\n```\n$ canvas put courses/:course_id/assignments/:assignment_id  -d \'\n     {\n       "assignment": {\n         "name": "New Test Name"\n       }\n     }\n     \'\n```\n\nOr a filename\n```\n$ canvas put courses/:course_id/assignments/:assignment_id  -d @file.json\n```\n\n\n### Piping\nWhen you pipe the output of `canvas` to another program, syntax highlighting will not be added. This is convenient, because it allows you to pipe to other programs like `jq` very easily.\nAdditionally, any info that is not the JSON response from Canvas is written to `stderr` instead of `stdout`, so you don\'t have to worry abou those\n\nThe JSON output will still be formatted. If you want to disable all of that you can use the `--raw` flag',
    'author': 'Sean Collings',
    'author_email': 'sean.collings@atomicjolt.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
