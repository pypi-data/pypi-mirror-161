# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['rich_ascii']

package_data = \
{'': ['*']}

modules = \
['NameAliases']
install_requires = \
['click>=8.1.3,<9.0.0', 'rich>=12.5.1,<13.0.0']

entry_points = \
{'console_scripts': ['ascii = rich_ascii.__main__:run']}

setup_kwargs = {
    'name': 'rich-ascii',
    'version': '0.2.0',
    'description': 'CLI tool to display the ASCII character code point information as a table.',
    'long_description': '# ascii\n\n`ascii` is small CLI tool to display information on the ASCII characters as a table.\n\nIf called with no options it will display the decimal value, hexadecimal value and name\nin 2 sets of columns (0-127 in the first and 128-255 in the second).\n\n```\nASCII Code Points\n┏━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃ Dec ┃ Hex  ┃ Name                        ┃ Dec ┃ Hex  ┃ Name                                       ┃\n┡━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩\n│ 00  │ 0x00 │ Null                        │ 128 │ 0x80 │ Padding Character                          │\n│ 01  │ 0x01 │ Start Of Heading            │ 129 │ 0x81 │ High Octet Preset                          │\n│ 02  │ 0x02 │ Start Of Text               │ 130 │ 0x82 │ Break Permitted Here                       │\n│ 03  │ 0x03 │ End Of Text                 │ 131 │ 0x83 │ No Break Here                              │\n│ 04  │ 0x04 │ End Of Transmission         │ 132 │ 0x84 │ Index                                      │\n│ 05  │ 0x05 │ Enquiry                     │ 133 │ 0x85 │ Next Line                                  │\n│ 06  │ 0x06 │ Acknowledge                 │ 134 │ 0x86 │ Start Of Selected Area                     │\n│ 07  │ 0x07 │ Alert                       │ 135 │ 0x87 │ End Of Selected Area                       │\n│ 08  │ 0x08 │ Backspace                   │ 136 │ 0x88 │ Character Tabulation Set                   │\n│ 09  │ 0x09 │ Character Tabulation        │ 137 │ 0x89 │ Character Tabulation With Justification    │\n│ 10  │ 0x0A │ Line Feed                   │ 138 │ 0x8A │ Line Tabulation Set                        │\n\n...\n\n│ 127 │ 0x7F │ Delete                      │ 255 │ 0xFF │ Latin Small Letter Y With Diaeresis        │\n└─────┴──────┴─────────────────────────────┴─────┴──────┴────────────────────────────────────────────┘\n```\n\nIf passed with the flag `--aliases` then the table will be displayed with a row for each character including a list of its aliases.\n\n```\nASCII Code Points\n┏━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃ Dec ┃ Hex  ┃ Name                                  ┃ Aliases                                       ┃\n┡━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩\n│ 00  │ 0x00 │ Null                                  │ NUL                                           │\n│ 01  │ 0x01 │ Start Of Heading                      │ SOH                                           │\n│ 02  │ 0x02 │ Start Of Text                         │ STX                                           │\n│ 03  │ 0x03 │ End Of Text                           │ ETX                                           │\n│ 04  │ 0x04 │ End Of Transmission                   │ EOT                                           │\n│ 05  │ 0x05 │ Enquiry                               │ ENQ                                           │\n│ 06  │ 0x06 │ Acknowledge                           │ ACK                                           │\n│ 07  │ 0x07 │ Alert                                 │ BEL                                           │\n│ 08  │ 0x08 │ Backspace                             │ BS                                            │\n│ 09  │ 0x09 │ Character Tabulation                  │ Horizontal Tabulation, HT, TAB                │\n│ 10  │ 0x0A │ Line Feed                             │ New Line, End Of Line, LF, NL, EOL            │\n\n...\n\n│ 255 │ 0xFF │ Latin Small Letter Y With Diaeresis   │                                               │\n└─────┴──────┴───────────────────────────────────────┴───────────────────────────────────────────────┘\n```\n\nIt also supports highlighting a specific item by passing the number to highlight either as a decimal of a hexadecimal number.\n\nYou can also control the style of the table with the following options\n\n    --style           = The style of the text\n    --title-style     = The style of the table title\n    --header-style    = The style of the table header\n    --highlight-style = The style of the highlighted row\n\nSee the [Rich dcoumentation](https://rich.readthedocs.io/en/stable/style.html) for details on how to specify a style.\n\nUses the [rich](https://rich.readthedocs.io/en/latest/) library for the fancy table formattting.\n\nThe aliases are taken from the `NameAliases.txt` file provided as part of the Unicode UCD\nand is [© 2020 Unicode®, Inc.](https://www.unicode.org/copyright.html)\n',
    'author': 'Simon Kennedy',
    'author_email': 'sffjunkie+code@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
