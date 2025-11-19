"""
部署配置文件
定义不同环境下的资源路径和配置
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional


class DeployConfig:
    """部署配置类"""
    
    def __init__(self):
        self.app_name = "hd5ftool"
        self.version = "1.0.0"
        
        # 环境检测
        self.is_development = self._detect_development()
        self.is_frozen = getattr(sys, 'frozen', False)
        self.is_windows = sys.platform == "win32"
        self.is_linux = sys.platform.startswith("linux")
        self.is_macos = sys.platform == "darwin"
        
        # 路径配置
        self.base_dir = self._get_base_directory()
        self.icons_dir = self.base_dir / "src" / "icons"
        self.resources_file = self.base_dir / "src" / "resources.rcc"
        
        # 资源配置
        self.resource_mappings = self._get_resource_mappings()
    
    def _detect_development(self) -> bool:
        """检测是否为开发环境"""
        indicators = [
            Path("resources.qrc").exists(),
            Path("main.py").exists(),
            Path("requirements.txt").exists(),
            "site-packages" not in Path(__file__).as_posix()
        ]
        return any(indicators)
    
    def _get_base_directory(self) -> Path:
        """获取应用程序基础目录"""
        if self.is_frozen:
            # 打包后的可执行文件
            return Path(sys.executable).parent
        else:
            # 开发环境 - 返回项目根目录
            return Path(__file__).parent.parent
    
    def _get_resource_mappings(self) -> Dict[str, str]:
        """获取资源映射配置"""
        return {
            # 图标映射
            "folder": "folder.svg",
            "folder_open": "folder-open.svg", 
            "dataset": "dataset.svg",
            "plot": "plot.svg",
            "hdf5view": "hdf5view.ico",
            "hdf5view_svg": "hdf5view.svg",
            "image": "image.svg",
            
            # 其他资源可以在这里添加
            # "theme": "themes/default.qss",
            # "config": "config/default.json",
        }
    
    def get_icon_path(self, icon_key: str) -> Optional[Path]:
        """获取图标文件的完整路径"""
        if icon_key not in self.resource_mappings:
            return None
        
        icon_name = self.resource_mappings[icon_key]
        return self.icons_dir / icon_name
    
    def get_resource_path(self, resource_key: str) -> Optional[str]:
        """获取资源的Qt资源路径"""
        if resource_key not in self.resource_mappings:
            return None
        
        resource_name = self.resource_mappings[resource_key]
        return f":/icons/{resource_name}"
    
    def validate_resources(self) -> List[str]:
        """验证资源文件是否存在"""
        missing_resources = []
        
        for key, filename in self.resource_mappings.items():
            if filename.endswith(('.svg', '.ico', '.png', '.jpg')):
                icon_path = self.icons_dir / filename
                if not icon_path.exists():
                    missing_resources.append(str(icon_path))
        
        return missing_resources
    
    def get_deployment_info(self) -> Dict:
        """获取部署信息"""
        return {
            "app_name": self.app_name,
            "version": self.version,
            "environment": "development" if self.is_development else "production",
            "platform": sys.platform,
            "base_dir": str(self.base_dir),
            "icons_dir": str(self.icons_dir),
            "resources_file": str(self.resources_file),
            "resource_mappings": self.resource_mappings,
            "missing_resources": self.validate_resources()
        }


# 创建全局配置实例
deploy_config = DeployConfig()


def get_deploy_config() -> DeployConfig:
    """获取部署配置实例"""
    return deploy_config


if __name__ == "__main__":
    # 测试代码
    config = get_deploy_config()
    info = config.get_deployment_info()
    
    print("部署配置信息:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # 验证资源
    missing = config.validate_resources()
    if missing:
        print(f"\n缺失的资源文件: {len(missing)}")
        for file in missing:
            print(f"  - {file}")
    else:
        print("\n✓ 所有资源文件都存在")