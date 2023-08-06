# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['djlint', 'djlint.formatter']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.0.1,<9.0.0',
 'colorama>=0.4.4,<0.5.0',
 'cssbeautifier>=1.14.4,<2.0.0',
 'html-tag-names>=0.1.2,<0.2.0',
 'html-void-elements>=0.1.0,<0.2.0',
 'importlib-metadata>=4.11.0,<5.0.0',
 'jsbeautifier>=1.14.4,<2.0.0',
 'pathspec>=0.9.0,<0.10.0',
 'regex>=2022.1.18,<2023.0.0',
 'tqdm>=4.62.2,<5.0.0']

extras_require = \
{':python_version < "3.11"': ['tomli>=2.0.1,<3.0.0']}

entry_points = \
{'console_scripts': ['djlint = djlint:main']}

setup_kwargs = {
    'name': 'djlint',
    'version': '1.9.4',
    'description': 'HTML Template Linter and Formatter',
    'long_description': '\n<h1 align="center">\n  <br>\n  <a href="https://www.djlint.com"><img src="https://raw.githubusercontent.com/Riverside-Healthcare/djLint/master/docs/src/static/img/icon.png" alt="djLint Logo" width="270"></a>\n  <br>\n</h1>\n<h3 align="center">🙏 Passed 100k downloads! Thank you! 🙏</h3>\n<h4 align="center">The missing formatter and linter for HTML templates.</h4>\n\n<p align="center">\n    <a href="https://twitter.com/intent/tweet?text=djLint%20%7C%20The%20missing%20formatter%20and%20linter%20for%20HTML%20templates.&url=https://djlint.com/&hashtags=djlint,html-templates,django,jinja,developers"><img alt="tweet" src="https://img.shields.io/twitter/url/http/shields.io.svg?style=social" /></a>\n    <a href="https://discord.gg/taghAqebzU">\n     <img src="https://badgen.net/discord/online-members/taghAqebzU?icon=discord&label" alt="Discord Chat">\n   </a>\n    </p>\n    <p align="center">\n   <a href="https://codecov.io/gh/Riverside-Healthcare/djlint">\n     <img src="https://codecov.io/gh/Riverside-Healthcare/djlint/branch/master/graph/badge.svg?token=eNTG721BAA" alt="Codecov Status">\n   </a>\n   <a href="https://www.codacy.com/gh/Riverside-Healthcare/djlint/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Riverside-Healthcare/djlint&amp;utm_campaign=Badge_Grade">\n     <img src="https://app.codacy.com/project/badge/Grade/dba6338b0e7a4de896b45b382574f369" alt="Codacy Status">\n   </a>\n   <a href="https://pepy.tech/project/djlint">\n     <img src="https://pepy.tech/badge/djlint" alt="Downloads">\n   </a>\n   <a href="https://www.npmjs.com/package/djlint">\n       <img alt="npm" src="https://img.shields.io/npm/dt/djlint?label=npm%20downloads">\n   </a>\n   <a href="https://pypi.org/project/djlint/">\n     <img src="https://img.shields.io/pypi/v/djlint" alt="Pypi Download">\n   </a>\n</p>\n\n<h4 align="center"><a href="https://www.djlint.com">How to use</a> • <a href="https://www.djlint.com/ru/">Как пользоваться</a> • <a href="https://www.djlint.com/fr/">Utilisation</a></h4>\n<h4 align="center">What lang are you using?</h4>\n\n<p align="center">\n   <a href="https://djlint.com/docs/languages/django/">Django</a> • <a href="https://djlint.com/docs/languages/jinja/">Jinja</a> • <a href="https://djlint.com/docs/languages/nunjucks/">Nunjucks</a> • <a href="https://djlint.com/docs/languages/twig/">Twig</a> • <a href="https://djlint.com/docs/languages/handlebars/">Handlebars</a> • <a href="https://djlint.com/docs/languages/mustach/">Mustache</a> • <a href="https://djlint.com/docs/languages/golang/">GoLang</a> • <a href="https://djlint.com/docs/languages/angular/">Angular</a>\n</p>\n\n<p align="center">\n  <img src="https://github.com/Riverside-Healthcare/djLint/blob/aa9097660d4a2e840450de5456f656c42bc7dd34/docs/src/static/img/demo-min.gif" alt="demo" width="600">\n</p>\n\n## 🤔 For What?\n\nOnce upon a time all the other programming languages had a formatter and linter. Css, javascript, python, the c suite, typescript, ruby, php, go, swift, and you know the others. The cool kids on the block.\n\nHTML templates were left out there on their own, in the cold, unformatted and unlinted :( The dirty corner in your repository. Something had to change.\n\n**djLint is a community build project to and add consistency to html templates.**\n\n## ✨ How?\n\nGrab it with `pip`\n\n```bash\npip install djlint\n```\n\n*Or with the npm experimental install - Note, this requires python and pip to be on your system path.*\n\n```bash\nnpm i djlint\n```\n\nLint your project\n\n```bash\ndjlint . --extension=html.j2 --lint\n```\nCheck your format\n\n```bash\ndjlint . --extension=html.j2 --check\n```\nFix my format!\n```bash\ndjlint . --extension=html.j2 --reformat\n```\n\n## 💙 Like it?\n\nAdd a badge to your projects ```readme.md```:\n\n```md\n[![Code style: djlint](https://img.shields.io/badge/html%20style-djlint-blue.svg)](https://www.djlint.com)\n```\n\nAdd a badge to your ```readme.rst```:\n\n```rst\n.. image:: https://img.shields.io/badge/html%20style-djlint-blue.svg\n   :target: https://www.djlint.com\n```\nLooks like this:\n\n[![djLint](https://img.shields.io/badge/html%20style-djLint-blue.svg)](https://github.com/Riverside-Healthcare/djlint)\n\n\n## 🛠️ Can I help?\n\nYes! \n\n*Would you like to add a rule to the linter?* Take a look at the [linter docs](https://djlint.com/docs/linter/) and [source code](https://github.com/Riverside-Healthcare/djLint/blob/master/src/djlint/rules.yaml)\n\n*Are you a regex pro?* Benchmark and submit a pr with improved regex for the [linter rules](https://github.com/Riverside-Healthcare/djLint/blob/master/src/djlint/rules.yaml)\n\n**⚠️ Help Needed! ⚠️** *Good with python?* djLint was an experimental project and is catching on with other devs. Help out with a rewrite of the formatter to improve speed and html style for edge cases. Contribute on the [2.0 branch](https://github.com/Riverside-Healthcare/djLint/tree/block_indent)\n\n## 🏃 Other Tools Of Note\n\n* [DjHTML](https://github.com/rtts/djhtml) A pure-Python Django/Jinja template indenter without dependencies.\n* [HTMLHint](https://htmlhint.com) Static code analysis tool you need for your HTML\n* [curlylint](https://www.curlylint.org) Experimental HTML templates linting for Jinja, Nunjucks, Django templates, Twig, Liquid\n',
    'author': 'Christopher Pickering',
    'author_email': 'cpickering@rhc.net',
    'maintainer': 'Christopher Pickering',
    'maintainer_email': 'cpickering@rhc.net',
    'url': 'https://github.com/Riverside-Healthcare/djlint',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.2,<4.0.0',
}


setup(**setup_kwargs)
