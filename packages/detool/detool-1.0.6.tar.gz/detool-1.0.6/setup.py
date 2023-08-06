# -*- coding:utf-8 -*-
# @Author cc
# @TIME 2019/5/25 23:26

from setuptools import setup, find_packages

setup(
    name='detool',
    version='1.0.6',
    description=(
        'decorator tool collection'
    ),
    keywords=("detool", "decorators"),
    long_description_content_type="text/markdown",
    long_description=open('README.md', encoding='utf-8').read(),
    author='abo123456789',
    author_email='abcdef123456chen@sohu.com',
    maintainer='cc',
    maintainer_email='abcdef123456chen@sohu.com',
    license='MIT License',
    install_requires=[
        "loguru>=0.6.0",
        "redis>=3.0.0"
    ],
    packages=find_packages(),
    platforms=["all"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries'
    ])
