#!/usr/bin/env python

# Support setuptools only, distutils has a divergent and more annoying API and
# few folks will lack setuptools.
from setuptools import setup
from importlib.resources import open_text

# Version info -- read without importing
_locals = {}
version = open_text('sedge', 'version.txt').read()

# PyYAML ships a split Python 2/3 codebase. Unfortunately, some pip versions
# attempt to interpret both halves of PyYAML, yielding SyntaxErrors. Thus, we
# exclude whichever appears inappropriate for the installing interpreter.
exclude = ['*.yaml2', 'tests']

# Frankenstein long_description: version-specific changelog note + README
text = open_text('sedge', 'README.md').read()
long_description = text


setup(
    name='secure_sedge',
    version=version,
    description='a helpful set of convocations to create certs',
    license='BSD',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='2ps',
    author_email='p.shingavi@yahoo.com',
    url='https://bitbucket.org/dbuy/secure_sedge',
    packages=[ 'sedge', ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'sedge = sedge.main:program.run',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Software Distribution',
        'Topic :: System :: Systems Administration',
    ],
    install_requires=[ 'raft>=1.4.1.2', 'boto3', 'sewer[route53]==0.8.2',
                       'pyyaml', 'colorlog', 'requests' ],
)
