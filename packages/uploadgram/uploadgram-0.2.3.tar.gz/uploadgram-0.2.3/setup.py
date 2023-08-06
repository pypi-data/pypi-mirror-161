# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['uploadgram']

package_data = \
{'': ['*']}

install_requires = \
['Pyrogram==2.0.35',
 'TgCrypto==1.2.3',
 'hachoir==3.1.1',
 'python-dotenv==0.10',
 'tqdm==4.62.3']

entry_points = \
{'console_scripts': ['uploadgram = uploadgram.shell:main']}

setup_kwargs = {
    'name': 'uploadgram',
    'version': '0.2.3',
    'description': 'Upload files to Telegram upto 4 GiB, from the Terminal',
    'long_description': '## uploadgram\n\nuploadgram uses your Telegram account to upload files up to 2GiB, from the Terminal.\n\n- Heavily inspired by the [telegram-upload](https://github.com/Nekmo/telegram-upload)\n\n- Installing:\n`pip install uploadgram`\n\n- Requirements:\n`pyrogram`\n\n\n# Sample Usage\n\n```sh\n$ uploadgram 7351948 /path/to/dir/or/file --delete_on_success True --fd True -t /path/to/custom/thumbnail\n```\n',
    'author': 'Shrimadhav U K',
    'author_email': 'uploADGRam@shrimadhavUK.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SpEcHiDe/UploadGram',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.7,<4',
}


setup(**setup_kwargs)
