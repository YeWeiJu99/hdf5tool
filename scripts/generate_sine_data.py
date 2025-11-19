#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正弦函数图像数据生成器

该脚本使用matplotlib生成各种正弦函数图像，并将数据保存为HDF5格式。
生成的数据包括：
1. 简单正弦波
2. 阻尼正弦波
3. 频率调制正弦波
4. 多通道正弦波（RGB）
5. 正弦波图像序列

作者: HDF5Tool
创建时间: 2025-11-19
"""

import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SineDataGenerator:
    """正弦函数数据生成器类"""
    
    def __init__(self, output_dir="../data"):
        """
        初始化生成器
        
        Args:
            output_dir (str): 输出目录路径
        """
        self.output_dir = output_dir
        self.ensure_output_dir()
        
    def ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"创建输出目录: {self.output_dir}")
    
    def generate_simple_sine(self, samples=1000, frequency=1.0, amplitude=1.0, phase=0.0):
        """
        生成简单正弦波数据
        
        Args:
            samples (int): 采样点数
            frequency (float): 频率 (Hz)
            amplitude (float): 振幅
            phase (float): 相位 (弧度)
            
        Returns:
            tuple: (时间数组, 正弦波数组)
        """
        try:
            t = np.linspace(0, 4*np.pi, samples)
            y = amplitude * np.sin(2 * np.pi * frequency * t + phase)
            logger.info(f"生成简单正弦波: 频率={frequency}Hz, 振幅={amplitude}, 采样点={samples}")
            return t, y
        except Exception as e:
            logger.error(f"生成简单正弦波时出错: {e}")
            raise
    
    def generate_damped_sine(self, samples=1000, frequency=1.0, amplitude=1.0, damping=0.1):
        """
        生成阻尼正弦波数据
        
        Args:
            samples (int): 采样点数
            frequency (float): 频率 (Hz)
            amplitude (float): 初始振幅
            damping (float): 阻尼系数
            
        Returns:
            tuple: (时间数组, 阻尼正弦波数组)
        """
        try:
            t = np.linspace(0, 4*np.pi, samples)
            y = amplitude * np.exp(-damping * t) * np.sin(2 * np.pi * frequency * t)
            logger.info(f"生成阻尼正弦波: 频率={frequency}Hz, 阻尼={damping}")
            return t, y
        except Exception as e:
            logger.error(f"生成阻尼正弦波时出错: {e}")
            raise
    
    def generate_frequency_modulated_sine(self, samples=1000, carrier_freq=5.0, mod_freq=0.5):
        """
        生成频率调制正弦波数据
        
        Args:
            samples (int): 采样点数
            carrier_freq (float): 载波频率 (Hz)
            mod_freq (float): 调制频率 (Hz)
            
        Returns:
            tuple: (时间数组, 调频正弦波数组)
        """
        try:
            t = np.linspace(0, 4*np.pi, samples)
            # 频率调制: 瞬时频率随时间变化
            instantaneous_freq = carrier_freq + mod_freq * np.sin(2 * np.pi * mod_freq * t)
            phase = 2 * np.pi * np.cumsum(instantaneous_freq) / samples
            y = np.sin(phase)
            logger.info(f"生成调频正弦波: 载频={carrier_freq}Hz, 调频={mod_freq}Hz")
            return t, y
        except Exception as e:
            logger.error(f"生成调频正弦波时出错: {e}")
            raise
    
    def generate_2d_sine_image(self, width=200, height=200, freq_x=2.0, freq_y=3.0):
        """
        生成2D正弦波图像数据
        
        Args:
            width (int): 图像宽度
            height (int): 图像高度
            freq_x (float): X方向频率
            freq_y (float): Y方向频率
            
        Returns:
            numpy.ndarray: 2D正弦波图像数组
        """
        try:
            x = np.linspace(0, 2*np.pi, width)
            y = np.linspace(0, 2*np.pi, height)
            X, Y = np.meshgrid(x, y)
            Z = np.sin(freq_x * X) * np.cos(freq_y * Y)
            # 归一化到0-255范围
            Z_normalized = ((Z + 1) * 127.5).astype(np.uint8)
            logger.info(f"生成2D正弦波图像: {width}x{height}, 频率({freq_x}, {freq_y})")
            return Z_normalized
        except Exception as e:
            logger.error(f"生成2D正弦波图像时出错: {e}")
            raise
    
    def generate_rgb_sine_image(self, width=200, height=200):
        """
        生成RGB正弦波图像数据
        
        Args:
            width (int): 图像宽度
            height (int): 图像高度
            
        Returns:
            numpy.ndarray: RGB正弦波图像数组 (height x width x 3)
        """
        try:
            # 生成不同频率的正弦波作为RGB三个通道
            red_channel = self.generate_2d_sine_image(width, height, freq_x=2.0, freq_y=1.0)
            green_channel = self.generate_2d_sine_image(width, height, freq_x=3.0, freq_y=2.0)
            blue_channel = self.generate_2d_sine_image(width, height, freq_x=1.0, freq_y=3.0)
            
            # 组合为RGB图像
            rgb_image = np.stack([red_channel, green_channel, blue_channel], axis=2)
            logger.info(f"生成RGB正弦波图像: {width}x{height}x3")
            return rgb_image
        except Exception as e:
            logger.error(f"生成RGB正弦波图像时出错: {e}")
            raise
    
    def generate_sine_sequence(self, frames=20, width=150, height=150):
        """
        生成正弦波图像序列
        
        Args:
            frames (int): 帧数
            width (int): 图像宽度
            height (int): 图像高度
            
        Returns:
            numpy.ndarray: 正弦波图像序列 (frames x height x width)
        """
        try:
            sequence = np.zeros((frames, height, width), dtype=np.uint8)
            for i in range(frames):
                # 每帧使用不同的相位
                phase_shift = i * 2 * np.pi / frames
                x = np.linspace(0, 2*np.pi, width)
                y = np.linspace(0, 2*np.pi, height)
                X, Y = np.meshgrid(x, y)
                Z = np.sin(2 * X + phase_shift) * np.cos(2 * Y)
                sequence[i] = ((Z + 1) * 127.5).astype(np.uint8)
            
            logger.info(f"生成正弦波序列: {frames}帧, {width}x{height}")
            return sequence
        except Exception as e:
            logger.error(f"生成正弦波序列时出错: {e}")
            raise
    
    def save_to_hdf5(self, data_dict, filename):
        """
        将数据保存到HDF5文件
        
        Args:
            data_dict (dict): 数据字典，键为数据集名称，值为数据数组
            filename (str): 输出文件名
        """
        try:
            filepath = os.path.join(self.output_dir, filename)
            with h5py.File(filepath, 'w') as f:
                for name, data in data_dict.items():
                    dataset = f.create_dataset(name, data=data)
                    # 添加属性
                    dataset.attrs['creation_time'] = datetime.now().isoformat()
                    dataset.attrs['data_type'] = 'sine_wave'
                    dataset.attrs['shape'] = str(data.shape)
                    
                    # 根据数据类型添加特定属性
                    if 'simple' in name:
                        dataset.attrs['description'] = '简单正弦波数据'
                    elif 'damped' in name:
                        dataset.attrs['description'] = '阻尼正弦波数据'
                    elif 'modulated' in name:
                        dataset.attrs['description'] = '频率调制正弦波数据'
                    elif 'image_2d' in name:
                        dataset.attrs['description'] = '2D正弦波图像'
                        dataset.attrs['image_type'] = 'grayscale'
                    elif 'image_rgb' in name:
                        dataset.attrs['description'] = 'RGB正弦波图像'
                        dataset.attrs['image_type'] = 'rgb'
                    elif 'sequence' in name:
                        dataset.attrs['description'] = '正弦波图像序列'
                        dataset.attrs['frame_count'] = data.shape[0]
            
            logger.info(f"数据已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"保存HDF5文件时出错: {e}")
            raise
    
    def generate_all_data(self):
        """生成所有类型的正弦波数据并保存"""
        try:
            logger.info("开始生成正弦波数据...")
            
            # 生成1D数据
            t1, y1 = self.generate_simple_sine(samples=1000, frequency=2.0)
            t2, y2 = self.generate_damped_sine(samples=1000, frequency=3.0, damping=0.05)
            t3, y3 = self.generate_frequency_modulated_sine(samples=1000, carrier_freq=5.0)
            
            # 生成2D图像数据
            img_2d = self.generate_2d_sine_image(width=200, height=200)
            img_rgb = self.generate_rgb_sine_image(width=200, height=200)
            img_sequence = self.generate_sine_sequence(frames=15, width=150, height=150)
            
            # 创建结构化数组用于1D数据
            dtype1d = [('time', 'f8'), ('simple_sine', 'f8'), ('damped_sine', 'f8'), ('modulated_sine', 'f8')]
            structured_data = np.zeros(len(t1), dtype=dtype1d)
            structured_data['time'] = t1
            structured_data['simple_sine'] = y1
            structured_data['damped_sine'] = y2[:len(t1)]  # 确保长度一致
            structured_data['modulated_sine'] = y3[:len(t1)]
            
            # 准备数据字典
            data_dict = {
                'sine_waves_1d': structured_data,
                'sine_image_2d': img_2d,
                'sine_image_rgb': img_rgb,
                'sine_image_sequence': img_sequence
            }
            
            # 生成带时间戳的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sine_data_{timestamp}.h5"
            
            # 保存数据
            filepath = self.save_to_hdf5(data_dict, filename)
            
            # 创建可视化图像（可选）
            self.create_visualization_plots(t1, y1, y2, y3, img_2d, timestamp)
            
            logger.info(f"所有数据生成完成！文件保存为: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"生成数据时出错: {e}")
            raise
    
    def create_visualization_plots(self, t, y1, y2, y3, img_2d, timestamp):
        """创建可视化图像并保存"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            
            # 简单正弦波
            axes[0, 0].plot(t, y1, 'b-', linewidth=2)
            axes[0, 0].set_title('简单正弦波')
            axes[0, 0].set_xlabel('时间')
            axes[0, 0].set_ylabel('振幅')
            axes[0, 0].grid(True)
            
            # 阻尼正弦波
            axes[0, 1].plot(t, y2[:len(t)], 'r-', linewidth=2)
            axes[0, 1].set_title('阻尼正弦波')
            axes[0, 1].set_xlabel('时间')
            axes[0, 1].set_ylabel('振幅')
            axes[0, 1].grid(True)
            
            # 调频正弦波
            axes[1, 0].plot(t, y3[:len(t)], 'g-', linewidth=2)
            axes[1, 0].set_title('频率调制正弦波')
            axes[1, 0].set_xlabel('时间')
            axes[1, 0].set_ylabel('振幅')
            axes[1, 0].grid(True)
            
            # 2D正弦波图像
            im = axes[1, 1].imshow(img_2d, cmap='viridis', aspect='auto')
            axes[1, 1].set_title('2D正弦波图像')
            axes[1, 1].set_xlabel('X')
            axes[1, 1].set_ylabel('Y')
            plt.colorbar(im, ax=axes[1, 1])
            
            plt.tight_layout()
            
            # 保存可视化图像
            viz_filename = f"sine_visualization_{timestamp}.png"
            viz_path = os.path.join(self.output_dir, viz_filename)
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"可视化图像已保存: {viz_path}")
            
        except Exception as e:
            logger.error(f"创建可视化图像时出错: {e}")
            # 不抛出异常，因为这不是核心功能


def main():
    """主函数"""
    try:
        # 创建生成器实例
        generator = SineDataGenerator()
        
        # 生成所有数据
        output_file = generator.generate_all_data()
        
        print("=" * 60)
        print("正弦函数数据生成完成！")
        print(f"输出文件: {output_file}")
        print("=" * 60)
        
        return output_file
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        return None


if __name__ == "__main__":
    main()