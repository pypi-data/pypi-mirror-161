# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ntuee_mailer']

package_data = \
{'': ['*'],
 'ntuee_mailer': ['template_letter/*', 'template_letter/attachments/*']}

install_requires = \
['Cerberus==1.3.4',
 'PyYAML==6.0',
 'email-validator==1.2.1',
 'rich==12.5.1',
 'typer[all]>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['ntuee-mailer = ntuee_mailer.main:app']}

setup_kwargs = {
    'name': 'ntuee-mailer',
    'version': '2.0.7',
    'description': 'an auto mailer to send emails in batch for you',
    'long_description': '# `ntuee-mailer`\n\nThis is a simple mailer for NTU students to send letters in batches.\n\n**Installation**\n\n```bash\n$ pip install ntuee-mailer\n```\n\n**Usage**:\n\n```bash\n$ ntuee-mailer [OPTIONS] COMMAND [ARGS]...\n```\n\n**Options**:\n\n- `--install-completion`: Install completion for the current shell.\n- `--show-completion`: Show completion for the current shell, to copy it or customize the installation.\n- `--help`: Show this message and exit.\n\n**Commands**:\n\n- `check`: check wether a directory is a valid letter a...\n- `config`: configure the auto mailer a valid config file...\n- `new`: create a new letter from template\n- `send`: send emails to a list of recipients as...\n\n## `ntuee-mailer check`\n\ncheck wether a directory is a valid letter\n\na letter folder should be structured as follows:\n\nletter\n\n├── attachments\n\n│ ├── ...\n\n│ └── ...\n\n├── config.yml\n\n├── content.html\n\n└── recipients.csv\n\n**Usage**:\n\n```console\n$ ntuee-mailer check [OPTIONS] LETTER_PATH\n```\n\n**Arguments**:\n\n- `LETTER_PATH`: Path to letter directory [required]\n\n**Options**:\n\n- `--help`: Show this message and exit.\n\n## `ntuee-mailer config`\n\nconfigure the auto mailer\n\na valid config file should have the following structure:\n\n[smtp]\n\nhost=smtps.ntu.edu.tw\n\nport=465\n\ntimeout=5\n\n[pop3]\n\nhost=msa.ntu.edu.tw\n\nport=995\n\ntimeout=5\n\n[account]\n\nname=John Doe\n\n**Usage**:\n\n```console\n$ ntuee-mailer config [OPTIONS]\n```\n\n**Options**:\n\n- `-f, --file TEXT`: Path to new config file whose content will be copied to config.ini\n- `-r, --reset`: Reset config.ini to default [default: False]\n- `-l, --list`: list current config [default: False]\n- `--help`: Show this message and exit.\n\n## `ntuee-mailer new`\n\ncreate a new letter from template\n\n**Usage**:\n\n```console\n$ ntuee-mailer new [OPTIONS] LETTER_NAME\n```\n\n**Arguments**:\n\n- `LETTER_NAME`: Name of letter [required]\n\n**Options**:\n\n- `--help`: Show this message and exit.\n\n## `ntuee-mailer send`\n\nsend emails to a list of recipients as configured in your letter\n\n**Usage**:\n\n```console\n$ ntuee-mailer send [OPTIONS] [LETTER_PATH]\n```\n\n**Arguments**:\n\n- `[LETTER_PATH]`: Path to letter\n\n**Options**:\n\n- `-t, --test`: Test mode: send mail to yourself [default: False]\n- `-c, --config FILE`: Path to config.ini [default: /home/madmax/.config/ntuee-mailer/config.ini]\n- `-q, --quiet`: Quiet mode: less output [default: False]\n- `-d, --debug INTEGER RANGE`: Debug level [default: 0]\n- `--help`: Show this message and exit.\n\n## `ntuee-mailer test`\n\n**Usage**:\n\n```console\n$ ntuee-mailer test [OPTIONS]\n```\n\n**Options**:\n\n- `--help`: Show this message and exit.\n',
    'author': 'zhuang-jia-xu',
    'author_email': '76544194+zhuang-jia-xu@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/NTUEE-SAAD/mailing',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
