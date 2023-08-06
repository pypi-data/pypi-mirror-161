# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lungo']

package_data = \
{'': ['*']}

install_requires = \
['Pygments>=2.12.0,<3.0.0', 'prompt-toolkit>=3.0.30,<4.0.0']

entry_points = \
{'console_scripts': ['lungo = lungo.interpreter:main']}

setup_kwargs = {
    'name': 'lungo',
    'version': '0.1.2',
    'description': '',
    'long_description': '# Lungo Programming Language\n\n`Lungo` is a dynamic programming language created just for fun.\n\n[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/stepan-anokhin/lungo/blob/master/LICENSE)\n[![PyPI Version](https://img.shields.io/pypi/v/lungo.svg)](https://pypi.org/project/lungo/)\n[![Python Versions](https://img.shields.io/pypi/pyversions/lungo.svg)](https://pypi.org/project/lungo/)\n\n## Getting Started\n\nInstallations:\n\n```shell\npip install --upgrade lungo\n```\n\nUsage:\n\n```shell\nlungo [FILE]\n```\n\n## Syntax\n\nYou need to define variable with `let` statement before assignment/reference:\n\n```\nlet x = 2;\n```\n\nAssign a previously defined variable:\n\n```\nlet x = 0;\nx = 42;\n```\n\nDefine a function:\n\n```\nfunc inc(x) {\n    return x + 1\n}\n```\n\nThe last statement in each code block is a result of the block evaluation, so in the previous example `return` is not\nnecessary:\n\n```\nfunc inc(x) {\n  x + 1\n}\n```\n\nFunction definitions are just an expressions. The previous line is equivalent to:\n\n```\nlet inc = func(x) { x + 1 }\n```\n\nConditional execution:\n\n```\nif ( x > 0 ) {\n  print("Positive")\n} elif ( x < 0 ) {\n  print("Negative")\n} else {\n  print("X is 0")\n}\n```\n\n`while`-loop:\n\n```\nlet x = 0;\nwhile ( x < 10 ) {\n  x = x + 1;\n  print(x)\n}\n```\n\n`for`-loop:\n\n```\nfor ( x in [1,2,3] ) {\n  print(x)\n}\n```\n\nAlmost everything is expression in Lungo (except for `return` and `let` statements):\n\n```\nlet x = 10;\nlet message = if(x > 5) { "big" } else { "small" };\nprint(message)\n```\n\nOutput:\n\n```\nbig\n```\n\nAnother example:\n\n```\nfunc hello(value) {\n    print("Hello " + value)\n};\n\nlet who = "world";\n\nhello(while(who.size < 20) { who = who + " and " + who })\n```\n\nOutput:\n\n```\nHello world and world and world and world\n```\n\n**NOTE**: A bit of syntactic bitterness. In the current implementation each statement in a code block (except for the\nlast one) must be followed by a semicolon `;`. So the `;` must be present after such expressions as function\ndefinitions, `for` and `while`-loops, etc. This will be fixed in a future release.\n\nSupported binary operators: `+`, `-`, `*`, `/`, `&&`, `||`, `==`, `!=`, `>`, `>=`, `<`, `<=`\n\nUnary operators: `!`, `-`\n\nHigher order functions:\n\n```\nfunc inc(x) {\n  x + 1\n};\n\nfunc comp(f, g) {\n  func(x) {\n    f(g(x))\n  }\n}\n\nprint(comp(inc, inc)(0))\n```\n\nOutput:\n\n```\n2\n```\n\nMore sophisticated example:\n\n```\nfunc pair(a, b) {\n    func(acceptor) {\n        acceptor(a, b)\n    }\n};\n\nfunc first(p) {\n    p(func(a,b) { a })\n};\n\nfunc second(p) {\n    p(func(a,b) { b })\n};\n\nlet p = pair(1, 2);\n\nprint(first(p));\nprint(second(p));\n```\n\nOutput:\n\n```\n1\n2\n```\n',
    'author': 'Stepan Anokhin',
    'author_email': 'stepan.anokhin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/stepan-anokhin/lungo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
