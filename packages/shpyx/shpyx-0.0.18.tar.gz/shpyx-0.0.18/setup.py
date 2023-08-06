# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['shpyx']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'shpyx',
    'version': '0.0.18',
    'description': 'Simple, clean and modern library for executing shell commands in Python',
    'long_description': '<p align="center">\n  <img src="![alt text](https://github.com/Apakottur/shpyx/blob/main/shpyx.png?raw=true)" />\n</p>\n\n[![PyPI](https://img.shields.io/pypi/v/shpyx?logo=pypi&logoColor=white&style=for-the-badge)](https://pypi.org/project/shpyx/)\n[![Downloads](https://img.shields.io/pypi/dm/shpyx?logo=pypi&logoColor=white&style=for-the-badge)](https://pypi.org/project/shpyx/)\n[![Python](https://img.shields.io/pypi/pyversions/shpyx?logo=pypi&logoColor=white&style=for-the-badge)](https://pypi.org/project/shpyx/)\n\n**shpyx** is a simple, clean and modern library for executing shell commands in Python.\n\nUse `shpyx.run` to run a shell command in a subprocess:\n\n```python\n>>> import shpyx\n>>> shpyx.run("echo 1").return_code\n0\n>>> shpyx.run("echo 1").stdout\n\'1\\n\'\n>>> shpyx.run("echo 1").stderr\n\'\'\n>>> shpyx.run("echo 1")\nShellCmdResult(cmd=\'echo 1\', stdout=\'1\\n\', stderr=\'\', all_output=\'1\\n\', return_code=0)\n```\n\n## Installation\n\nInstall with `pip`:\n\n```shell\npip install shpyx\n```\n\n## Usage examples\n\nRun a command:\n\n```python\n>>> import shpyx\n>>> shpyx.run("echo \'Hello world\'")\nShellCmdResult(cmd="echo \'Hello world\'", stdout=\'Hello world\\n\', stderr=\'\', all_output=\'Hello world\\n\', return_code=0)\n```\n\nRun a command and print live output:\n\n```python\n>>> shpyx.run("echo \'Hello world\'", log_output=True)\nHello world\nShellCmdResult(cmd="echo \'Hello world\'", stdout=\'Hello world\\n\', stderr=\'\', all_output=\'Hello world\\n\', return_code=0)\n```\n\n## Motivation\n\nI\'ve been writing automation scripts for many years, mostly in Bash.\n\nI love Bash scripts, but in my opinion they become extremely hard to read, maintain and reason about once they grow\ntoo big. I find Python to be a much more pleasant tool for "gluing" together pieces of a project and external Bash\ncommands.\n\nHere are things that one might find nicer to do in Python than in bare Bash:\n\n1. String/list manipulation\n2. Error handling\n3. Flow control (loops and conditions)\n4. Output manipulation\n\nThe Python standard library provides the excellent [subprocess module](https://docs.python.org/3/library/subprocess.html)\n, which can be used to run bash commands through Python:\n\n```python\nimport subprocess\n\ncmd = "ls -l"\np = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)\ncmd_stdout, cmd_stderr = p.communicate()\n```\n\nIt\'s great for a very simple, single command, but becomes a bit tedious to use in more complex scenarios, when\none or more of the following is needed:\n\n- Run many commands\n- Inspect the return code\n- See live command output (while it is being run)\n- Gracefully handle commands that are stuck (due to blocking I/O, for example)\n- Add formatted printing of every executed command and/or its output\n\nThis often leads to each project having their own "run" function, which encapsulates `subprocess.Popen`.\n\nThis library aims to provide a simple, typed and configurable `run` function, dealing with all the caveats of using\n`subprocess.Popen`.\n\n## Security\n\nEssentially, `shpyx` is a wrapper around `subprocess.Popen`.\nThe call to `subprocess.Popen` uses `shell=True` which means that an actual system shell is being\ncreated, and the subprocess has the permissions of the main Python process.\n\nIt is therefore not recommended running untrusted commands via `shpyX`.\n\nFor more info, see [security considerations](https://docs.python.org/3/library/subprocess.html#security-considerations).\n',
    'author': 'Yossi Rozantsev',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Apakottur/shpyx',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
