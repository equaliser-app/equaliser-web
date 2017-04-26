# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='equaliser-web',
    version='1.0.0',
    author='George Brighton',
    author_email='gxb256@cs.bham.ac.uk',
    description='Equaliser\'s website',
    url='https://git-teaching.cs.bham.ac.uk/mod-60cr-proj-2016/gxb256/tree/equaliser-web',
    packages=[
        'equaliser_web',
        'website'
    ],
    install_requires=[
        'Django',
        'django-phonenumber-field',
        'Jinja2',
        'Babel',
        'requests'
    ]
)
