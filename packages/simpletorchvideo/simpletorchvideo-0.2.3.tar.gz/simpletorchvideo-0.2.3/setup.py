#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

with open("README.md", "r", encoding='utf8') as fh:
    long_description = fh.read()

package_dir = {
    'simpletorchvideo': 'simpletorchvideo',
    'simpletorchvideo.reader': 'simpletorchvideo/reader',
    'simpletorchvideo.ffmpeg': 'simpletorchvideo/ffmpeg',
    'simpletorchvideo.reds': 'simpletorchvideo/reds',
    'simpletorchvideo.vimeo': 'simpletorchvideo/vimeo',
}

setup(
    name='simpletorchvideo',
    version='0.2.3',
    author='yindaheng98',
    author_email='yindaheng98@163.com',
    url='https://github.com/yindaheng98/simpletorchvideo',
    description=u'Some useful video dataset in pytorch',
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir=package_dir,
    packages=[key for key in package_dir],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'torch>=1.12.0',
        'opencv-python>=4.6.0.66',
        'ffmpeg-python>=0.2.0',
    ],
)
