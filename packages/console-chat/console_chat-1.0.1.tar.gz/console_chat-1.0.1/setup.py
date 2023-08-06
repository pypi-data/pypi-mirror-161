from setuptools import setup
from io import open

version = '1.0.1'

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='console_chat',
    version=version,

    author='chevychelov.n',

    description=u'Simple console chat',
    long_description=long_description,
    long_description_content_type='text/markdown',

    packages=['console_chat'],

    classifiers=[
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.9'

    ]
)