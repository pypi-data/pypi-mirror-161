# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['constyle']

package_data = \
{'': ['*']}

install_requires = \
['importlib-metadata>=4.11.0,<5.0.0']

entry_points = \
{'console_scripts': ['constyle = constyle.__main__:main']}

setup_kwargs = {
    'name': 'constyle',
    'version': '1.1.0',
    'description': 'A Python library to add style to your console.',
    'long_description': '# constyle\nA Python library to add style to your console.\n\nThe name of the library comes from merging the words **CONSoLE** and **STYLE**. Also "con" means "with" in Spanish.\n\n## Installation\n\nYou can install this package with pip or conda.\n```sh\n$ pip install constyle\n```\n```sh\n$ conda install -c abrahammurciano constyle\n```\n\n## Links\n\nThe full documentation is available [here](https://abrahammurciano.github.io/python-constyle/constyle).\n\nThe source code is available [here](https://github.com/abrahammurciano/python-constyle).\n\nJoin the support Discord server [here](https://discord.gg/nUmsrhNDSs).\n\n## Usage\n\nThere are a couple of ways to use this library.\n\n### The `style` function\n\nThe simplest way is with the `style` function.\n\n```py\nfrom constyle import style, Attributes\n\nprint(style(\'Hello World\', Attributes.GREEN, Attributes.BOLD, Attributes.ON_BLUE))\n```\n\n### `Style` objects\n\nYou can also use `Style` objects to create a reusable style with any number of attributes.\n\n#### Calling a `Style` object\n\n`Style` objects are callable and take a string as input and return a styled string.\n\n```py\nwarning = Style(Attributes.YELLOW, Attributes.BOLD)\nprint(warning(\'You shall not pass!\'))\n```\n\n#### Adding `Style` objects\n\nAdding together `Style` objects will also create `Style` objects.\n\n```py\nwhisper = Attributes.GREY + Attributes.DIM + Attributes.SUPERSCRIPT\nprint(whisper(\'Fly you fools\'))\n```\n\n#### Converting `Style` objects to strings\n\n`Style` objects can be converted to strings to obtain the ANSI escape sequence for that style.\n\n```py\nwarning = Style(Attributes.YELLOW, Attributes.BOLD)\nprint(f"{warning}You shall not pass!{Attributes.RESET}")\n```\n\n### Attributes\n\nThe `Attributes` enum contains all the available ANSI attributes. You can read more about them [here](https://en.wikipedia.org/wiki/ANSI_escape_code#SGR_(Select_Graphic_Rendition)_parameters).\n\n`Attributes` are also `Style` objects, and as such, as demonstrated above, they too can be called to style a string, added together and to other `Style` objects, and converted to strings to obtain their ANSI sequence.\n\nYou\'ll find there is limited support for all the ANSI attributes among some consoles.\n\nIf you find more attributes that aren\'t provided in this enum, you can create your own by constructing a `Style` with an integer.\n\n### Nesting\n\nIn order to nest styles, you can use the `end=` keyword argument of the `style` function or the `Style` class. Usually when applying a style, the `RESET` attribute is appended to the end. This can be undesirable when nesting (see the example below).\n\n```py\nbold = Attributes.BOLD\nyellow = Attributes.YELLOW\ngreen = Attributes.GREEN\n\nprint(yellow(bold(\'This is bold and yellow\')))\nprint(green(f"This is green. {yellow(\'This is yellow.\')} This is no longer green"))\n```\n\nIn order to achieve the desired result in the above example, you would have to use the `end=` keyword argument of the `style` function. You can pass any `Style` to `end`.\n\n```py\nprint(green(f"This is green. {bold(\'This is green and bold.\', end=Attributes.NO_BOLD)} This is still green but not bold anymore"))\nprint(green(f"This is green. {yellow(\'This is yellow.\', end=green)} This is now green again"))\n```\n\n### Custom colours\n\nThe `constyle.custom_colours` module contains a few classes that can be used to create custom colours.\n\n#### RGB colours\n\nYou can create a `Style` for a custom RGB colour by using the `RGB` class. This is not well supported by all consoles.\n\n```py\nfrom constyle.custom_colours import RGB\n\nprint(style(\'This is pink\', RGB(255, 192, 203)))\n```\n\n#### 8-bit colours\n\nSome consoles support 8-bit colours. You can create a `Style` for an 8-bit colour by using the `EightBit` class, passing a single integer to it, or you can use the `EightBitRGB` class to create an 8-bit colour style as close to the RGB values as possible.\n\n## The command line interface\n\nThis package also provides a very basic command line interface to print styled strings.\n\nUse `constyle --help` to see how to use it.\n',
    'author': 'Abraham Murciano',
    'author_email': 'abrahammurciano@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/abrahammurciano/python-constyle',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
