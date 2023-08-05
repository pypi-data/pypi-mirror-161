import sys, os, subprocess, sysconfig
from distutils import sysconfig
import setuptools
import re
import platform

pkg = 'kvaser'

with open('README.md', 'r') as fh:
    long_description = fh.read()

base_dir = os.path.dirname(__file__)

about = {}
with open(os.path.join(base_dir, 'src', pkg, '__about__.py')) as f:
    exec(f.read(), about)


#scripts =
scripts = None

setuptools.setup(
    name=about['__name__'],
    version=about['__version__'],
    author=about['__author__'],
    author_email=about['__email__'],
    url=about['__url__'],
    description=about['__description__'],
    long_description_content_type='text/markdown',
    long_description=long_description,
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    zip_safe=False,
    license=about['__license__'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: C++',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Mathematics',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent'
    ],
    # scripts=list(map(lambda x: 'bin/'+x, os.listdir('bin'))),
    install_requires=[
        'pandas>=1.0.3',
        'numpy>=1.15',
        'rich',
        #'pyarrow>=1.0',
        'azure-storage-blob>=12.0'
    ],
    package_data={pkg: ['data/*.dat', 'data/*.gz']},
    tests_require=['pytest'],
)
