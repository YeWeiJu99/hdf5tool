"""
包含绘图设置对话框类。
"""

import json
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QFileDialog,
    QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QScrollArea, QSpinBox, QVBoxLayout
)


class PlotSettingsDialog(QDialog):
    """绘图设置对话框，用于选择绘图的列和默认设置。"""
    
    def __init__(self, parent=None, column_names=None, current_x_col=0, current_y_cols=None):
        super().__init__(parent)
        self.setWindowTitle("绘图设置")
        self.setModal(True)
        
        # 获取应用程序设置
        self.settings = QSettings()
        # 初始化变量
        self.column_names = column_names if column_names else []
        self.current_x_col = current_x_col
        self.current_y_cols = current_y_cols if current_y_cols else []
        self.y_checkboxes = []

        # 创建UI
        self.init_ui()
        # 加载默认设置
        self.load_default_settings()

    def init_ui(self):
        """初始化用户界面。"""
        layout = QVBoxLayout()
        layout.setSpacing(8)  # 减小间距，使布局更紧凑

        # 创建列选择组
        column_group = QGroupBox("列选择")
        column_layout = QVBoxLayout()  # 使用 QVBoxLayout 更好控制

        # X轴选择
        x_label = QLabel("X轴数据:")
        self.x_combo = QComboBox()
        # 添加"索引"选项作为第一个选项
        all_column_names = ["索引"] + self.column_names
        self.x_combo.addItems(all_column_names)
        column_layout.addWidget(x_label)
        column_layout.addWidget(self.x_combo)

        # Y轴选择 (使用 QScrollArea 包裹，防止占用过多空间)
        y_label = QLabel("Y轴数据 (可选择多个):")
        column_layout.addWidget(y_label)

        # 创建滚动区域以容纳大量复选框
        self.y_scroll_area = QScrollArea()
        self.y_scroll_widget = QWidget()
        self.y_scroll_layout = QVBoxLayout()
        self.y_scroll_layout.setSpacing(2)  # 减小复选框间的间距
        for i, col_name in enumerate(self.column_names):
            checkbox = QCheckBox(f"{i+1}. {col_name}")
            checkbox.setStyleSheet("QCheckBox { margin-left: 20px; }")
            self.y_checkboxes.append(checkbox)
            self.y_scroll_layout.addWidget(checkbox)
        self.y_scroll_widget.setLayout(self.y_scroll_layout)
        self.y_scroll_area.setWidget(self.y_scroll_widget)
        self.y_scroll_area.setWidgetResizable(True)
        self.y_scroll_area.setMaximumHeight(150)  # 设置最大高度，强制出现滚动条
        self.y_scroll_area.setMinimumHeight(80)  # 设置最小高度
        column_layout.addWidget(self.y_scroll_area)

        column_group.setLayout(column_layout)
        layout.addWidget(column_group)

        # 创建默认设置组
        default_group = QGroupBox("默认设置")
        default_layout = QVBoxLayout()

        # 默认X轴列
        default_x_label = QLabel("默认X轴:")
        self.default_x_combo = QComboBox()
        # 添加"索引"选项作为第一个选项
        all_column_names_for_default = ["索引"] + self.column_names
        self.default_x_combo.addItems(all_column_names_for_default)
        default_layout.addWidget(default_x_label)
        default_layout.addWidget(self.default_x_combo)

        # 默认Y轴列 (同样使用滚动区域)
        default_y_label = QLabel("默认Y轴 (可选择多个):")
        default_layout.addWidget(default_y_label)

        self.default_y_scroll_area = QScrollArea()
        self.default_y_scroll_widget = QWidget()
        self.default_y_scroll_layout = QVBoxLayout()
        self.default_y_scroll_layout.setSpacing(2)
        self.default_y_checkboxes = []
        for i, col_name in enumerate(self.column_names):
            checkbox = QCheckBox(f"{i+1}. {col_name}")
            checkbox.setStyleSheet("QCheckBox { margin-left: 20px; }")
            self.default_y_checkboxes.append(checkbox)
            self.default_y_scroll_layout.addWidget(checkbox)
        self.default_y_scroll_widget.setLayout(self.default_y_scroll_layout)
        self.default_y_scroll_area.setWidget(self.default_y_scroll_widget)
        self.default_y_scroll_area.setWidgetResizable(True)
        self.default_y_scroll_area.setMaximumHeight(100)
        self.default_y_scroll_area.setMinimumHeight(60)
        default_layout.addWidget(self.default_y_scroll_area)

        # 点数量设置
        points_label = QLabel("显示点数:")
        points_control_layout = QHBoxLayout()
        self.points_spinbox = QSpinBox()
        self.points_spinbox.setMinimum(10)
        self.points_spinbox.setMaximum(10000)
        self.points_spinbox.setValue(1000)
        points_control_layout.addWidget(self.points_spinbox)
        # 将点数标签和控制布局放在一行
        points_row_layout = QHBoxLayout()
        points_row_layout.addWidget(points_label)
        points_row_layout.addLayout(points_control_layout)
        default_layout.addLayout(points_row_layout)

        default_group.setLayout(default_layout)
        layout.addWidget(default_group)

        # 按钮组 - 放在布局底部，使用水平布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(4)  # 减小按钮间距

        # 添加自定义标签按钮
        self.custom_label_button = QPushButton("自定义标签")
        self.custom_label_button.clicked.connect(self.show_custom_label_dialog)
        button_layout.addWidget(self.custom_label_button)

        # 应用、保存为默认、导出图片按钮
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)

        self.save_default_button = QPushButton("保存为默认")
        self.save_default_button.clicked.connect(self.save_default_settings)
        button_layout.addWidget(self.save_default_button)

        self.export_image_button = QPushButton("导出图片")
        self.export_image_button.clicked.connect(self.export_image)
        button_layout.addWidget(self.export_image_button)

        # 全选、清除、取消按钮
        self.select_all_button = QPushButton("全选Y轴")
        self.select_all_button.clicked.connect(self.select_all_y_columns)
        button_layout.addWidget(self.select_all_button)

        self.clear_all_button = QPushButton("清除Y轴")
        self.clear_all_button.clicked.connect(self.clear_all_y_columns)
        button_layout.addWidget(self.clear_all_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        # 将按钮布局添加到主布局
        layout.addLayout(button_layout)

        # 在最后添加一个拉伸弹簧，将上面的内容推到顶部，确保按钮始终在底部可见
        layout.addStretch()

        self.setLayout(layout)

    def load_default_settings(self):
        """加载默认设置。"""
        # 加载默认X轴列
        default_x_col_from_settings = self.settings.value("plot/default_x_column", 0, type=int)
        # 将 -1 (索引) 映射到 combo 的 0, 其他 0,1,2... 映射到 combo 的 1,2,3...
        combo_index = 0 if default_x_col_from_settings == -1 else default_x_col_from_settings + 1
        if combo_index < self.default_x_combo.count():
            self.default_x_combo.setCurrentIndex(combo_index)

        # 加载默认Y轴列
        default_y_cols_str = self.settings.value("plot/default_y_columns", "")
        if default_y_cols_str:
            try:
                default_y_cols = [int(x) for x in default_y_cols_str.split(",") if x.strip()]
            except:
                default_y_cols = []
        else:
            default_y_cols = []
        for i, checkbox in enumerate(self.default_y_checkboxes):
            if i in default_y_cols and i < len(self.column_names):
                checkbox.setChecked(True)

        # 加载默认点数量
        default_points = self.settings.value("plot/default_points", 1000, type=int)
        self.points_spinbox.setValue(default_points)

        # 应用默认设置到当前选择
        self.apply_default_to_current()

    def apply_default_to_current(self):
        """将默认设置应用到当前选择。"""
        # 设置当前X轴
        combo_index = self.default_x_combo.currentIndex()
        # 将 combo 的 0 (索引) 映射到 -1, 其他 1,2,3... 映射到 0,1,2...
        x_idx = -1 if combo_index == 0 else combo_index - 1
        # 查找 x_idx 对应的 combo 索引
        target_combo_idx = 0 if x_idx == -1 else x_idx + 1
        if target_combo_idx < self.x_combo.count():
            self.x_combo.setCurrentIndex(target_combo_idx)

        # 设置当前Y轴
        for i, checkbox in enumerate(self.y_checkboxes):
            if i < len(self.default_y_checkboxes):
                checkbox.setChecked(self.default_y_checkboxes[i].isChecked())

    def apply_settings(self):
        """应用设置并关闭对话框。"""
        # 获取选择的X轴列
        x_combo_index = self.x_combo.currentIndex()
        # 如果选择的是"索引"(第一个选项)，则 x_col_index 为 0，映射到 -1
        # 否则，x_col_index 从 1 开始，映射到 0, 1, 2... (对应 column_names 的索引)
        self.current_x_col = -1 if x_combo_index == 0 else x_combo_index - 1

        # 获取选择的Y轴列
        self.current_y_cols = []
        for i, checkbox in enumerate(self.y_checkboxes):
            if checkbox.isChecked():
                self.current_y_cols.append(i)

        # 如果没有选择Y轴，则选择除X轴外的所有列
        if not self.current_y_cols:
            for i in range(len(self.column_names)):
                if i != self.current_x_col and self.current_x_col != -1:  # 如果X轴是索引，则不排除任何Y轴
                    self.current_y_cols.append(i)
                elif self.current_x_col == -1:  # 如果X轴是索引，则选择所有列
                    self.current_y_cols = list(range(len(self.column_names)))
                    break
        self.accept()

    def save_default_settings(self):
        """保存默认设置。"""
        # 保存默认X轴列
        combo_index = self.default_x_combo.currentIndex()
        # 将 combo 的 0 (索引) 映射到 -1，将 1, 2, 3... 映射到 0, 1, 2...
        default_x_col_for_settings = -1 if combo_index == 0 else combo_index - 1
        self.settings.setValue("plot/default_x_column", default_x_col_for_settings)

        # 保存默认Y轴列
        default_y_cols = []
        for i, checkbox in enumerate(self.default_y_checkboxes):
            if checkbox.isChecked():
                default_y_cols.append(i)
        # 将列表转换为逗号分隔的字符串
        self.settings.setValue("plot/default_y_columns", ",".join(map(str, default_y_cols)))

        # 保存默认点数量
        self.settings.setValue("plot/default_points", self.points_spinbox.value())

        QMessageBox.information(self, "设置已保存", "默认设置已保存。")

    def select_all_y_columns(self):
        """全选Y轴列。"""
        for checkbox in self.y_checkboxes:
            checkbox.setChecked(True)

    def clear_all_y_columns(self):
        """清除所有Y轴列选择。"""
        for checkbox in self.y_checkboxes:
            checkbox.setChecked(False)

    def get_settings(self):
        """获取当前设置。"""
        return {
            'x_column': self.current_x_col,
            'y_columns': self.current_y_cols,
            'points': self.points_spinbox.value(),
            'custom_title': getattr(self, 'custom_title', ""),
            'custom_x_label': getattr(self, 'custom_x_label', ""),
            'custom_y_label': getattr(self, 'custom_y_label', "")
        }

    def show_custom_label_dialog(self):
        """显示自定义标签对话框。"""
        dialog = QDialog(self)
        dialog.setWindowTitle("自定义标签")
        dialog.setModal(True)
        layout = QFormLayout()

        # 自定义标题
        title_label = QLabel("图表标题:")
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("留空使用默认标题")
        layout.addRow(title_label, self.title_edit)

        # 自定义X轴标签
        x_label_label = QLabel("X轴标签:")
        self.x_label_edit = QLineEdit()
        self.x_label_edit.setPlaceholderText("留空使用默认标签")
        layout.addRow(x_label_label, self.x_label_edit)

        # 自定义Y轴标签
        y_label_label = QLabel("Y轴标签:")
        self.y_label_edit = QLineEdit()
        self.y_label_edit.setPlaceholderText("留空使用默认标签")
        layout.addRow(y_label_label, self.y_label_edit)

        # 确认按钮
        confirm_button = QPushButton("确认")
        confirm_button.clicked.connect(lambda: self.save_custom_labels(dialog))
        layout.addRow(confirm_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def save_custom_labels(self, dialog):
        """保存自定义标签设置。"""
        self.custom_title = self.title_edit.text().strip()
        self.custom_x_label = self.x_label_edit.text().strip()
        self.custom_y_label = self.y_label_edit.text().strip()
        dialog.close()

    def export_image(self):
        """导出当前绘图为图片。"""
        # 获取父窗口中的绘图视图
        parent = self.parent()
        if hasattr(parent, 'plot_views') and parent.plot_views:
            # 获取第一个绘图视图
            plot_view = list(parent.plot_views.values())[0]
            if hasattr(plot_view, 'plot_item'):
                # 打开文件对话框选择保存位置
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "导出图片",
                    "",
                    "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;All Files (*)"
                )
                if file_path:
                    try:
                        # 使用pyqtgraph的导出功能 - 修复导出器导入
                        from pyqtgraph import exporters
                        exporter = exporters.ImageExporter(plot_view.plot_item)
                        exporter.export(file_path)
                        QMessageBox.information(self, "导出成功", f"图片已导出到: {file_path}")
                    except Exception as e:
                        QMessageBox.warning(self, "导出失败", f"导出图片时出错: {str(e)}")
            else:
                QMessageBox.warning(self, "导出失败", "未找到可导出的绘图")
        else:
            QMessageBox.warning(self, "导出失败", "未找到可导出的绘图")