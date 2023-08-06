# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['ast_comments']
setup_kwargs = {
    'name': 'ast-comments',
    'version': '0.1.1',
    'description': '',
    'long_description': '# ast-comments\n\nAn extension to the built-in `ast` module. \nFinds comments in source code and adds them to the parsed tree.\n\n## Installation\n```\npip install ast-comments\n```\n\n## Usage\n\nThere is no difference in usage between `ast` and `ast-comments`\n```\n>>> import ast_comments as astcom\n>>> tree = astcom.parse("hello = \'hello\' # comment to hello")\n```\nParsed tree is instance of the original ast.Module object\n```\n>>> tree\n<_ast.Module object at 0x7ffba52322e0>\n```\nAny "statement" node of the tree has `comments` field\n```\n>>> tree.body[0].comments\n(\'comment to hello\',)\n>>> astcom.dump(tree)\n"Module(body=[Assign(targets=[Name(id=\'hello\', ctx=Store())], value=Constant(value=\'hello\', kind=None), type_comment=None, comments=(\'comment to hello\',))], type_ignores=[])"\n```\n\n## Contributing\nYou are welcome to open an issue or create a pull request',
    'author': 'Dmitry Makarov',
    'author_email': 'dmtern0vnik@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/t3rn0/ast-comments',
    'py_modules': modules,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
