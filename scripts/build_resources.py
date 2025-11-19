#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
资源构建脚本
用于编译Qt资源文件和准备部署
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def find_pyside6_rcc():
    """查找PySide6的rcc工具"""
    try:
        # 尝试通过模块查找
        import PySide6
        pyside6_path = Path(PySide6.__file__).parent
        
        # 常见的rcc工具位置
        rcc_names = ["pyside6-rcc", "pyside6-rcc.exe", "rcc"]
        
        for rcc_name in rcc_names:
            rcc_path = pyside6_path / rcc_name
            if rcc_path.exists():
                return str(rcc_path)
        
        # 尝试系统PATH中的pyside6-rcc
        result = subprocess.run(["pyside6-rcc", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return "pyside6-rcc"
            
    except ImportError:
        pass
    
    return None


def compile_resources():
    """编译Qt资源文件"""
    # 确定正确的路径
    base_dir = Path(__file__).parent.parent
    qrc_file = base_dir / "src" / "resources.qrc"
    rcc_file = base_dir / "src" / "resources.rcc"
    
    if not qrc_file.exists():
        print(f"错误: 找不到资源文件 {qrc_file}")
        return False
    
    # 查找rcc工具
    rcc_tool = find_pyside6_rcc()
    if not rcc_tool:
        print("错误: 找不到pyside6-rcc工具")
        print("请确保已正确安装PySide6")
        return False
    
    print(f"使用rcc工具: {rcc_tool}")
    
    # 编译资源文件
    try:
        cmd = [rcc_tool, str(qrc_file), "-o", str(rcc_file)]
        print(f"执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ 成功编译资源文件: {rcc_file}")
            return True
        else:
            print(f"✗ 编译资源文件失败:")
            print(f"错误输出: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ 编译资源文件时出错: {e}")
        return False


def verify_resources():
    """验证资源文件"""
    base_dir = Path(__file__).parent.parent
    rcc_file = base_dir / "src" / "resources.rcc"
    
    if not rcc_file.exists():
        print(f"警告: 找不到编译后的资源文件 {rcc_file}")
        return False
    
    # 尝试加载资源文件进行验证
    try:
        from PySide6.QtCore import QResource
        
        if QResource.registerResource(str(rcc_file)):
            print("✓ 资源文件验证成功")
            
            # 检查资源内容
            test_resource = QResource(":/icons/folder.svg")
            if test_resource.isValid():
                print("✓ 资源内容验证成功")
                return True
            else:
                print("✗ 资源内容验证失败")
                return False
        else:
            print("✗ 资源文件注册失败")
            return False
            
    except ImportError:
        print("警告: 无法验证资源文件（PySide6未安装）")
        return True
    except Exception as e:
        print(f"✗ 验证资源文件时出错: {e}")
        return False


def clean_resources():
    """清理生成的资源文件"""
    base_dir = Path(__file__).parent.parent
    rcc_file = base_dir / "src" / "resources.rcc"
    py_file = base_dir / "src" / "resources_rc.py"
    
    removed_files = []
    
    if rcc_file.exists():
        rcc_file.unlink()
        removed_files.append(str(rcc_file))
    
    if py_file.exists():
        py_file.unlink()
        removed_files.append(str(py_file))
    
    if removed_files:
        print(f"已清理文件: {', '.join(removed_files)}")
    else:
        print("没有需要清理的文件")


def create_resource_backup():
    """创建资源文件备份"""
    base_dir = Path(__file__).parent.parent
    icons_dir = base_dir / "src" / "icons"
    backup_dir = base_dir / "src" / "icons_backup"
    
    if not icons_dir.exists():
        print("警告: 找不到icons目录")
        return False
    
    try:
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        
        shutil.copytree(icons_dir, backup_dir)
        print(f"✓ 已创建图标备份: {backup_dir}")
        return True
        
    except Exception as e:
        print(f"✗ 创建备份失败: {e}")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="资源构建工具")
    parser.add_argument("--compile", action="store_true", help="编译资源文件")
    parser.add_argument("--verify", action="store_true", help="验证资源文件")
    parser.add_argument("--clean", action="store_true", help="清理生成的文件")
    parser.add_argument("--backup", action="store_true", help="创建备份")
    parser.add_argument("--all", action="store_true", help="执行所有步骤")
    
    args = parser.parse_args()
    
    if args.all or not any([args.compile, args.verify, args.clean, args.backup]):
        # 执行完整流程
        print("开始完整资源构建流程...")
        
        if not create_resource_backup():
            return 1
        
        if not compile_resources():
            return 1
        
        if not verify_resources():
            return 1
        
        print("✓ 资源构建完成")
        return 0
    
    # 执行指定步骤
    if args.backup:
        if not create_resource_backup():
            return 1
    
    if args.compile:
        if not compile_resources():
            return 1
    
    if args.verify:
        if not verify_resources():
            return 1
    
    if args.clean:
        clean_resources()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())