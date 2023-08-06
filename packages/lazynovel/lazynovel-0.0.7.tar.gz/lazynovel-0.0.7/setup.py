#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="lazynovel",
    version="0.0.7",
    description="小说平台接口封包",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    author="ZeroSeeker",
    author_email="zeroseeker@foxmail.com",
    url="https://gitee.com/ZeroSeeker/lazynovel",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'lazysdk==0.0.16'
    ]
)
