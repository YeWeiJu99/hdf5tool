#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
hdf5tool启动脚本

这个脚本用于启动hdf5tool应用程序。
它会检查依赖项并启动主程序。
支持-f参数处理单个或多个HDF5文件。
"""

import sys
import os
import argparse
import glob

def check_dependencies():
    """检查依赖项是否已安装"""
    required_packages = [
        ('PySide6', 'PySide6'),
        ('h5py', 'h5py'),
        ('pyqtgraph', 'pyqtgraph'),
        ('psutil', 'psutil')
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("错误: 缺少以下依赖项:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请使用以下命令安装依赖项:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_file_exists(file_path):
    """检查文件是否存在"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    return file_path

def check_h5_file(file_path):
    """检查文件是否为有效的HDF5文件"""
    try:
        import h5py
        with h5py.File(file_path, 'r') as f:
            # 简单的文件格式检查
            if not hasattr(f, 'file'):
                raise ValueError(f"文件格式不正确: {file_path}")
    except Exception as e:
        raise ValueError(f"无法读取HDF5文件 {file_path}: {str(e)}")
    
    return file_path

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="HDF5数据可视化工具（中文版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  hdf5tool                         # 启动应用程序但不打开文件
  hdf5tool -f file1.h5            # 打开单个文件
  hdf5tool -f file1.h5 -f file2.h5 -f file3.h5  # 打开多个文件
  hdf5tool -f *.h5                # 使用通配符打开所有h5文件
  hdf5tool -f file.h5 --no-format-check  # 跳过文件格式检查
  
备用用法（直接运行源码）:
  python run.py                   # 启动应用程序但不打开文件
  python run.py -f file1.h5       # 打开单个文件
        """
    )
    
    parser.add_argument(
        "-f", "--file", 
        dest="files",
        action="append",
        help="HDF5文件路径（可多次使用此参数指定多个文件）"
    )
    
    parser.add_argument(
        "--no-format-check", 
        action="store_true",
        help="跳过HDF5文件格式检查"
    )
    
    return parser.parse_args()

def process_file_list(file_patterns, skip_format_check=False):
    """处理文件列表，支持通配符和格式检查"""
    if not file_patterns:
        return []
    
    expanded_files = []
    
    for file_pattern in file_patterns:
        if '*' in file_pattern or '?' in file_pattern:
            # 使用glob处理通配符
            matched_files = glob.glob(file_pattern)
            if not matched_files:
                print(f"警告: 通配符 '{file_pattern}' 没有匹配到任何文件")
            expanded_files.extend(matched_files)
        else:
            expanded_files.append(file_pattern)
    
    if not expanded_files:
        print("警告: 没有找到任何有效的文件")
        return []
    
    # 去重文件列表
    expanded_files = list(set(expanded_files))
    
    # 验证文件
    valid_files = []
    for file_path in expanded_files:
        try:
            check_file_exists(file_path)
            if not skip_format_check:
                check_h5_file(file_path)
            valid_files.append(file_path)
            print(f"[OK] 文件验证通过: {file_path}")
        except (FileNotFoundError, ValueError) as e:
            print(f"[ERROR] 文件验证失败: {str(e)}")
        except Exception as e:
            print(f"[ERROR] 文件验证出错: {str(e)}")
    
    return valid_files

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # print("hd5ftool_cn - HDF5数据可视化工具（中文版）")
    # print("=" * 50)
    
    # 检查依赖项
    if not check_dependencies():
        input("按任意键退出...")
        return 1
    
    # 处理文件参数
    valid_files = process_file_list(args.files, args.no_format_check)
    
    if args.files and not valid_files:
        print("\n错误: 没有有效的HDF5文件可以打开")
        input("按任意键退出...")
        return 1
    
    # 导入并运行应用程序
    try:
        from PySide6.QtWidgets import QApplication
        # 尝试不同的导入方式，兼容包安装和直接运行
        try:
            from src.mainwindow import MainWindow
        except ImportError:
            # 包安装模式
            from .src.mainwindow import MainWindow
        
        # 创建QApplication实例
        app = QApplication(sys.argv)
        
        # 设置应用程序属性
        app.setApplicationName("hdf5tool")
        app.setApplicationDisplayName("HDF5数据可视化工具")
        app.setOrganizationName("hdf5tool")
        
        # 创建并显示主窗口
        window = MainWindow(app)
        window.show()
        
        # 打开命令行指定的文件
        if valid_files:
            print(f"\n正在打开 {len(valid_files)} 个文件:")
            for file_path in valid_files:
                print(f"  - {file_path}")
                try:
                    window.open_file(file_path)
                except Exception as e:
                    print(f"[ERROR] 打开文件失败 {file_path}: {str(e)}")
        
        # 启动事件循环
        return app.exec()
        
    except Exception as e:
        print(f"启动应用程序时出错: {e}")
        import traceback
        traceback.print_exc()
        input("按任意键退出...")
        return 1

if __name__ == "__main__":
    sys.exit(main())