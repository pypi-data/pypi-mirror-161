# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['firebirdsql_run']

package_data = \
{'': ['*']}

install_requires = \
['firebirdsql>=1.2.2,<2.0.0']

setup_kwargs = {
    'name': 'firebirdsql-run',
    'version': '1.0.1',
    'description': 'Firebirdsql wrapper inspired by subprocess.run',
    'long_description': '# firebirdsql-run\n\n> [Firebirdsql](https://github.com/nakagami/pyfirebirdsql/) wrapper inspired by [subprocess.run](https://docs.python.org/3/library/subprocess.html#subprocess.run)\n\n[![PyPI version](https://img.shields.io/pypi/v/firebirdsql-run)](https://pypi.org/project/firebirdsql-run)\n[![CI/CD](https://github.com/DeadNews/firebirdsql-run/actions/workflows/python-app.yml/badge.svg)](https://github.com/DeadNews/firebirdsql-run/actions/workflows/python-app.yml)\n[![pre-commit.ci](https://results.pre-commit.ci/badge/github/DeadNews/firebirdsql-run/main.svg)](https://results.pre-commit.ci/latest/github/DeadNews/firebirdsql-run/main)\n[![codecov](https://codecov.io/gh/DeadNews/firebirdsql-run/branch/main/graph/badge.svg?token=OCZDZIYPMC)](https://codecov.io/gh/DeadNews/firebirdsql-run)\n\n## Installation\n\n```sh\npip install firebirdsql-run\n```\n\n## Examples\n\n### Execute\n\n| maker | model | type |\n| ----- | ----- | ---- |\n| B     | 1121  | PC   |\n| A     | 1232  | PC   |\n\n```py\nresult = execute(\n    query="SELECT * FROM TABLE",\n    host="localhost",\n    db="fdb",\n    user="sysdba",\n    passwd=getenv("FB_PASSWORD"),\n)\n\nif result.returncode != 0:\n    log.error(result)\nelse:\n    log.info(result)\n```\n\n- `Info`\n\n```py\nCompletedTransaction(\n    host="localhost",\n    db="fdb",\n    user="sysdba",\n    returncode=0,\n    error="",\n    query="SELECT * FROM TABLE",\n    params=(),\n    data=[\n        {"maker": "B", "model": 1121, "type": "PC"},\n        {"maker": "A", "model": 1232, "type": "PC"},\n    ],\n)\n```\n\n- `Error`\n\n```py\nCompletedTransaction(\n    host="localhost",\n    db="fdb",\n    user="sysdba",\n    returncode=1,\n    error="Dynamic SQL Error\\nSQL error code = -204\\nTable unknown\\nTABLE\\nAt line 1, column 15\\n",\n    query="SELECT * FROM TABLE",\n    params=(),\n    data=[],\n)\n```\n\n### Reuse connection\n\n```py\nconn = connection(\n    host="localhost",\n    db="fdb",\n    user="sysdba",\n    passwd=getenv("FB_PASSWORD"),\n)\n\nexecute(use_conn=conn, query="SELECT * FROM TABLE")\n...\ncallproc(use_conn=conn, procname="PROCNAME", params=(...))\n...\n\nconn.close()\n```\n',
    'author': 'DeadNews',
    'author_email': 'uhjnnn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DeadNews/firebirdsql-run',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
