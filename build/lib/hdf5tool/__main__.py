#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDF5Tool包主入口点

当使用python -m hdf5tool时调用此文件。
支持命令行参数直接打开HDF5文件。
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 导入并运行主程序
from run import main

if __name__ == "__main__":
    main()