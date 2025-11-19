# HDF5Tool - HDF5数据可视化工具

一个基于PySide6的HDF5文件可视化工具，提供直观的界面来查看、分析和导出HDF5数据。

## 🚀 功能特性

- 📁 **文件结构浏览** - 树形视图展示HDF5文件层次结构
- 📊 **数据表格查看** - 表格形式显示数据集内容
- 📈 **交互式数据绘图** - 支持多种图表类型和自定义配置
- 🖼️ **图像显示** - 支持2D/3D图像数据集的可视化
- 📤 **数据导出** - 将数据导出为CSV格式
- 🔍 **数据切片** - 支持多维数据的切片查看
- 🎯 **命令行接口** - 支持通过命令行直接打开文件

## 📦 安装方法

### 方法一：从源码安装（推荐）

```bash
# 克隆项目
git clone <项目地址>
cd hd5ftool

# 安装为可执行包
pip install -e . -i https://pypi.mirrors.ustc.edu.cn/simple/
```

### 方法二：直接运行源码

```bash
# 安装依赖
pip install -r requirements.txt

# 直接运行
python run.py
```

## 🛠️ 依赖库

项目依赖以下Python包：

```txt
PySide6>=6.4.0        # GUI框架
h5py>=3.7.0          # HDF5文件操作
pyqtgraph>=0.13.0    # 数据绘图
psutil>=5.9.0        # 系统信息
pandas>=1.5.0		# CSV导出
```

安装依赖：
```bash
pip install PySide6 h5py pyqtgraph psutil pandas
```

## 🎮 使用方法

### 命令行使用

```bash
# 显示帮助信息
hdf5tool --help

# 打开单个HDF5文件
hdf5tool -f "path/to/your/file.h5"

# 打开多个HDF5文件
hdf5tool -f file1.h5 -f file2.h5 -f file3.h5

# 使用通配符打开所有h5文件
hdf5tool -f "*.h5"

# 跳过文件格式检查
hdf5tool -f "your_file.h5" --no-format-check
```

### 作为Python模块使用

```bash
# 作为模块运行
python -m hdf5tool -f "your_file.h5"

# 直接运行源码
python run.py -f "your_file.h5"
```

### 图形界面操作

1. **打开文件**：通过菜单栏"文件"→"打开"或工具栏打开按钮
2. **浏览结构**：左侧树形视图显示HDF5文件层次
3. **查看数据**：双击数据集在右侧查看表格内容
4. **绘制图表**：选择数据集后点击"绘图"按钮
5. **查看图像**：支持2D/3D图像数据集的显示
6. **导出数据**：选择数据集后导出为CSV格式

## 📁 项目结构

```
hd5ftool/
├── run.py              # 主启动脚本
├── __main__.py         # 包入口点
├── setup.py            # 包安装配置
├── requirements.txt    # 依赖包列表
├── MANIFEST.in         # 包资源清单
├── README.md           # 项目说明文档
├── src/               # 源代码目录
│   ├── main.py        # 应用程序入口
│   ├── mainwindow.py  # 主窗口实现
│   ├── models/        # 数据模型
│   │   ├── __init__.py
│   │   ├── table_models.py
│   │   ├── tree_model.py
│   │   ├── utils.py
│   │   └── view_models.py
│   ├── views/         # 视图组件
│   │   ├── __init__.py
│   │   ├── hdf5_widget.py
│   │   ├── plot_dialog.py
│   │   ├── image_view.py
│   │   ├── plot_view.py
│   │   └── export_utils.py
│   ├── resources.py   # 资源管理
│   ├── resources.qrc  # Qt资源文件
│   └── icons/         # 图标资源
├── config/            # 配置文件
│   ├── deploy_config.py
│   └── plot_config.json
├── scripts/           # 工具脚本
│   ├── build_resources.py
│   └── generate_sine_data.py
├── docs/              # 文档
│   └── HDF5_IMAGE_FORMAT.md
└── data/              # 测试数据
    └── *.h5           # HDF5测试文件
```

## 🔧 开发说明

### 构建Qt资源

```bash
# 编译Qt资源文件
python scripts/build_resources.py --compile
```

### 生成测试数据

```bash
# 生成正弦波测试数据
python scripts/generate_sine_data.py
```

### 项目架构

项目采用模块化设计：

- **models/** - 数据模型层，处理HDF5数据结构
- **views/** - 视图层，实现用户界面组件
- **config/** - 配置文件，部署和应用配置
- **scripts/** - 工具脚本，构建和数据处理

## 📚 相关文档

- [HDF5图像格式说明](docs/HDF5_IMAGE_FORMAT.md) - 如何将图像正确保存为HDF5格式

## 🐛 常见问题

### Q: 命令行工具无法识别？
A: 确保已正确安装包：`pip install -e .`

### Q: 打开文件时提示格式错误？
A: 使用 `--no-format-check` 参数跳过格式检查

### Q: 如何查看帮助信息？
A: 运行 `hdf5tool --help` 或 `python run.py --help`

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

---

**版本**: 1.0.0  
**最后更新**: 2025年11月