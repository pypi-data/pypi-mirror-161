# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tanmatsu', 'tanmatsu.widgets']

package_data = \
{'': ['*']}

install_requires = \
['parsy>=1.3.0,<2.0.0', 'tri.declarative>=5.0,<6.0', 'wcwidth>=0.2,<0.3']

setup_kwargs = {
    'name': 'tanmatsu',
    'version': '0.0.1.1',
    'description': 'Declarative Terminal User Interface Library',
    'long_description': '# About\n\nDeclarative TUI (Terminal User Interface) library, with layout features modelled after modern web components.\n\nThe syntax will be familiar with anyone who\'s used Django models before. Widget objects can be created declaratively by creating a class that inherits from the desired widget class.\n\nA CSS flexbox-style widget that contains a text box and a button can be created declaratively, like so:\n\n```python\nclass NiceFlexBox(widgets.FlexBox):\n\ttext_box = widgets.TextBox(text="Hello World!")\n\tbutton = widgets.Button(label="Button 2", callback=None)\n\t\n\tclass Meta:\n\t\tborder_label = "Nice FlexBox"\n\nnice_flex_box = NiceFlexBox()\n\n```\n\nor imperatively, like so:\n\n```python\nchildren = {\n\t\'text_box\': widgets.TextBox(text="Hello World!"),\n\t\'button\': widgets.Button(label="Button 2", callback=None)\n}\n\nnice_flex_box = widgets.FlexBox(children=children, border_label="Nice FlexBox")\n\n```\n\n# Example\n\n![tanmatsu example screenshot](/screenshots/main.png)\n\nwhich is given by the code:\n\n```python\nfrom tanmatsu import Tanmatsu, widgets\n\n\nclass ButtonList(widgets.List):\n\tclass Meta:\n\t\tborder_label = "List"\n\t\tchildren = [\n\t\t\twidgets.Button(label="Button 1", callback=None),\n\t\t\twidgets.Button(label="Button 2", callback=None),\n\t\t\twidgets.Button(label="Button 3", callback=None),\n\t\t]\n\t\titem_height = 5\n\n\nclass VertSplit(widgets.FlexBox):\n\ttext_box = widgets.TextBox(border_label="Text Box", text="Hello World!")\n\ttext_log = widgets.TextLog(border_label="Text Log")\n\tbutton_list = ButtonList()\n\t\n\tclass Meta:\n\t\tflex_direction = widgets.FlexBox.HORIZONTAL\n\n\nwith Tanmatsu(title="Tanmatsu!") as t:\n\trw = VertSplit()\n\tt.set_root_widget(rw)\n\t\n\tfor (i, v) in enumerate(rw.button_list.children):\n\t\tv.callback = lambda i=i: rw.text_log.append_line(f"Button {i + 1} pressed")\n\t\n\tt.loop()\n```\n\n# Documentation\n\nhttps://tanmatsu.readthedocs.io/en/latest/\n\n# Requirements\n\n* Python >=3.11\n* GNU/Linux\n* Full-featured terminal emulator (e.g., Gnome VTE)\n\n# Dependencies\n\n* tri.declarative\n* parsy\n* sphinx\n* wcwidth\n\n# Development\n\n## Installing\n\n1. Install [pyenv](https://github.com/pyenv/pyenv) (intructions in the `README.md`)\n2. Install [pipenv](https://github.com/pypa/pipenv) with `pip3 install pipenv`\n3. Run `pipenv install` from the repository directory to set up a virtual environment with the necessary python version and packages\n\n## Running\n\n`pipenv run python3 main.py`\n\n## Testing\n\n`pipenv run python3 -m unittest`\n\n# License\n\nMIT. For more information, see `LICENSE.md`\n',
    'author': 'snowdrop4',
    'author_email': '82846066+snowdrop4@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/snowdrop4/tanmatsu',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
