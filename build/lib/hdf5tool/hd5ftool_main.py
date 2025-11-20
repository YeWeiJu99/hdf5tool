#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDF5Tool命令行入口点

这个文件作为可安装包的主入口点，支持命令行调用。
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 导入并运行主程序
from run import main

if __name__ == "__main__":
    main()