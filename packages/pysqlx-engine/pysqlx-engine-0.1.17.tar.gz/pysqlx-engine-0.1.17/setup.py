# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sqlx_engine',
 'sqlx_engine._binary',
 'sqlx_engine._config',
 'sqlx_engine._core']

package_data = \
{'': ['*']}

install_requires = \
['Pygments>=2.12.0,<3.0.0',
 'aiofiles>=0.8.0,<0.9.0',
 'httpx>=0.23.0,<0.24.0',
 'pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'pysqlx-engine',
    'version': '0.1.17',
    'description': 'Python Async SQL Engines',
    'long_description': '# PySQLXEngine\n\n<p align="center">\n  <a href="/"><img src="https://carlos-rian.github.io/pysqlx-engine/img/logo-text3.png" alt="PySQLXEngine Logo"></a>\n</p>\n<p align="center">\n    <em>PySQLXEngine, a minimalist asynchronous SQL engine</em>\n</p>\n\n<p align="center">\n<a href="https://github.com/carlos-rian/pysqlx-engine/actions?query=workflow%3ATest+event%3Apush+branch%3Amain" target="_blank">\n    <img src="https://github.com/carlos-rian/pysqlx-engine/workflows/Test/badge.svg?event=push&branch=main" alt="Test">\n</a>\n<a href="https://app.codecov.io/gh/carlos-rian/pysqlx-engine" target="_blank">\n    <img src="https://img.shields.io/codecov/c/github/carlos-rian/pysqlx-engine?color=%2334D058" alt="Coverage">\n</a>\n<a href="https://pypi.org/project/pysqlx-engine" target="_blank">\n    <img src="https://img.shields.io/pypi/v/pysqlx-engine?color=%2334D058&label=pypi%20package" alt="Package version">\n</a>\n<a href="https://pypi.org/project/pysqlx-engine" target="_blank">\n    <img src="https://img.shields.io/pypi/pyversions/pysqlx-engine.svg?color=%2334D058" alt="Supported Python versions">\n</a>\n</p>\n\n---\n\n**Documentation**: <a href="https://carlos-rian.github.io/pysqlx-engine/" target="_blank">https://carlos-rian.github.io/pysqlx-engine/</a>\n\n**Source Code**: <a href="https://github.com/carlos-rian/pysqlx-engine" target="_blank">https://github.com/carlos-rian/pysqlx-engine</a>\n\n---\n\nPySQLXEngine supports the option of sending **raw sql** to your database.\n\nThe PySQLXEngine is a minimalist **Async** SQL engine. Currently this lib only supports *asynchronous programming*, you need to use `await` in all methods.\n\nDatabase Support:\n\n* `SQLite`\n* `PostgreSQL`\n* `MySQL`\n* `Microsoft SQL Server`\n\nOS Support:\n\n* `Linux`\n* `MacOS`\n* `Windows`\n\n## Installation\n\n\nPIP\n\n```console\n$ pip install pysqlx-engine\n```\n\nPoetry\n\n```console\n$ poetry add pysqlx-engine\n```\n\n\n## Example\n\n* Create `main.py` file.\n\n```python\nimport asyncio\n\nfrom sqlx_engine import SQLXEngine\n\nuri = "file:./db.db"\ndb = SQLXEngine(provider="sqlite", uri=uri)\n\nasync def main():\n    await db.connect()\n    rows = await db.query(query="select 1 as number")\n    print(rows)\n\nasyncio.run(main())\n```\n\n* Run it\n\n<div class="termy">\n\n```console\n$ python3 main.py\n\n[BaseRow(number=1)]\n```\n</div>',
    'author': 'Carlos Rian',
    'author_email': 'crian.rian@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://carlos-rian.github.io/pysqlx-engine',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
