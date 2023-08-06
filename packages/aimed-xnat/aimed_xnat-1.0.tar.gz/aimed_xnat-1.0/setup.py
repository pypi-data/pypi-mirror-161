#!/usr/bin/env python
import os
import io
import re
from setuptools import setup, find_packages


def parse_requirements(filepath):
    with open(filepath) as f:
        contents = f.read()
    return contents.split('\n')


def read(*names, **kwargs):
    with io.open(os.path.join(os.path.dirname(__file__), *names),
                 encoding=kwargs.get("encoding", "utf8")) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = open('README.md').read()

setup(
    # Metadata
    name='aimed_xnat',
    version='1.0',
    author='Abdolkarim Saeedi',
    description='XNAT data manipulation tools',
    author_email='parsa592323@gmail.com',
    url='https://github.com/KiLJ4EdeN/aimed_xnat',
    download_url='https://github.com/KiLJ4EdeN/aimed_xnatreleases/tag/v_01',
    long_description=long_description,
    license='Apache-2.0',
    packages=find_packages(),
    # Package info
    # include_package_data=True,
    install_requires=['alabaster==0.7.12', 'Babel==2.9.1', 'certifi==2021.10.8',
                      'charset-normalizer==2.0.7', 'colorama==0.4.4', 'docutils==0.17.1',
                      'future==0.18.2', 'idna==3.3', 'imagesize==1.2.0', 'isodate==0.6.0',
                      'Jinja2==3.0.2', 'lxml==4.6.3', 'MarkupSafe==2.0.1', 'packaging==21.0',
                      'pathlib==1.0.1', 'progressbar2==3.55.0', 'Pygments==2.10.0', 'pyparsing==3.0.3',
                      'python-utils==2.5.6', 'pytz==2021.3', 'pyxnat==1.4', 'requests==2.26.0',
                      'six==1.16.0', 'snowballstemmer==2.1.0', 'Sphinx==4.2.0', 'sphinx-rtd-theme==1.0.0',
                      'sphinxcontrib-applehelp==1.0.2', 'sphinxcontrib-devhelp==1.0.2',
                      'sphinxcontrib-htmlhelp==2.0.0', 'sphinxcontrib-jsmath==1.0.1',
                      'sphinxcontrib-qthelp==1.0.3', 'sphinxcontrib-serializinghtml==1.1.5',
                      'urllib3==1.26.7', 'Werkzeug==1.0.1', 'wrapt==1.12.1', 'xnat==0.3.28',
                      'zipp==3.1.0', 'zope.event==4.4', 'zope.interface==5.1.0'],
    keywords=['medical', 'xnat', 'under-development'],
)
