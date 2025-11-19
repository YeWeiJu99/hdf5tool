"""
统一资源管理模块
提供跨平台的图标和资源加载功能
"""

import os
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtGui import QIcon
from PySide6.QtCore import QResource


class ResourceManager:
    """资源管理器，提供统一的图标加载接口"""
    
    def __init__(self):
        self._resource_registered = False
        self._app_dir = None
        self._fallback_enabled = True
        
        # 初始化应用目录
        self._init_app_directory()
        
        # 尝试注册资源文件
        self._try_register_resources()
    
    def _init_app_directory(self):
        """初始化应用程序目录"""
        # 获取应用程序的根目录
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件
            self._app_dir = Path(sys.executable).parent
        else:
            # 开发环境
            # 从当前文件向上找到项目根目录
            current_file = Path(__file__).resolve()
            self._app_dir = current_file.parent.parent  # 向上两级到项目根目录
    
    def _try_register_resources(self):
        """尝试注册Qt资源文件"""
        try:
            # 查找资源文件
            qrc_file = self._app_dir / "resources.rcc"
            
            if qrc_file.exists():
                # 注册编译后的资源文件
                if QResource.registerResource(str(qrc_file)):
                    self._resource_registered = True
                    print(f"已注册资源文件: {qrc_file}")
            else:
                # 尝试注册源资源文件（开发环境）
                qrc_source = self._app_dir / "src" / "resources.qrc"
                if qrc_source.exists():
                    # 在开发环境中，Qt会自动查找.qrc文件
                    print(f"找到资源源文件: {qrc_source}")
                    # 注意：.qrc文件需要通过pyrcc或pyside6-rcc编译
        except Exception as e:
            print(f"注册资源文件失败: {e}")
    
    def get_icon(self, icon_name: str) -> QIcon:
        """
        获取图标，支持多种回退机制
        
        Args:
            icon_name: 图标文件名，如 "folder.svg"
            
        Returns:
            QIcon: 加载的图标，如果失败则返回空图标
        """
        # 1. 首先尝试从Qt资源系统加载
        if self._resource_registered:
            resource_path = f":/icons/{icon_name}"
            icon = QIcon(resource_path)
            if not icon.isNull():
                return icon
        
        # 2. 尝试从开发环境相对路径加载
        if self._fallback_enabled:
            # 构建绝对路径
            icon_path = self._app_dir / "src" / "icons" / icon_name
            
            if icon_path.exists():
                return QIcon(str(icon_path))
            
            # 3. 尝试从系统路径加载（用于系统图标）
            system_icon = QIcon.fromTheme(icon_name.replace('.svg', '').replace('.ico', ''))
            if not system_icon.isNull():
                return system_icon
        
        # 4. 返回空图标
        print(f"警告: 无法加载图标: {icon_name}")
        return QIcon()
    
    def get_icon_path(self, icon_name: str) -> Optional[str]:
        """
        获取图标的文件路径
        
        Args:
            icon_name: 图标文件名
            
        Returns:
            str: 图标文件的绝对路径，如果找不到返回None
        """
        # 检查资源系统
        if self._resource_registered:
            resource_path = f":/icons/{icon_name}"
            if QResource(resource_path).isValid():
                return resource_path
        
        # 检查文件系统
        icon_path = self._app_dir / "icons" / icon_name
        if icon_path.exists():
            return str(icon_path)
        
        return None
    
    def set_fallback_enabled(self, enabled: bool):
        """启用或禁用回退机制"""
        self._fallback_enabled = enabled
    
    def get_available_icons(self) -> list:
        """获取所有可用的图标列表"""
        icons_dir = self._app_dir / "icons"
        if icons_dir.exists():
            return [f.name for f in icons_dir.iterdir() if f.is_file()]
        return []


# 创建全局资源管理器实例
resource_manager = ResourceManager()


# 便捷函数
def get_icon(icon_name: str) -> QIcon:
    """便捷函数：获取图标"""
    return resource_manager.get_icon(icon_name)


def get_icon_path(icon_name: str) -> Optional[str]:
    """便捷函数：获取图标路径"""
    return resource_manager.get_icon_path(icon_name)


def preload_common_icons():
    """预加载常用图标以提高性能"""
    common_icons = [
        "folder.svg",
        "folder-open.svg", 
        "dataset.svg",
        "plot.svg",
        "hdf5view.ico",
        "image.svg"
    ]
    
    for icon_name in common_icons:
        try:
            get_icon(icon_name)  # 预加载到缓存中
        except Exception as e:
            print(f"预加载图标失败 {icon_name}: {e}")


# 图标常量定义
class Icons:
    """图标常量类，提供类型安全的图标引用"""
    
    FOLDER = "folder.svg"
    FOLDER_OPEN = "folder-open.svg"
    DATASET = "dataset.svg"
    PLOT = "plot.svg"
    HDF5VIEW = "hdf5view.ico"
    HDF5VIEW_SVG = "hdf5view.svg"
    IMAGE = "image.svg"
    
    @classmethod
    def get(cls, icon_name: str) -> QIcon:
        """获取指定名称的图标"""
        return get_icon(icon_name)


if __name__ == "__main__":
    # 测试代码
    print("资源管理器测试")
    print(f"应用目录: {resource_manager._app_dir}")
    print(f"资源已注册: {resource_manager._resource_registered}")
    print(f"可用图标: {resource_manager.get_available_icons()}")
    
    # 测试图标加载
    for icon_name in ["folder.svg", "dataset.svg", "plot.svg"]:
        icon = get_icon(icon_name)
        print(f"图标 {icon_name}: {'✓' if not icon.isNull() else '✗'}")