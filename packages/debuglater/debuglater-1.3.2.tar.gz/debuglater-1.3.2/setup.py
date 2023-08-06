import re
import ast
from glob import glob
from os.path import basename, splitext

from setuptools import find_packages
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('src/debuglater/__init__.py', 'rb') as f:
    VERSION = str(
        ast.literal_eval(
            _version_re.search(f.read().decode('utf-8')).group(1)))

DESCRIPTION = """
debuglater allows post-mortem debugging for Python programs.

It writes the traceback of an exception into a file and can later load
it in a Python debugger.

Works with the built-in pdb and with other popular debuggers
(pudb, ipdb and pdbpp).
"""

# requirements
REQUIRES = [
    'colorama',
]

# optional requirements
ALL = [
    'dill',
]

# only needed for development
DEV = [
    'pytest',
    'yapf',
    'flake8',
    'invoke',
    'twine',
    'pkgmt',
    # for tests
    'pandas',
    'numpy',
]

setup(
    name='debuglater',
    version=VERSION,
    description='Post-mortem debugging for Python programs',
    long_description=DESCRIPTION,
    author='Ploomber',
    license='MIT',
    author_email='contact@plooomber.io',
    url='https://github.com/ploomber/debuglater',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    extras_require={
        'dev': DEV + ALL,
        'all': ALL,
    },
    entry_points={
        'console_scripts': [
            'debuglater=debuglater.cli:main',
            'dltr=debuglater.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta', 'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English', 'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Debuggers'
    ],
    install_requires=REQUIRES,
)
