"""
包含导出功能的工具类。
"""

import os
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QMessageBox


class ExportUtils:
    """包含导出功能的工具类，提供CSV导出和图片导出功能。"""
    
    @staticmethod
    def export_to_csv(data_model, hdf_widget, path=None):
        """将当前表格数据导出为CSV文件。
        
        参数:
            data_model: 数据表格模型
            hdf_widget: HDF5小部件引用
            path: 可选，导出路径
            
        返回:
            None
        """
        # 检查是否有数据可导出
        if data_model.node is None:
            QMessageBox.warning(hdf_widget, "警告", "没有可导出的数据！")
            return

        # 获取当前选中的节点路径
        current_index = hdf_widget.tree_view.currentIndex()
        if not current_index.isValid():
            QMessageBox.warning(hdf_widget, "警告", "请先选择要导出的数据集！")
            return

        if not path:
            node_path = hdf_widget.tree_model.itemFromIndex(current_index).data(Qt.UserRole)
            if not node_path:
                QMessageBox.warning(hdf_widget, "警告", "无法获取数据集路径！")
                return
            dataset_name = os.path.basename(node_path)

            # 打开文件保存对话框
            path, _ = QFileDialog.getSaveFileName(
                hdf_widget,
                "导出CSV文件",
                f"{dataset_name}.csv",
                "CSV文件 (*.csv);;所有文件 (*.*)"
            )
            
        if not path:  # 用户取消了保存
            return

        try:
            # 获取表格数据
            data = data_model.data_view
            rows = data_model.row_count
            cols = data_model.column_count

            # 创建DataFrame
            if data_model.compound_names:
                # 复合数据类型
                column_names = data_model.compound_names
                df_data = {}
                for i, col_name in enumerate(column_names):
                    if data.ndim == 0:
                        df_data[col_name] = [data[col_name]]
                    else:
                        df_data[col_name] = [data[row][col_name] for row in range(rows)]
                df = pd.DataFrame(df_data)
            else:
                # 简单数据类型
                if data.ndim == 0:
                    # 标量值
                    df = pd.DataFrame([[data]])
                elif data.ndim == 1:
                    # 一维数组
                    df = pd.DataFrame(data.reshape(-1, 1))
                else:
                    # 二维数组
                    df = pd.DataFrame(data)

            # 导出到CSV，确保正确处理中文
            df.to_csv(path, index=False, encoding='utf-8-sig')
            QMessageBox.information(
                hdf_widget,
                "导出成功",
                f"数据已成功导出到:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(
                hdf_widget,
                "导出失败",
                f"导出数据时发生错误:\n{str(e)}"
            )
    
    @staticmethod
    def export_plot_image(plot_view, parent_widget, path=None):
        """导出当前绘图为图片。
        
        参数:
            plot_view: 绘图视图
            parent_widget: 父窗口小部件
            path: 可选，导出路径
            
        返回:
            None
        """
        if not plot_view or not hasattr(plot_view, 'plot_item'):
            QMessageBox.warning(parent_widget, "导出失败", "未找到可导出的绘图")
            return
        
        if not path:
            # 打开文件对话框选择保存位置
            path, _ = QFileDialog.getSaveFileName(
                parent_widget,
                "导出图片",
                "",
                "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;All Files (*)"
            )
        
        if path:
            try:
                # 使用pyqtgraph的导出功能
                from pyqtgraph import exporters
                exporter = exporters.ImageExporter(plot_view.plot_item)
                exporter.export(path)
                QMessageBox.information(parent_widget, "导出成功", f"图片已导出到: {path}")
            except Exception as e:
                QMessageBox.warning(parent_widget, "导出失败", f"导出图片时出错: {str(e)}")