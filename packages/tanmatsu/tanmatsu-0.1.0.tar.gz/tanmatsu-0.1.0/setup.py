# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tanmatsu', 'tanmatsu.widgets']

package_data = \
{'': ['*']}

install_requires = \
['parsy>=1.3.0,<1.4.0', 'tri.declarative>=5.0,<6.0', 'wcwidth>=0.2,<0.3']

setup_kwargs = {
    'name': 'tanmatsu',
    'version': '0.1.0',
    'description': 'Declarative Terminal User Interface Library',
    'long_description': '```haskell\n      :~^:.             :YJ?!                            .Y&J?^                 \n      %@@P!     :GG&!   ~@@&:   .PGP?                     B@&~.                 \n      !@@%      :&@J    ^@@?    .#@B.                     G@#            ^!.    \n      !@@%  !^  :&@?    ^@@?     #@G     :%~~~~~~~~~~~~~~^B@#~^~~~~~~~~~Y@@#Y^  \n ~?!!!J@@Y~Y&&P^.&@&~!!!?&@&!!!!!&@B     :!!~~~~~~~~~~~~~~B@&~~~~~~~~~~~~~~~!^  \n :~^:^::::%Y?%~.:@@J::::::::::::^PBY                      G@#                   \n  :&      &@@?:.:%%: ..     .... ^PG?:                    G@#         .?~       \n   PG     B@&  JJ%%%%%%?B#G?%%%%%J&&&J:     ^?!!~~~~~~~~~~B@&!~~~~~~~%B@@B%.    \n   ~@P   :@&:          %@B^                 .!~^^^^^^^^^P@@@&G!^^^^^^^^^^^~.    \n   .#@?  ?@J   :&?^:::^#&:.:..::::JP?^                :G@G#@#~P%                \n    P@G  G#.   .&@P!!%#@Y!!Y&#%!!%@@&%              .Y@&? G@# :PB!              \n    Y@! ^&~  ::.#@J  .&@%  !@&.   #@%             .J&&J.  G@#.  %##J:           \n    ..  YB%??!..#@J  .#@%  %@&.  .#@%           ^Y#B%.    G@#.   .?#@G?^.       \n  .^!?&GGJ!:   .#@J  .#@%  %@&.  .#@%        .%PBY^       B@#.     .%G@@#PJ!~^. \n.P&&#&%^       .&@J  .&@%  %@&:   #@%     .~J&J~          B@#.        ^JB@@@#J^ \n ~#!           :&@J  .&@?  ?@@^~!%&@%    ^?!^            .#@&.           :!J^   \n               :#&?   ?J^  ^J?..:P#P!                     B@#:                  \n ^GGGGGG^   %P~ ..  %P!  ?P^   ?Y~   .Y&:     ?P^   ?GGGGGG:. ^YPPJ^   .&Y  %P~ \n .~!@@%~:  .&@G     B@@~ P@!   G@L:  Y@@~    :@@P   ^~&G&~^  !@B~!&@^  :B&. &B% \n    #&.    J@%@~    B@@#.&@!   G@@A /@@@~    Y@@%.   Y@%    !@G^. ^/   :B#. &B% \n   .#&:   .&!^&G    B@Y&.P@!   G@#B@&PG@~   :@<^G%    Y@%     \\&BBG%   :B#. &B% \n   .#&:   J@! #@~   B@!!@@@!   G@^\\J@^G@~   Y@! &@:   Y@%    .:  .B@~  :B#  &B% \n   .&@:  .&&%%?@G   B@% J@@!   G@~ ^/ G@~  :@#%^J@%   Y@%    %@P~~J@^  .#B%~B@~ \n   .PP.  !B?   &G:  ?B~  &G~   YG^    YG^  %B%   &P.  !B?     %PBG&~    :YGBP!  \n```\n\n# About\n\nDeclarative TUI (Terminal User Interface) library, with layout features modelled after modern web components.\n\nWidget objects can be created by defining a class that inherits from the desired widget class.\n\nFor example, a CSS flexbox-style widget that contains a text box and a button can be created declaratively, like so:\n\n```python\nclass NiceFlexBox(widgets.FlexBox):\n    text_box = widgets.TextBox(text="Hello World!")\n    button   = widgets.Button(label="Button 2", callback=None)\n    \n    class Meta:\n        border_label = "Nice FlexBox"\n\nnice_flex_box = NiceFlexBox()\n\n```\n\nor imperatively, like so:\n\n```python\nchildren = {\n    \'text_box\': widgets.TextBox(text="Hello World!"),\n    \'button\':   widgets.Button(label="Button 2", callback=None)\n}\n\nnice_flex_box = widgets.FlexBox(children=children, border_label="Nice FlexBox")\n\n```\n\nTanmatsu supports either style. The declarative syntax should be familiar with anyone who\'s used Django models before.\n\n# Example\n\n![tanmatsu example screenshot](/screenshots/main.png)\n\nwhich is given by the code:\n\n```python\nfrom tanmatsu import Tanmatsu, widgets\n\nclass ButtonList(widgets.List):\n    class Meta:\n        border_label = "List"\n        children = [\n            widgets.Button(label="Button 1", callback=None),\n            widgets.Button(label="Button 2", callback=None),\n            widgets.Button(label="Button 3", callback=None),\n        ]\n        item_height = 5\n\nclass VertSplit(widgets.FlexBox):\n    text_box = widgets.TextBox(border_label="Text Box", text="Hello World!")\n    text_log = widgets.TextLog(border_label="Text Log")\n    button_list = ButtonList()\n    \n    class Meta:\n        flex_direction = widgets.FlexBox.HORIZONTAL\n\n\nwith Tanmatsu(title="Tanmatsu!") as t:\n    rw = VertSplit()\n    t.set_root_widget(rw)\n    \n    for (i, v) in enumerate(rw.button_list.children):\n        v.callback = lambda i=i: rw.text_log.append_line(f"Button {i + 1} pressed")\n    \n    t.loop()\n```\n\n# Installation\n\n`pip install tanmatsu`\n\n# Documentation\n\nhttps://tanmatsu.readthedocs.io/en/latest/\n\n# Requirements\n\n* Python >=3.11\n* GNU/Linux\n* Full-featured terminal emulator (e.g., Gnome VTE)\n* A font with unicode symbols (e.g., [Noto](https://fonts.google.com/noto))\n\n# Dependencies\n\n* tri.declarative\n* parsy\n* wcwidth\n\nDevelopment dependancies:\n\n* sphinx\n\n# Development\n\n## Installing\n\n1. If not running python 3.11, install [pyenv](https://github.com/pyenv/pyenv).\n2. Install [poetry](https://python-poetry.org/docs/).\n3. Run `poetry install` from the repository directory to set up a virtual environment with the necessary python version and packages\n\n## Running\n\n`poetry run python3 main.py`\n\n## Testing\n\n`poetry run python3 -m unittest`\n\n# Changelog\n\nSee [CHANGELOG.md](../master/CHANGELOG.md).\n\n# License\n\nMIT. For more information, see [LICENSE.md](../master/LICENSE.md).\n',
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
