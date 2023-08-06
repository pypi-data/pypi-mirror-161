import codecs
import os.path
import re

from setuptools import find_packages, setup

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

with open('requirements_dev.txt') as f:
    dev_requires = f.read().splitlines()

with open('docs/requirements.txt') as f:
    docs_requires = f.read().splitlines()

with open('README.md') as f:
    long_description = f.read()


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        match = re.search(r'## (\d{1,2}\.\d{1,2}\.\d{1,2})', line)
        if match is not None:
            match = match.group(1)
            return str(match)
    else:
        raise RuntimeError('Unable to find version string.')


setup(
    name='osaft',
    version=get_version('CHANGELOG.md'),
    packages=find_packages(),
    description='An Open-Source Python Library For Acoustofluidics',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='osaftpy developer team',
    author_email='osaftpy@gmail.com',
    url='https://gitlab.com/acoustofluidics/osaft',
    project_urls={
        'Documentation': 'https://osaft.readthedocs.io/en/stable/',
        'Tracker': 'https://gitlab.com/acoustofluidics/osaft/-/issues',
    },
    install_requires=install_requires,
    extras_require={
        'dev': dev_requires,
        'docs': docs_requires,
    },
    test_suite='tests',
    keywords='msaf arf scattering acoustofluidic acoustic-radiation-force',
    license='LPGL v3',
    python_requires='>=3.9',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU Lesser General Public License v3 '
        '(LGPLv3)',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
