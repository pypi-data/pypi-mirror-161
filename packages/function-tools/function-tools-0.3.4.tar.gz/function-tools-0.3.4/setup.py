from codecs import (
    open,
)
from os import (
    path,
)

from setuptools import (
    find_packages,
    setup,
)


__version__ = '0.3.4'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'CHANGES.md'), encoding='utf-8') as f:
    long_description += f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [
    x.strip()
    for x in all_reqs if
    'git+' not in x
]
dependency_links = [
    x.strip().replace('git+', '')
    for x in all_reqs if
    x.startswith('git+')
]

excluded_packages = (
    'docs',
)

setup(
    name='function-tools',
    version=__version__,
    description='Tools for creating functions',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='',
    packages=find_packages(exclude=excluded_packages),
    include_package_data=True,
    author='Alexander Danilenko',
    install_requires=install_requires,
    dependency_links=dependency_links,
    author_email='a.danilenko@bars.group',
    url='https://github.com/sandanilenko/function-tools',
)
