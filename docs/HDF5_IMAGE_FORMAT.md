# HDF5图像格式说明

## 概述

HDF5Tool可以正确显示存储在HDF5文件中的图像数据。要让图像在该程序中可见，需要按照特定的格式要求保存数据。

## 图像数据格式要求

### 1. 数据维度

- **2D图像**: `(height, width)` - 灰度图像
- **3D图像**: `(height, width, channels)` - 彩色图像
  - `channels = 1`: 灰度图像
  - `channels = 3`: RGB图像
  - `channels = 4`: RGBA图像

### 2. 数据类型

支持以下数据类型：
- `uint8` - 8位无符号整数 (0-255)
- `uint16` - 16位无符号整数 (0-65535)
- `float32` - 32位浮点数
- `float64` - 64位浮点数

### 3. 最小尺寸要求

- 最小图像尺寸: `10 x 10` 像素
- 推荐尺寸: `100 x 100` 像素以上

## matplotlib图像保存为HDF5的方法

### 方法1: 直接保存渲染结果

```python
import numpy as np
import h5py
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

# 创建matplotlib图形
fig, ax = plt.subplots(figsize=(8, 6))
x = np.linspace(0, 10, 1000)
y = np.sin(2 * np.pi * x)
ax.plot(x, y, 'b-', linewidth=2)
ax.set_title("正弦波")
ax.set_xlabel("时间 (s)")
ax.set_ylabel("振幅")
ax.grid(True)

# 渲染为numpy数组
fig.canvas.draw()
# 获取RGB图像数据
image_array = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
image_array = image_array.reshape(fig.canvas.get_width_height()[::-1] + (3,))

# 保存到HDF5
with h5py.File('output.h5', 'w') as f:
    f.create_dataset('sine_wave_image', data=image_array, compression='gzip')
    
    # 添加有用的属性
    f['sine_wave_image'].attrs['description'] = '正弦波matplotlib图像'
    f['sine_wave_image'].attrs['creation_time'] = '2025-11-19T20:50:00'
    f['sine_wave_image'].attrs['image_type'] = 'rgb'

plt.close(fig)
```

### 方法2: 使用缓冲区保存

```python
import io
import numpy as np
import h5py
import matplotlib.pyplot as plt
from PIL import Image

# 创建图形
fig, ax = plt.subplots(figsize=(10, 6))
# ... 绘图代码 ...

# 保存到内存缓冲区
buf = io.BytesIO()
fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
buf.seek(0)

# 使用PIL读取并转换为numpy数组
img = Image.open(buf)
image_array = np.array(img)

# 如果是RGBA，转换为RGB
if image_array.shape[2] == 4:
    image_array = image_array[:, :, :3]

# 保存到HDF5
with h5py.File('output.h5', 'w') as f:
    f.create_dataset('plot_image', data=image_array, compression='gzip')

buf.close()
plt.close(fig)
```

### 方法3: 手动创建图像数据

```python
import numpy as np
import h5py

# 创建自定义图像数据
height, width = 500, 800
image_array = np.zeros((height, width, 3), dtype=np.uint8)

# 绘制简单的正弦波
x = np.linspace(0, 4*np.pi, width)
for i in range(height):
    y = int(height/2 + 100 * np.sin(x + i * 0.02))
    if 0 <= y < height:
        image_array[i, y-2:y+2, :] = [255, 0, 0]  # 红色线条

# 添加背景
image_array[:, :, 1] = 50  # 绿色背景
image_array[:, :, 2] = 50  # 蓝色背景

# 保存到HDF5
with h5py.File('output.h5', 'w') as f:
    f.create_dataset('custom_sine_image', data=image_array, compression='gzip')
```

## 推荐的HDF5图像结构

### 基本结构

```python
with h5py.File('images.h5', 'w') as f:
    # 图像数据集
    f.create_dataset('image_name', data=image_array, compression='gzip')
    
    # 推荐属性
    f['image_name'].attrs.update({
        'description': '图像描述',
        'creation_time': '2025-11-19T20:50:00',
        'image_type': 'rgb',  # 'rgb', 'rgba', 'grayscale'
        'width': image_array.shape[1],
        'height': image_array.shape[0],
        'channels': image_array.shape[2] if len(image_array.shape) > 2 else 1,
        'dpi': 150,
        'source': 'matplotlib'
    })
```

### 多图像文件结构

```python
with h5py.File('multi_images.h5', 'w') as f:
    # 多个相关图像
    images = {
        'plot_1': plot1_array,
        'plot_2': plot2_array,
        'plot_3': plot3_array
    }
    
    for name, img in images.items():
        f.create_dataset(name, data=img, compression='gzip')
        f[name].attrs['description'] = f'图像 {name}'
        f[name].attrs['creation_time'] = '2025-11-19T20:50:00'
    
    # 添加元数据组
    metadata_group = f.create_group('metadata')
    metadata_group.attrs['total_images'] = len(images)
    metadata_group.attrs['created_by'] = 'matplotlib_script'
```

## 常见问题

### 1. 图像不显示

**原因**: 数据维度不正确
**解决**: 确保数据是2D或3D数组，3D数组的最后一维是通道数

### 2. 颜色异常

**原因**: 数据类型或通道顺序不正确
**解决**: 
- 使用uint8类型，值范围0-255
- 确保RGB顺序正确

### 3. 图像尺寸问题

**原因**: 图像太小或太大
**解决**: 
- 最小尺寸10x10像素
- 考虑使用压缩减少文件大小

### 4. 内存问题

**原因**: 图像数据过大
**解决**: 
- 使用数据压缩
- 考虑降低分辨率
- 分块保存大型图像序列

## 验证工具

使用以下代码验证HDF5图像格式：

```python
import h5py
import numpy as np

def validate_hdf5_image(filename, dataset_name):
    """验证HDF5中的图像数据格式"""
    try:
        with h5py.File(filename, 'r') as f:
            if dataset_name not in f:
                return False, f"数据集 '{dataset_name}' 不存在"
            
            dataset = f[dataset_name]
            data = dataset[()]
            
            # 检查维度
            if len(data.shape) < 2:
                return False, f"数据维度不足: {len(data.shape)}D"
            
            # 检查尺寸
            if data.shape[0] < 10 or data.shape[1] < 10:
                return False, f"图像尺寸过小: {data.shape}"
            
            # 检查通道数
            if len(data.shape) == 3 and data.shape[2] not in [1, 3, 4]:
                return False, f"不支持的通道数: {data.shape[2]}"
            
            # 检查数据类型
            if data.dtype not in [np.uint8, np.uint16, np.float32, np.float64]:
                return False, f"不支持的数据类型: {data.dtype}"
            
            return True, f"图像格式正确: {data.shape}, {data.dtype}"
            
    except Exception as e:
        return False, f"验证失败: {str(e)}"

# 使用示例
is_valid, message = validate_hdf5_image('output.h5', 'sine_wave_image')
print(f"验证结果: {message}")
```

## 最佳实践

1. **使用压缩**: `compression='gzip'` 可以显著减少文件大小
2. **添加元数据**: 包含创建时间、描述等有用信息
3. **合理尺寸**: 平衡图像质量和文件大小
4. **一致命名**: 使用有意义的数据集名称
5. **验证格式**: 保存前验证数据格式是否正确

通过遵循这些指南，您可以创建与HDF5Tool完全兼容的图像文件。