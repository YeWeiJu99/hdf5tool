# HDF5Tool 项目结构说明

## 目录结构概述

本项目采用标准的Python项目结构，将不同类型的文件分类存放，便于维护和扩展。

## 主要目录说明

### 根目录文件

- **run.py** - 主启动脚本，包含命令行参数解析和依赖检查
- **requirements.txt** - 项目依赖包列表
- **README.md** - 项目说明文档
- **__init__.py** - 包初始化文件，定义版本信息

### src/ - 源代码目录

包含所有应用程序源代码：

- **main.py** - 应用程序入口点
- **mainwindow.py** - 主窗口实现
- **models.py** - 模型模块重定向文件
- **views.py** - 视图模块重定向文件
- **resources.py** - 资源管理模块
- **resources.qrc** - Qt资源文件定义
- **icons/** - 图标资源文件
- **models/** - 数据模型模块
  - table_models.py - 表格数据模型
  - tree_model.py - 树形结构模型
  - view_models.py - 视图数据模型
  - utils.py - 工具函数
- **views/** - 视图组件模块
  - hdf5_widget.py - HDF5文件主视图
  - plot_dialog.py - 绘图配置对话框
  - image_view.py - 图像显示视图
  - plot_view.py - 数据绘图视图
  - export_utils.py - 数据导出工具

### config/ - 配置文件目录

- **deploy_config.py** - 部署配置模块
- **plot_config.json** - 绘图配置文件

### scripts/ - 工具脚本目录

- **build_resources.py** - 资源构建脚本
- **generate_sine_data.py** - 测试数据生成脚本

### docs/ - 文档目录

- **PROJECT_STRUCTURE.md** - 详细的项目结构文档

### data/ - 数据目录

- **test_*.h5** - 各种测试用的HDF5文件
- **sine_*.h5** - 正弦波测试数据文件

## 模块导入说明

### 路径处理

为了确保模块能正确导入，在src目录下的主要文件中添加了路径处理：

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

这确保了从项目根目录开始导入模块。

### 导入示例

```python
# 从src目录导入
from src.mainwindow import MainWindow
from src.views import HDF5Widget
from src.models import DimsTableModel
```

## 开发工作流

### 1. 开发新功能

- 在src/models/或src/views/中添加新模块
- 更新相应的__init__.py文件
- 在src/models.py或src/views.py中添加重定向

### 2. 添加配置

- 在config/目录添加配置文件
- 使用config/deploy_config.py进行管理

### 3. 创建工具脚本

- 在scripts/目录添加工具脚本
- 使用相对路径引用项目文件

### 4. 文档更新

- 在docs/目录添加文档
- 更新README.md

## 构建和部署

### 资源构建

```bash
cd scripts
python build_resources.py --compile
```

### 依赖安装

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
python run.py
```

## 注意事项

1. 所有相对路径都基于项目根目录
2. src目录下的重定向文件确保向后兼容性
3. 资源文件路径在resources.py中统一管理
4. 配置文件集中存放在config目录
5. 测试数据统一存放在data目录