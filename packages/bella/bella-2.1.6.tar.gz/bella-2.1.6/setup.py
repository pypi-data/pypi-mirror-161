# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bella', 'bella.modules']

package_data = \
{'': ['*']}

install_requires = \
['ujson>=5.4.0,<6.0.0']

setup_kwargs = {
    'name': 'bella',
    'version': '2.1.6',
    'description': 'BellaPy - A useful helper for any python program',
    'long_description': "# bellapy\nBellaPy - A useful helper for any python program\n\n[![PyPI version](https://badge.fury.io/py/bella.svg)](https://badge.fury.io/py/bella)\n![CI test](https://github.com/ndaidong/bellapy/workflows/ci-test/badge.svg)\n![CodeQL](https://github.com/ndaidong/bellapy/workflows/CodeQL/badge.svg)\n\n\n## Contents\n\n* [Setup](#setup)\n* [APIs](#apis)\n* [Dev & Test](#dev--test)\n* [License](#license)\n\n\n## Setup\n\n```bash\npip install bella\n\n# or build from source\ngit clone https://github.com/ndaidong/bellapy.git\ncd bellapy\npython3 setup.py install\n```\n\n## Usage\n\n```py\nfrom bella import genid, md5\n\ngenid()  # --> akrqHX7eQyT3neF6\ngenid(5)  # --> xzxNK\nmd5('hello')  # --> 5d41402abc4b2a76b9719d911017c592\n```\n\n\n# APIs\n\n### Datatype detection\n\n-  is_int(val: Any)\n-  is_float(val: Any)\n-  is_num(val: Any)\n-  is_str(val: Any)\n-  is_bool(val: Any)\n-  is_list(val: Any)\n-  is_dict(val: Any)\n-  is_valid_url(val: Any)\n\n\n### Encryption\n\n```python\nmd5(text: str)\nmd160(text: str)\nsha256(text: str, salt: str, dkpower: int = 3, iterations: int = 50000)\n```\n\nExamples:\n\n```python\nmd5('hello')  # --> 5d41402abc4b2a76b9719d911017c592\nmd160('hello')  # --> 108f07b8382412612c048d07d13f814118445acd\nsha256('1234', 'v23')  # --> 457b01a0f6169725\n\n# dkpower relates to length of output, default is 3\n# output length = 2 ** (dkpower + 1)\n# for example with dkpower = 4 --> output length = 2 ** 5 = 32\nsha256('1234', 'v23', dkpower=4) # --> 457b01a0f61697250083c598f7b8a8fd\n```\n\n\n### Date & time\n\n\n```python\nPY_DATE_PATTERN  # '%Y-%m-%d %H:%M:%S %z'\nMY_DATE_PATTERN  # '%a, %b %d, %Y %H:%M:%S'\n\nget_time()\nformat_time(datetime, pattern)\nget_local_time()\nget_utc_time()\n```\n\nExamples\n\n```python\nfrom bella import PY_DATE_PATTERN, format_time, get_time\n\nnow = get_time()\ndate_str = format_time(now, PY_DATE_PATTERN)\nprint(date_str)\n```\n\n### Filesystem\n\n\n```python\nfrom bella import fs\n\nfs.exists(file_path: str)\nfs.isdir(file_path: str)\nfs.isfile(file_path: str)\n\n# Get list of child files/folders by specific glob pattern\nfs.get_files(pattern)\n\n# Copy file or folder `source` into `dest`:\nfs.copy(source, dest)\n\n# Remove file or folder\nfs.remove(path)\n```\n\n\n### Utils\n\n```python\ngenid(count: int = 16,  prefix: str = '') # return a random string\nslugify(text: str) # create slug from a string\nstrip_accents(text: str) # remove accents string\nremove_tags(text: str) # remove HTML tags from a string\ntruncate(text: str, maxlen: int) # cut a long string to shorter one\nplurialize(word: str = None, count: int = 1) # return plural format of word\nbyte_to_text(bytesize: int, precision: int = 2)\n\nwrite_json_to_file(file_path: str = '', data: dict = {})\nread_json_from_file(file_path: str = '')\njprint(data: Any, sorting=True, identation=2)\n\nthrottle(seconds: int) # decorator, make a function throttling\ntiming(name: str) # decorator, measure time to execute an expression\n\nhas_installed(package) # check if a python package is installed\n\ncurry(func) # make `func` become a curry function\ncompose(functions) # performs right-to-left function composition\npipe(functions) # performs left-to-right function composition\n```\n\nExamples:\n\n```python\nprint(genid())  # --> akrqHX7eQyT3neF6\nprint(genid(5))  # --> xzxNK\nprint(genid(10, 'id_'))  # --> id_j0fpXAZ\n\nslugify('BellaPy - A useful helper for any python program')\n# --> bellapy-a-useful-helper-for-any-python-program\nslugify('Ngày hội “đám mây” của Amazon')\n# --> ngay-hoi-dam-may-cua-amazon\n\nplurialize('leaf', 1)  # => leaf\nplurialize('leaf', 2)  # => leaves\n\n@throttle(5)\ndef fn(a):\n    print('No call multi times within 5 seconds')\n    print(a)\n\nfn(1)\nfn(2)\nfn(3)\nfn(4)\nfn(5)\nfn(6)\nfn(7)\n\n@timing('save_item')\ndef save_item(data):\n    write_json_to_file('./cache.json', data)\n\nsave_item(dict(name='Alice'))\n# => Timing for save_item: 0.00134 s\n```\n\n\n# Dev & Test\n\n```bash\ngit clone https://github.com/ndaidong/bellapy.git\ncd bellapy\npoetry install\n./run_test.sh\n```\n\n\n# License\n\nThe MIT License (MIT)\n",
    'author': 'Dong Nguyen',
    'author_email': 'ndaidong@gmail.com',
    'maintainer': 'Dong Nguyen',
    'maintainer_email': 'ndaidong@gmail.com',
    'url': 'https://pypi.org/project/bella',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
