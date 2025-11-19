# HDF5Tool 项目结构文档

## 项目概述

HDF5Tool 是一个基于 PySide6 的 HDF5 文件查看和分析工具，支持数据可视化、图像显示和绘图功能。

## 项目结构

```
hd5ftool/
├── README.md                    # 项目说明文档
├── PROJECT_STRUCTURE.md         # 项目结构文档（本文件）
├── requirements.txt             # 项目依赖
├── run.py                      # 主程序入口
├── main.py                     # 主程序配置
├── mainwindow.py               # 主窗口类
├── generate_sine_data.py       # 正弦函数数据生成器
├── resources.py                # 资源管理器
├── resources.qrc               # Qt资源文件
├── build_resources.py          # 资源构建脚本
├── deploy_config.py            # 部署配置
├── plot_config.json            # 绘图配置文件
├── icons/                      # 图标资源目录
│   ├── dataset.svg            # 数据集图标
│   ├── folder-open.svg        # 打开文件夹图标
│   ├── folder.svg             # 文件夹图标
│   ├── hdf5view.ico           # 应用图标
│   ├── hdf5view.svg           # 应用SVG图标
│   ├── image.svg              # 图像图标
│   └── plot.svg               # 绘图图标
├── models/                     # 数据模型目录
│   ├── __init__.py            # 模型包初始化
│   ├── table_models.py        # 表格模型
│   ├── tree_model.py          # 树形模型
│   ├── utils.py               # 工具函数
│   └── view_models.py         # 视图模型
├── views/                      # 视图组件目录
│   ├── __init__.py            # 视图包初始化
│   ├── hdf5_widget.py         # 主HDF5组件
│   ├── image_view.py          # 图像视图
│   ├── plot_view.py           # 绘图视图
│   ├── plot_dialog.py         # 绘图对话框
│   └── export_utils.py        # 导出工具
└── test_data/                  # 测试数据目录
    ├── sine_data_*.h5         # 正弦函数测试数据
    ├── sine_visualization_*.png # 数据可视化图像
    ├── image_test_data.h5     # 图像测试数据
    ├── test_15cols.h5         # 15列测试数据
    └── FFarData.h5           # 原始测试数据
```

## 核心模块说明

### 1. 主程序模块

- **run.py**: 程序入口点，处理命令行参数和文件加载
- **main.py**: 应用程序主类和初始化逻辑
- **mainwindow.py**: 主窗口界面，包含菜单、工具栏和布局管理

### 2. 数据模型 (models/)

- **table_models.py**: 
  - `AttributesTableModel`: HDF5属性表格模型
  - `DatasetTableModel`: 数据集信息表格模型
  - `DataTableModel`: 数据内容表格模型
  - `DimsTableModel`: 维度设置表格模型

- **tree_model.py**: HDF5文件结构树形模型
- **view_models.py**: 
  - `ImageModel`: 图像数据模型
  - `PlotModel`: 绘图数据模型

- **utils.py**: 数据处理工具函数

### 3. 视图组件 (views/)

- **hdf5_widget.py**: 主HDF5查看组件，包含所有主要功能
- **image_view.py**: 图像显示组件，支持2D/3D/4D数据
- **plot_view.py**: 数据绘图组件，支持多列数据可视化
- **plot_dialog.py**: 绘图设置对话框
- **export_utils.py**: CSV导出功能

### 4. 资源管理

- **resources.py**: 统一资源管理器，处理图标加载
- **resources.qrc**: Qt资源定义文件
- **icons/**: 所有图标文件

### 5. 工具脚本

- **generate_sine_data.py**: 正弦函数测试数据生成器
- **build_resources.py**: 资源编译脚本
- **deploy_config.py**: 部署配置管理

## 主要功能

### 1. 文件操作
- 打开HDF5文件
- 拖拽文件支持
- 最近文件列表
- 多标签页支持

### 2. 数据查看
- 树形结构浏览
- 属性查看
- 数据表格显示
- 维度设置

### 3. 数据可视化
- **绘图功能**: 支持多列数据绘图，自定义轴选择
- **图像显示**: 支持灰度/RGB/RGBA图像，多维数据浏览
- **数据导出**: CSV格式导出

### 4. 界面特性
- 现代化界面设计
- 响应式布局
- 工具栏快捷操作
- 状态栏信息显示

## 依赖库

```
PySide6>=6.0.0
h5py>=3.0.0
numpy>=1.20.0
matplotlib>=3.5.0
pyqtgraph>=0.12.0
psutil>=5.8.0
```

## 开发规范

### 1. 代码风格
- 遵循PEP 8规范
- 使用类型提示
- 详细的文档字符串
- 合理的异常处理

### 2. 文件命名
- 模块名使用小写字母和下划线
- 类名使用驼峰命名法
- 常量使用大写字母和下划线
- 测试数据文件包含时间戳

### 3. 异常处理
- 使用try-except块处理可能出现的错误
- 记录详细的错误日志
- 提供用户友好的错误信息
- 确保程序健壮性

### 4. 资源管理
- 统一的资源加载机制
- 跨平台路径处理
- 图标缓存机制

## 测试数据

项目包含多种测试数据：

1. **正弦函数数据** (`sine_data_*.h5`):
   - 简单正弦波
   - 阻尼正弦波
   - 频率调制正弦波
   - 2D正弦波图像
   - RGB正弦波图像
   - 正弦波图像序列

2. **图像测试数据** (`image_test_data.h5`):
   - 灰度图像
   - RGB图像
   - RGBA图像
   - 图像序列
   - 复杂4D数据

3. **其他测试数据**:
   - 15列数据测试
   - 原始FFar数据

## 使用说明

### 1. 基本使用
```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python run.py

# 打开特定文件
python run.py -f datafile.h5
```

### 2. 生成测试数据
```bash
# 生成正弦函数测试数据
python generate_sine_data.py
```

### 3. 构建资源
```bash
# 编译Qt资源
python build_resources.py
```

## 扩展开发

### 1. 添加新的数据模型
继承相应的基类并实现必要的方法

### 2. 添加新的视图组件
在views目录下创建新文件，继承Qt基础组件

### 3. 添加新的功能模块
遵循现有的代码结构和命名规范

## 注意事项

1. **兼容性**: 支持Python 3.8+
2. **平台**: 支持Windows、macOS、Linux
3. **内存**: 处理大文件时注意内存使用
4. **性能**: 对于大型数据集，建议使用适当的采样率

## 更新日志

- 2025-11-19: 项目结构整理，添加正弦函数数据生成器
- 2025-11-19: 优化轴选择界面，修复滚动条问题
- 2025-11-19: 添加图像显示功能
- 2025-11-19: 优化图标资源管理