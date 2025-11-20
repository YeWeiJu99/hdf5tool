#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDF5Tool安装脚本

将hd5ftool打包为可安装的Python包，支持命令行使用。
"""

import os
import sys
from setuptools import setup, find_packages

# 读取版本信息
version = "1.0.0"
with open("__init__.py", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"\'')
            break

# 读取README
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

# 读取依赖项
requirements = []
if os.path.exists("requirements.txt"):
    with open("requirements.txt", "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="hdf5tool",
    version=version,
    description="基于PySide6的HDF5数据可视化工具（中文版）",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="hdf5tool开发团队",
    author_email="",
    url="",
    packages=find_packages() + ["src", "src.models", "src.views"],
    package_dir={
        "": ".",
        "src": "src",
        "src.models": "src/models", 
        "src.views": "src/views"
    },
    include_package_data=True,
    package_data={
        "src": [
            "*.py",
            "*.rcc",
            "*.qrc",
            "icons/*.svg",
            "icons/*.ico",
        ],
        "src.models": [
            "*.py",
        ],
        "src.views": [
            "*.py",
        ],
        "": [
            "config/*.py",
            "config/*.json",
            "README.md",
        ]
    },
    entry_points={
        "console_scripts": [
            "hdf5tool=hdf5tool.__main__:main",
        ],
    },
    install_requires=requirements,
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Utilities",
    ],
    keywords="hdf5 visualization data-analysis pyqt pyside",
)