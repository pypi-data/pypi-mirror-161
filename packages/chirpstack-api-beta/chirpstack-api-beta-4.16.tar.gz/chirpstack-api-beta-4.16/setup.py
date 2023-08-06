# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

REQUIREMENTS = [
    'grpcio',
    'google-api-core'
]


CLASSIFIERS = [
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.7',
    'Topic :: Communications',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
]

setup(
    py_modules=['chirpstack-ap'],
    name='chirpstack-api-beta',
    version = "4.16",
    url='https://github.com/chirpstack/chirpstack/tree/master/api/',
    author='Orne Brocaar',
    author_email='info@brocaar.com',
    license='MIT',
    description='Chirpstack Python API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
)
