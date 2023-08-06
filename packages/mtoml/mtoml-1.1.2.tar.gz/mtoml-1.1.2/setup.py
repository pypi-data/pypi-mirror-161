#######################################################################
# Copyright (c) 2022 Jordan Schaffrin                                 #
#                                                                     #
# This Source Code Form is subject to the terms of the Mozilla Public #
# License, v. 2.0. If a copy of the MPL was not distributed with this #
# file, You can obtain one at http://mozilla.org/MPL/2.0/.            #
#######################################################################

from setuptools import setup

def read_file(filename: str) -> str:
    text_result = r''

    with open(filename, r'r') as the_file:
        text_result = the_file.read()

    return text_result

setup(
    name=r'mtoml',
    version=r'1.1.2',    
    description=r'Manage multiple TOML configurations from a single module.',
    long_description=read_file(r'./README.md'),
    long_description_content_type=r'text/markdown',
    url=r'https://github.com/wuotes/mtoml',
    download_url=r'https://pypi.org/project/mtoml/',
    author=r'Jordan Schaffrin',
    author_email=r'mailbox@xrtuen.com',
    license=r'Mozilla Public License 2.0',
    python_requires=r'>=3.9',
    packages=[r'mtoml'],
    install_requires=[r'tomli>=2.0.1',
                      r'tomli_w>=1.0.0',                     
                      ],

    classifiers=[
        r'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        r'Programming Language :: Python :: 3.9',
        r'Programming Language :: Python :: 3.10',
        r'Programming Language :: Python :: 3.11',
        r'Programming Language :: Python :: 3.12',
        r'Operating System :: Microsoft :: Windows',
        r'Operating System :: POSIX :: Linux',
        r'Operating System :: MacOS',
    ],
)
