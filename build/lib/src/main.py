"""
包含应用程序的主入口点或命令行接口，
并定义应用程序查找资源的路径。
"""

import argparse
import os
import sys

import PySide6
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

# 包内导入
from .mainwindow import MainWindow
from .resources import get_icon, preload_common_icons


def main():
    """定义主应用程序入口点（命令行接口）。"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("-f", "--file", type=str, required=False)
    args = parser.parse_args()

    # 创建QApplication实例
    app = QApplication(sys.argv)
    app.setOrganizationName("hd5ftool")
    app.setApplicationName("hd5ftool")
    app.setApplicationDisplayName("HDF5数据可视化工具")
    
    # 预加载常用图标
    preload_common_icons()
    
    # 设置窗口图标
    app.setWindowIcon(get_icon("hdf5view.svg"))

    # 创建并显示主窗口
    window = MainWindow(app)
    window.show()

    # 如果在命令行中提供了文件，则打开该文件
    if args.file:
        window.open_file(args.file)

    # 启动事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()