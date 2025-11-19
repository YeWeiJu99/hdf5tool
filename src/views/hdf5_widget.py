"""
包含HDF5主视图容器小部件。
"""

import h5py
import os
import psutil
from PySide6.QtCore import QModelIndex, Qt, QSettings
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QDialog,
    QFileDialog, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QScrollBar, QSpinBox, QTabBar, QTableView, QTabWidget,
    QTreeView, QVBoxLayout, QWidget, QFormLayout, QMenu, QScrollArea,
    QHeaderView, QSizePolicy, QGridLayout
)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models import (
    AttributesTableModel, DatasetTableModel, DataTableModel,
    DimsTableModel, PlotModel, TreeModel, ImageModel
)
from .plot_dialog import PlotSettingsDialog
from .image_view import ImageView
from .plot_view import PlotView
from .export_utils import ExportUtils


class HDF5Widget(QWidget):
    """主HDF5视图容器小部件。"""
    def __init__(self, hdf):
        super().__init__()
        self.hdf = hdf
        self.plot_views = {}
        self.image_views = {}

        # 初始化模型
        self.tree_model = TreeModel(self.hdf)
        self.attrs_model = AttributesTableModel(self.hdf)
        self.dataset_model = DatasetTableModel(self.hdf)
        self.dims_model = DimsTableModel(self.hdf)
        self.data_model = DataTableModel(self.hdf)
        self.plot_model = PlotModel(self.hdf)
        self.image_model = None  # 将在需要时初始化

        # 设置主文件树视图
        self.tree_view = QTreeView(headerHidden=False)
        self.tree_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tree_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tree_view.setModel(self.tree_model)
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tree_view.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tree_view.header().setStretchLastSection(True)

        # 设置属性表视图
        self.attrs_view = QTableView()
        self.attrs_view.setModel(self.attrs_model)
        self.attrs_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.attrs_view.horizontalHeader().setStretchLastSection(True)
        self.attrs_view.verticalHeader().hide()
        # 设置行高自动调整
        self.attrs_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # 设置数据集表视图
        self.dataset_view = QTableView()
        self.dataset_view.setModel(self.dataset_model)
        self.dataset_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.dataset_view.horizontalHeader().setStretchLastSection(True)
        self.dataset_view.verticalHeader().hide()
        # 设置行高自动调整
        self.dataset_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # 创建绘图设置视图
        self.plot_settings_view = QWidget()
        self.plot_settings_layout = QVBoxLayout()

        # 第一组：轴选择和状态显示
        axis_group = QGroupBox("轴设置")
        axis_layout = QVBoxLayout()
        
        # 轴选择按钮和状态显示
        axis_button_layout = QHBoxLayout()
        self.axis_settings_button = QPushButton("轴选择")
        self.axis_settings_button.clicked.connect(self.show_axis_settings_dialog)
        axis_button_layout.addWidget(self.axis_settings_button)
        
        # 显示当前轴选择状态
        self.axis_status_label = QLabel("未选择")
        self.axis_status_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        axis_button_layout.addWidget(self.axis_status_label)
        axis_button_layout.addStretch()
        
        axis_layout.addLayout(axis_button_layout)
        axis_group.setLayout(axis_layout)
        self.plot_settings_layout.addWidget(axis_group)
        
        # 创建轴选择对话框（但不立即显示）
        self.axis_dialog = QDialog(self)
        self.axis_dialog.setWindowTitle("轴选择设置")
        self.axis_dialog.setModal(True)
        self.setup_axis_dialog()

        # 第二组：显示设置
        display_group = QGroupBox("显示设置")
        display_layout = QVBoxLayout()
        
        # 点数量设置
        points_layout = QHBoxLayout()
        points_label = QLabel("显示点数:")
        self.points_spinbox = QSpinBox()
        self.points_spinbox.setMinimum(10)
        self.points_spinbox.setMaximum(10000)
        self.points_spinbox.setValue(1000)
        self.points_spinbox.setToolTip("控制绘图中显示的数据点数量")
        
        points_layout.addWidget(points_label)
        points_layout.addWidget(self.points_spinbox)
        points_layout.addStretch()
        display_layout.addLayout(points_layout)
        
        # 数据统计按钮
        stats_button_layout = QHBoxLayout()
        self.show_max_button = QPushButton("显示最大值")
        self.show_max_button.clicked.connect(self.show_column_max_values)
        self.show_max_button.setToolTip("显示每一列的最大值及其所在行号")
        stats_button_layout.addWidget(self.show_max_button)
        
        self.show_min_button = QPushButton("显示最小值")
        self.show_min_button.clicked.connect(self.show_column_min_values)
        self.show_min_button.setToolTip("显示每一列的最小值及其所在行号")
        stats_button_layout.addWidget(self.show_min_button)
        
        display_layout.addLayout(stats_button_layout)
        display_group.setLayout(display_layout)
        self.plot_settings_layout.addWidget(display_group)

        # 第三组：配置管理
        config_group = QGroupBox("配置管理")
        config_layout = QVBoxLayout()
        
        # 配置按钮布局
        config_button_layout = QHBoxLayout()
        
        self.save_config_button = QPushButton("保存配置")
        self.save_config_button.clicked.connect(self.save_plot_config)
        self.save_config_button.setToolTip("将当前绘图设置保存到文件")
        config_button_layout.addWidget(self.save_config_button)
        
        self.load_config_button = QPushButton("加载配置")
        self.load_config_button.clicked.connect(self.load_plot_config)
        self.load_config_button.setToolTip("从文件加载绘图设置")
        config_button_layout.addWidget(self.load_config_button)
        
        config_layout.addLayout(config_button_layout)
        config_group.setLayout(config_layout)
        self.plot_settings_layout.addWidget(config_group)

        # 第四组：主要功能按钮
        action_group = QGroupBox("操作")
        action_layout = QVBoxLayout()
        
        # 应用按钮
        self.apply_plot_button = QPushButton("应用设置并绘图")
        self.apply_plot_button.clicked.connect(self.apply_plot_settings)
        self.apply_plot_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.apply_plot_button.setToolTip("应用当前设置并创建新的绘图")
        action_layout.addWidget(self.apply_plot_button)
        
        # 其他设置按钮 - 弹出菜单集成高级功能
        self.other_settings_button = QPushButton("其他设置")
        self.other_settings_button.clicked.connect(self.show_other_settings_menu)
        self.other_settings_button.setToolTip("自定义标签、导出图片等高级功能")
        action_layout.addWidget(self.other_settings_button)
        
        action_group.setLayout(action_layout)
        self.plot_settings_layout.addWidget(action_group)

        # 添加弹性空间
        self.plot_settings_layout.addStretch()

        self.plot_settings_view.setLayout(self.plot_settings_layout)

        # 设置主数据表视图
        self.data_view = QTableView()
        self.dv_dss = self.data_view.horizontalHeader().defaultSectionSize()
        self.data_view.setModel(self.data_model)

        # 为数据表视图设置上下文菜单
        self.data_view.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.export_csv_action = QAction("导出为CSV", self)
        self.data_view.addAction(self.export_csv_action)
        self.export_csv_action.triggered.connect(self.export_to_csv)

        # 设置选项卡
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.South)
        self.tabs.setTabsClosable(True)
        self.tabs.addTab(self.data_view, "表格")
        self.tabs.tabBar().setTabButton(0, QTabBar.RightSide, None)
        self.tabs.tabCloseRequested.connect(self.handle_close_tab)

        # 创建主布局
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        # 保存每个选项卡的当前dims状态，以便在
        # 更改选项卡时可以恢复
        self.tab_dims = {id(self.tabs.widget(0)): list(self.dims_model.shape)}
        # 容器用于保存每个选项卡的当前节点（树的选定节点）
        # 以便在更改选项卡时可以恢复。
        self.tab_node = {}

        # 如果加载节点将消耗大于self.memory_ratio_limit的可用内存的较大比例，
        # 将出现警告对话框，以便用户可以选择加载
        # 节点或取消加载。
        self.memory_ratio_limit = 0.3

        # 最后，初始化视图的信号
        self.init_signals()

    def init_signals(self):
        """初始化视图信号。"""
        # 当选择树节点时更新表视图
        self.tree_view.selectionModel().selectionChanged.connect(
            self.handle_selection_changed
        )
        # 选择时动态填充更多树项
        # 以保持最小内存使用。
        self.tree_view.expanded.connect(self.tree_model.handle_expanded)
        self.tree_view.collapsed.connect(self.tree_model.handle_collapsed)
        self.tabs.currentChanged.connect(self.handle_tab_changed)
        self.dims_model.dataChanged.connect(self.handle_dims_data_changed)

    def close_file(self):
        """关闭hdf5文件并清理。"""
        self.hdf.close()

    #
    # 槽函数
    #

    def handle_dims_data_changed(self, topLeft, bottomRight, roles):
        """设置要在表中显示的维度。"""
        id_cw = id(self.tabs.currentWidget())
        if isinstance(self.tabs.currentWidget(), QTableView):
            self.data_model.set_dims(self.dims_model.shape)
        elif isinstance(self.tabs.currentWidget(), PlotView):
            self.plot_model.set_dims(self.dims_model.shape)
            self.plot_views[id_cw].update_plot()
        elif isinstance(self.tabs.currentWidget(), ImageView):
            self.image_model.set_dims(self.dims_model.shape)
            self.image_views[id_cw].update_image()
        self.tab_dims[id_cw] = list(self.dims_model.shape)

    def handle_selection_changed(self, selected, deselected):
        """当树视图上的选择更改时，
        更新模型上的节点路径并
        刷新关联表中的数据
        视图。
        """
        index = selected.indexes()[0]
        path = self.tree_model.itemFromIndex(index).data(Qt.UserRole)
        is_path_dataset = isinstance(self.hdf[path], h5py.Dataset)
        if is_path_dataset:
            memory_ratio = self.calculate_memory_ratio(path)
            continue_loading = self.check_node_size(memory_ratio, path)
            if not continue_loading:
                # 用户选择不加载节点
                if not deselected.isEmpty():
                    index = deselected.indexes()[0]
                else:
                    index = QModelIndex()
                self.tree_view.selectionModel().blockSignals(True)
                self.tree_view.setCurrentIndex(index)
                self.tree_view.selectionModel().blockSignals(False)
                return

        self.attrs_model.update_node(path)
        self.attrs_view.scrollToTop()
        self.dataset_model.update_node(path)
        self.dataset_view.scrollToTop()
        self.dims_model.update_node(
            path, now_on_PlotView=isinstance(self.tabs.currentWidget(), PlotView)
        )
        # 更新绘图设置视图
        self.update_plot_settings_view(path)
        id_cw = id(self.tabs.currentWidget())
        self.tab_dims[id_cw] = list(self.dims_model.shape)
        self.tab_node[id_cw] = index
        if not is_path_dataset:
            return

        if isinstance(self.tabs.currentWidget(), QTableView):
            md_0 = self.data_view.horizontalHeader().sectionResizeMode(0)
            node = self.hdf[path]
            compound_names = node.dtype.names
            if isinstance(compound_names, type(None)):
                if node.ndim in [0, 1]:
                    size_crit = node.size
                    ncols = 1
                elif node.ndim == 2:
                    size_crit = node.size
                    ncols = node.shape[1]
                elif node.ndim > 2 and node.shape[-1] in [3, 4]:
                    size_crit = node.shape[-3] * node.shape[-2] * node.shape[-1]
                    ncols = node.shape[-2]
                else:
                    size_crit = node.shape[-2] * node.shape[-1]
                    ncols = node.shape[-1]
            else:
                ncols = len(compound_names)
                size_crit = node.shape[0] * ncols

            if size_crit < 5000 and ncols == 1:
                self.data_model.update_node(path)
                if md_0 != 3:
                    self.data_view.horizontalHeader().setSectionResizeMode(
                        QHeaderView.ResizeToContents
                    )
                self.data_view.resizeColumnsToContents()
            else:
                if md_0 != 0:
                    self.data_view.horizontalHeader().setSectionResizeMode(
                        QHeaderView.Interactive
                    )
                    for i in range(self.data_view.horizontalHeader().count()):
                        self.data_view.horizontalHeader().resizeSection(i, self.dv_dss)
                self.data_model.update_node(path)
            self.data_view.scrollToTop()

        elif isinstance(self.tabs.currentWidget(), ImageView):
            self.image_model.update_node(path)
            self.image_views[id_cw].update_image()

        elif isinstance(self.tabs.currentWidget(), PlotView):
            self.plot_model.update_node(path)
            self.plot_views[id_cw].update_plot()

    def handle_tab_changed(self):
        """保留每个选项卡的dims并在选项卡更改时
        重置dims_view。
        """
        c_index = self.tree_view.currentIndex()
        o_index = self.tab_node[id(self.tabs.currentWidget())]
        o_slice = list(self.tab_dims[id(self.tabs.currentWidget())])
        if c_index != o_index:
            self.tree_view.setCurrentIndex(o_index)
        self.dims_model.beginResetModel()
        self.dims_model.shape = o_slice
        self.dims_model.endResetModel()
        self.dims_model.dataChanged.emit(QModelIndex(), QModelIndex(), [])

    def add_image(self):
        """添加选项卡以查看hdf5文件中数据集的图像。"""
        c_index = self.tab_node[id(self.tabs.currentWidget())]
        path = self.tree_model.itemFromIndex(c_index).data(Qt.UserRole)
        
        # 检查数据是否适合图像显示
        dataset = self.hdf[path]
        if not isinstance(dataset, h5py.Dataset):
            QMessageBox.warning(self, "警告", "请选择一个数据集！")
            return
            
        # 检查数据维度
        if dataset.ndim < 2:
            QMessageBox.warning(self, "警告", "数据集维度不足，需要至少2维数据才能显示为图像！")
            return
            
        # 初始化图像模型
        if self.image_model is None:
            self.image_model = ImageModel(self.hdf)
            
        # 更新图像模型
        self.image_model.update_node(path)
        
        # 创建图像视图
        image_view = ImageView(self.image_model, self.dims_model)
        image_view.update_image()
        
        # 添加到选项卡
        self.dims_model.update_node(path, now_on_PlotView=True)
        id_image = id(image_view)
        self.image_views[id_image] = image_view
        self.tab_dims[id_image] = list(self.dims_model.shape)
        self.tab_node[id_image] = self.tree_view.currentIndex()
        
        # 获取数据集名称作为选项卡标题
        dataset_name = path.split('/')[-1]
        self.tabs.addTab(image_view, f"图像: {dataset_name}")
        self.tabs.setCurrentWidget(image_view)

    def _convert_1d_to_image(self, source_path: str, processor):
        """
        将1D数据转换为图像并显示
        
        Args:
            source_path: 源数据集路径
            processor: 图像处理器实例
        """
        try:
            # 生成目标数据集名称
            source_name = source_path.split('/')[-1]
            target_name = f"{source_name}_matplotlib_image"
            
            # 执行转换
            success = processor.convert_1d_to_image(self.hdf, source_path, target_name)
            
            if not success:
                QMessageBox.critical(self, "错误", "转换1D数据为图像失败！")
                return
            
            # 初始化图像模型
            if self.image_model is None:
                self.image_model = ImageModel(self.hdf)
            
            # 更新图像模型以显示新创建的图像
            self.image_model.update_node(target_name)
            
            # 创建图像视图
            image_view = ImageView(self.image_model, self.dims_model)
            image_view.update_image()
            
            # 添加到选项卡
            self.dims_model.update_node(target_name, now_on_PlotView=True)
            id_image = id(image_view)
            self.image_views[id_image] = image_view
            self.tab_dims[id_image] = list(self.dims_model.shape)
            self.tab_node[id_image] = self.tree_view.currentIndex()
            
            # 添加选项卡
            self.tabs.addTab(image_view, f"转换图像: {source_name}")
            self.tabs.setCurrentWidget(image_view)
            
            QMessageBox.information(self, "成功", f"成功将1D数据转换为图像！\n新数据集: {target_name}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"转换1D数据为图像时发生错误: {str(e)}")
            
    def add_plot(self):
        """添加选项卡以查看hdf5文件中数据集的绘图。"""
        c_index = self.tab_node[id(self.tabs.currentWidget())]
        path = self.tree_model.itemFromIndex(c_index).data(Qt.UserRole)

        # 使用默认设置创建绘图
        settings = {
            'x_column': 0,  # 默认第一列作为X轴
            'y_columns': [],  # 将在add_plot_with_settings中设置
            'points': 1000  # 默认显示1000个点
        }

        # 获取列名
        dataset = self.hdf[path]
        if dataset.dtype.names:
            column_names = list(dataset.dtype.names)
        else:
            # 对于简单数据类型，创建列名
            if dataset.ndim == 1:
                column_names = ["数据"]
            else:
                column_names = [f"列{i+1}" for i in range(dataset.shape[1])]

        # 根据数据列数设置默认Y轴
        if len(column_names) > 1:
            # 如果有第二列和第三列，默认使用它们作为Y轴
            if len(column_names) >= 3:
                settings['y_columns'] = [1, 2]  # 第二列和第三列
            else:
                # 否则使用除第一列外的所有列
                settings['y_columns'] = list(range(1, len(column_names)))
        else:
            # 只有一列数据，使用它作为Y轴
            settings['y_columns'] = [0]

        self.add_plot_with_settings(path, settings)

    def add_plot_with_settings(self, path, settings):
        """使用指定设置添加绘图选项卡。"""
        self.dims_model.update_node(path, now_on_PlotView=True)
        self.plot_model.update_node(path)
        pv = PlotView(self.plot_model, self.dims_model, settings)
        pv.update_plot()
        id_pv = id(pv)
        self.plot_views[id_pv] = pv
        self.tab_dims[id_pv] = list(self.dims_model.shape)
        tree_index = self.tree_view.currentIndex()
        self.tab_node[id_pv] = tree_index
        index = self.tabs.addTab(self.plot_views[id_pv], "绘图")
        self.tabs.blockSignals(True)
        self.tabs.setCurrentIndex(index)
        self.tabs.blockSignals(False)

    def apply_plot_settings(self):
        """应用绘图设置并创建绘图。"""
        # 获取当前选中的节点
        current_index = self.tree_view.currentIndex()
        if not current_index.isValid():
            QMessageBox.warning(self, "警告", "请先选择要绘制的数据集！")
            return

        path = self.tree_model.itemFromIndex(current_index).data(Qt.UserRole)

        # 获取设置
        x_col_index = self.x_combo.currentIndex()
        # 如果选择的是索引(第一个选项)，则x_col=-1表示使用索引，否则使用实际列号
        x_col = -1 if x_col_index == 0 else x_col_index - 1
        y_cols = []
        for i, checkbox in enumerate(self.y_checkboxes):
            if checkbox.isChecked():
                # Y轴列号直接对应数据列号
                y_cols.append(i)

        # 如果没有选择Y轴，则选择所有列
        if not y_cols:
            dataset = self.hdf[path]
            if dataset.dtype.names:
                col_count = len(dataset.dtype.names)
            else:
                col_count = dataset.shape[1] if dataset.ndim > 1 else 1
            y_cols = list(range(col_count))
            # 如果X轴选择了实际列，则从Y轴中排除该列
            if x_col >= 0 and x_col in y_cols:
                y_cols.remove(x_col)

        settings = {
            'x_column': x_col,
            'y_columns': y_cols,
            'points': self.points_spinbox.value(),
            'custom_title': getattr(self, 'custom_title', ''),
            'custom_x_label': getattr(self, 'custom_x_label', ''),
            'custom_y_label': getattr(self, 'custom_y_label', '')
        }

        # 创建绘图
        self.add_plot_with_settings(path, settings)

    def handle_close_tab(self, index):
        """关闭选项卡。"""
        widget = self.tabs.widget(index)
        self.tabs.removeTab(index)
        self.tab_dims.pop(id(widget))
        self.tab_node.pop(id(widget))
        widget.deleteLater()

    def export_to_csv(self):
        """将当前表格数据导出为CSV文件。"""
        ExportUtils.export_to_csv(self.data_model, self)

    def update_plot_settings_view(self, path):
        """更新绘图设置视图。"""
        dataset = self.hdf[path]
        # 只对数据集进行绘图设置，不对组进行
        if not isinstance(dataset, h5py.Dataset):
            # 清空设置视图
            self.x_combo.clear()
            for checkbox in self.y_checkboxes:
                checkbox.setParent(None)
            self.y_checkboxes.clear()
            return

        # 获取列名
        if hasattr(dataset, 'dtype') and dataset.dtype.names:
            column_names = list(dataset.dtype.names)
        else:
            # 对于简单数据类型，创建列名
            if dataset.ndim == 1:
                column_names = ["数据"]
            else:
                column_names = [f"列{i+1}" for i in range(dataset.shape[1])]

        # 更新X轴下拉框
        self.x_combo.clear()
        # 添加"索引"选项作为第一个选项
        all_column_names = ["索引"] + column_names
        self.x_combo.addItems(all_column_names)

        # 更新Y轴复选框
        # 隐藏现有复选框而不是删除它们
        for checkbox in self.y_checkboxes:
            checkbox.setVisible(False)
        
        # 确保有足够的复选框
        while len(self.y_checkboxes) < len(column_names):
            checkbox = QCheckBox(f"列 {len(self.y_checkboxes)+1}")
            checkbox.setVisible(False)
            checkbox.setStyleSheet("""
                QCheckBox {
                    spacing: 5px;
                    padding: 2px;
                    min-height: 20px;
                }
                QCheckBox:hover {
                    background-color: #f0f0f0;
                    border-radius: 3px;
                }
            """)
            self.y_checkboxes.append(checkbox)
            # 插入到弹性空间之前
            self.y_scroll_layout.insertWidget(self.y_scroll_layout.count() - 1, checkbox)
        
        # 更新复选框文本并显示
        for i, col_name in enumerate(column_names):
            checkbox = self.y_checkboxes[i]
            checkbox.setText(f"{i+1}. {col_name.replace('数据列_', '')}")
            checkbox.setVisible(True)

        # 设置默认选择
        if len(column_names) > 1:
            # 如果有第二列和第三列，默认使用它们作为Y轴
            if len(column_names) >= 3:
                self.y_checkboxes[1].setChecked(True)  # 第二列
                self.y_checkboxes[2].setChecked(True)  # 第三列
            else:
                # 否则使用除第一列外的所有列
                for i in range(1, len(column_names)):
                    self.y_checkboxes[i].setChecked(True)
        else:
            # 只有一列数据，使用它作为Y轴
            self.y_checkboxes[0].setChecked(True)

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
        
        # 保存到设置中
        settings = QSettings()
        settings.setValue("plot/custom_title", self.custom_title)
        settings.setValue("plot/custom_x_label", self.custom_x_label)
        settings.setValue("plot/custom_y_label", self.custom_y_label)
        
        # 如果当前有绘图，更新绘图标签
        if hasattr(self, 'plot_views') and self.plot_views:
            for plot_view in self.plot_views.values():
                try:
                    if hasattr(plot_view, 'update_plot') and plot_view.isVisible():
                        plot_view.update_plot()
                except RuntimeError:
                    # 如果PlotView已被删除，跳过
                    pass
    
    def export_plot_image(self):
        """导出当前绘图为图片。"""
        if not self.plot_views:
            QMessageBox.warning(self, "导出失败", "未找到可导出的绘图")
            return
        
        # 获取当前活动的绘图视图
        current_widget = self.tabs.currentWidget()
        if not isinstance(current_widget, PlotView):
            QMessageBox.warning(self, "导出失败", "请先切换到绘图选项卡")
            return
        
        ExportUtils.export_plot_image(current_widget, self)
    
    def select_all_y_columns(self):
        """全选Y轴列。"""
        for checkbox in self.y_checkboxes:
            if checkbox.isVisible():
                checkbox.setChecked(True)
    
    def clear_all_y_columns(self):
        """清除所有Y轴列选择。"""
        for checkbox in self.y_checkboxes:
            if checkbox.isVisible():
                checkbox.setChecked(False)
    
    def invert_y_selection(self):
        """反选Y轴列。"""
        for checkbox in self.y_checkboxes:
            if checkbox.isVisible():
                checkbox.setChecked(not checkbox.isChecked())
    
    def setup_axis_dialog(self):
        """设置轴选择对话框，优化多列选择的布局管理。"""
        dialog_layout = QVBoxLayout()
        dialog_layout.setSpacing(10)
        dialog_layout.setContentsMargins(15, 15, 15, 15)
        
        # 设置对话框最小和最大尺寸
        self.axis_dialog.setMinimumSize(400, 300)
        self.axis_dialog.setMaximumSize(800, 600)
        self.axis_dialog.resize(500, 450)  # 默认大小
        
        # X轴选择组
        x_group = QGroupBox("X轴选择")
        x_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        x_layout = QHBoxLayout()
        x_layout.setSpacing(10)
        
        x_label = QLabel("数据源:")
        x_label.setMinimumWidth(60)
        self.x_combo = QComboBox()
        self.x_combo.setMinimumWidth(200)
        self.x_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        x_layout.addWidget(x_label)
        x_layout.addWidget(self.x_combo)
        x_layout.addStretch()
        x_group.setLayout(x_layout)
        dialog_layout.addWidget(x_group)
        
        # Y轴选择组
        y_group = QGroupBox("Y轴选择 (可选择多个)")
        y_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        y_group_layout = QVBoxLayout()
        y_group_layout.setSpacing(8)
        
        # Y轴操作按钮行
        y_buttons_layout = QHBoxLayout()
        y_buttons_layout.setSpacing(8)
        
        self.select_all_y_button = QPushButton("全选")
        self.select_all_y_button.setFixedWidth(80)
        self.select_all_y_button.clicked.connect(self.select_all_y_columns)
        
        self.clear_all_y_button = QPushButton("清除")
        self.clear_all_y_button.setFixedWidth(80)
        self.clear_all_y_button.clicked.connect(self.clear_all_y_columns)
        
        # 添加列数统计标签
        self.column_count_label = QLabel("共 0 列")
        self.column_count_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        
        y_buttons_layout.addWidget(self.select_all_y_button)
        y_buttons_layout.addWidget(self.clear_all_y_button)
        y_buttons_layout.addStretch()
        y_buttons_layout.addWidget(self.column_count_label)
        
        y_group_layout.addLayout(y_buttons_layout)
        
        # Y轴复选框区域 - 使用垂直布局并添加滚动条
        self.y_checkboxes = []
        self.y_scroll_area = QScrollArea()
        self.y_scroll_area.setWidgetResizable(True)
        self.y_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.y_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # 强制显示滚动条
        
        # 设置滚动区域的固定高度，确保滚动条可见
        self.y_scroll_area.setFixedHeight(250)
        
        self.y_scroll_widget = QWidget()
        self.y_scroll_layout = QVBoxLayout()  # 改回垂直布局
        self.y_scroll_layout.setSpacing(3)
        self.y_scroll_layout.setContentsMargins(5, 5, 5, 5)
        self.y_scroll_layout.addStretch()  # 在底部添加弹性空间
        
        # 初始创建复选框占位符
        for i in range(20):  # 预创建20个位置
            checkbox = QCheckBox(f"列 {i+1}")
            checkbox.setVisible(False)  # 初始隐藏
            checkbox.setStyleSheet("""
                QCheckBox {
                    spacing: 5px;
                    padding: 2px;
                    min-height: 20px;
                }
                QCheckBox:hover {
                    background-color: #f0f0f0;
                    border-radius: 3px;
                }
            """)
            self.y_checkboxes.append(checkbox)
            # 插入到弹性空间之前
            self.y_scroll_layout.insertWidget(self.y_scroll_layout.count() - 1, checkbox)
        
        self.y_scroll_widget.setLayout(self.y_scroll_layout)
        self.y_scroll_area.setWidget(self.y_scroll_widget)
        y_group_layout.addWidget(self.y_scroll_area)
        
        y_group.setLayout(y_group_layout)
        dialog_layout.addWidget(y_group)
        
        # 添加弹性空间
        dialog_layout.addStretch()
        
        # 确定和取消按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 添加快捷操作按钮
        self.invert_selection_button = QPushButton("反选")
        self.invert_selection_button.setFixedWidth(80)
        self.invert_selection_button.clicked.connect(self.invert_y_selection)
        button_layout.addWidget(self.invert_selection_button)
        
        button_layout.addStretch()
        
        self.ok_button = QPushButton("确定")
        self.ok_button.setFixedWidth(80)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.ok_button.clicked.connect(self.apply_axis_settings)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setFixedWidth(80)
        self.cancel_button.clicked.connect(self.axis_dialog.reject)
        button_layout.addWidget(self.cancel_button)
        
        dialog_layout.addLayout(button_layout)
        
        self.axis_dialog.setLayout(dialog_layout)
    
    def show_axis_settings_dialog(self):
        """显示轴选择对话框，优化多列显示。"""
        # 更新对话框中的列信息
        current_index = self.tree_view.currentIndex()
        if current_index.isValid():
            path = self.tree_model.itemFromIndex(current_index).data(Qt.UserRole)
            dataset = self.hdf[path]
            
            if isinstance(dataset, h5py.Dataset):
                # 获取列名
                if hasattr(dataset, 'dtype') and dataset.dtype.names:
                    column_names = list(dataset.dtype.names)
                else:
                    if dataset.ndim == 1:
                        column_names = ["数据"]
                    else:
                        column_names = [f"列{i+1}" for i in range(dataset.shape[1])]
                
                # 更新X轴下拉框
                self.x_combo.clear()
                self.x_combo.addItem("索引")
                self.x_combo.addItems(column_names)
                
                # 更新列数统计
                self.column_count_label.setText(f"共 {len(column_names)} 列")
                
                # 更新Y轴复选框 - 使用网格布局
                # 隐藏所有现有复选框
                for checkbox in self.y_checkboxes:
                    checkbox.setVisible(False)
                    checkbox.setChecked(False)
                
                # 显示并设置新的复选框
                for i, col_name in enumerate(column_names):
                    if i < len(self.y_checkboxes):
                        checkbox = self.y_checkboxes[i]
                        checkbox.setText(f"{i+1:2d}. {col_name}")
                        checkbox.setVisible(True)
                        
                        # 设置默认选择逻辑
                        if len(column_names) > 1:
                            if i >= 1 and i <= min(2, len(column_names) - 1):  # 默认选择第2、3列
                                checkbox.setChecked(True)
                        else:
                            if i == 0:  # 只有一列时选择第一列
                                checkbox.setChecked(True)
                
                # 动态调整对话框大小
                self._adjust_dialog_size(len(column_names))
        
        self.axis_dialog.exec_()
    
    def _adjust_dialog_size(self, column_count):
        """根据列数动态调整对话框大小。"""
        if column_count <= 6:
            # 少量列，使用较小尺寸
            width = 450
            height = 350
        elif column_count <= 12:
            # 中等列数
            width = 500
            height = 450
        elif column_count <= 20:
            # 较多列数
            width = 550
            height = 550
        else:
            # 大量列数，使用最大尺寸
            width = 600
            height = 600
        
        # 确保不超过最大尺寸限制
        width = min(width, 800)
        height = min(height, 600)
        
        self.axis_dialog.resize(width, height)
    
    def apply_axis_settings(self):
        """应用轴设置并更新状态标签。"""
        # 获取选中的Y轴列
        selected_y_cols = []
        for i, checkbox in enumerate(self.y_checkboxes):
            if checkbox.isVisible() and checkbox.isChecked():
                selected_y_cols.append(i)
        
        # 获取X轴选择
        x_selection = self.x_combo.currentIndex() - 1  # 减去索引选项
        
        # 更新状态标签，优化显示格式
        if selected_y_cols:
            x_text = "索引" if x_selection == -1 else f"列{x_selection + 1}"
            
            if len(selected_y_cols) <= 3:
                # 少量列时显示完整列表
                y_text = ", ".join([f"列{i+1}" for i in selected_y_cols])
            else:
                # 多列时显示简化格式
                y_text = f"列{selected_y_cols[0]+1}-{selected_y_cols[-1]+1} ({len(selected_y_cols)}列)"
            
            status_text = f"X: {x_text}, Y: {y_text}"
        else:
            status_text = "未选择"
        
        self.axis_status_label.setText(status_text)
        self.axis_dialog.accept()
        
        # 应用绘图设置
        self.apply_plot_settings()
    
    def show_other_settings_menu(self):
        """显示高级设置菜单。"""
        menu = QMenu(self)
        
        # 自定义标签动作
        custom_label_action = menu.addAction("自定义标签")
        custom_label_action.triggered.connect(self.show_custom_label_dialog)
        
        # 导出图片动作
        export_image_action = menu.addAction("导出图片")
        export_image_action.triggered.connect(self.export_plot_image)
        
        # 显示菜单
        menu.exec_(self.other_settings_button.mapToGlobal(self.other_settings_button.rect().bottomLeft()))

    def save_plot_config(self):
        """保存绘图配置到文件。"""
        # 获取当前绘图设置
        config = {
            'x_column': self.x_combo.currentIndex() - 1 if self.x_combo.currentIndex() > 0 else -1,
            'y_columns': [i for i, checkbox in enumerate(self.y_checkboxes) if checkbox.isChecked()],
            'custom_title': getattr(self, 'custom_title', ''),
            'custom_x_label': getattr(self, 'custom_x_label', ''),
            'custom_y_label': getattr(self, 'custom_y_label', '')
        }
        
        # 打开文件对话框选择保存位置
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "保存绘图配置", 
            "plot_config.json", 
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "保存成功", f"绘图配置已保存到: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "保存失败", f"保存配置时出错: {str(e)}")
    
    def load_plot_config(self):
        """从文件加载绘图配置。"""
        # 打开文件对话框选择配置文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "加载绘图配置", 
            "", 
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 应用配置
                if 'x_column' in config:
                    x_col = config['x_column']
                    # 将-1（索引）映射到combo的0，其他列映射到对应的索引
                    combo_index = 0 if x_col == -1 else x_col + 1
                    if combo_index < self.x_combo.count():
                        self.x_combo.setCurrentIndex(combo_index)
                
                if 'y_columns' in config:
                    # 清除所有选择
                    for checkbox in self.y_checkboxes:
                        checkbox.setChecked(False)
                    # 设置选择的列
                    for col_index in config['y_columns']:
                        if 0 <= col_index < len(self.y_checkboxes):
                            self.y_checkboxes[col_index].setChecked(True)
                
                # 加载自定义标签
                if 'custom_title' in config:
                    self.custom_title = config['custom_title']
                if 'custom_x_label' in config:
                    self.custom_x_label = config['custom_x_label']
                if 'custom_y_label' in config:
                    self.custom_y_label = config['custom_y_label']
                
                # 保存到设置中
                settings = QSettings()
                settings.setValue("plot/custom_title", getattr(self, 'custom_title', ''))
                settings.setValue("plot/custom_x_label", getattr(self, 'custom_x_label', ''))
                settings.setValue("plot/custom_y_label", getattr(self, 'custom_y_label', ''))
                
                QMessageBox.information(self, "加载成功", f"绘图配置已从文件加载")
                
                # 自动应用设置
                self.apply_plot_settings()
                
            except Exception as e:
                QMessageBox.warning(self, "加载失败", f"加载配置时出错: {str(e)}")

    def show_column_max_values(self):
        """显示每一列的最大值及其所在行号。"""
        current_index = self.tree_view.currentIndex()
        if not current_index.isValid():
            QMessageBox.warning(self, "警告", "请先选择要查看的数据集！")
            return
        
        path = self.tree_model.itemFromIndex(current_index).data(Qt.UserRole)
        dataset = self.hdf[path]
        
        if not isinstance(dataset, h5py.Dataset):
            QMessageBox.warning(self, "警告", "请选择数据集而非组！")
            return
        
        try:
            # 获取数据
            data = dataset[:]
            
            # 获取列名
            if hasattr(dataset, 'dtype') and dataset.dtype.names:
                column_names = list(dataset.dtype.names)
            else:
                if dataset.ndim == 1:
                    column_names = ["数据"]
                else:
                    column_names = [f"列{i+1}" for i in range(dataset.shape[1])]
            
            # 计算每一列的最大值和所在行号
            max_values = []
            if dataset.dtype.names:
                # 复合数据类型
                for col_name in column_names:
                    if data.ndim == 0:
                        max_val = data[col_name]
                        max_row = 0
                    else:
                        max_val = data[col_name].max()
                        max_row = data[col_name].argmax()
                    max_values.append((col_name, max_val, max_row))
            else:
                # 简单数据类型
                if dataset.ndim == 1:
                    max_val = data.max()
                    max_row = data.argmax()
                    max_values.append((column_names[0], max_val, max_row))
                else:
                    for i, col_name in enumerate(column_names):
                        max_val = data[:, i].max()
                        max_row = data[:, i].argmax()
                        max_values.append((col_name, max_val, max_row))
            
            # 显示结果
            result_text = "每一列的最大值及其所在行号：\n"
            for col_name, max_val, max_row in max_values:
                result_text += f"{col_name}: {max_val:.6e} (行号: {max_row})\n"
            
            QMessageBox.information(self, "最大值", result_text)
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"计算最大值时出错: {str(e)}")
    
    def show_column_min_values(self):
        """显示每一列的最小值及其所在行号。"""
        current_index = self.tree_view.currentIndex()
        if not current_index.isValid():
            QMessageBox.warning(self, "警告", "请先选择要查看的数据集！")
            return
        
        path = self.tree_model.itemFromIndex(current_index).data(Qt.UserRole)
        dataset = self.hdf[path]
        
        if not isinstance(dataset, h5py.Dataset):
            QMessageBox.warning(self, "警告", "请选择数据集而非组！")
            return
        
        try:
            # 获取数据
            data = dataset[:]
            
            # 获取列名
            if hasattr(dataset, 'dtype') and dataset.dtype.names:
                column_names = list(dataset.dtype.names)
            else:
                if dataset.ndim == 1:
                    column_names = ["数据"]
                else:
                    column_names = [f"列{i+1}" for i in range(dataset.shape[1])]
            
            # 计算每一列的最小值和所在行号
            min_values = []
            if dataset.dtype.names:
                # 复合数据类型
                for col_name in column_names:
                    if data.ndim == 0:
                        min_val = data[col_name]
                        min_row = 0
                    else:
                        min_val = data[col_name].min()
                        min_row = data[col_name].argmin()
                    min_values.append((col_name, min_val, min_row))
            else:
                # 简单数据类型
                if dataset.ndim == 1:
                    min_val = data.min()
                    min_row = data.argmin()
                    min_values.append((column_names[0], min_val, min_row))
                else:
                    for i, col_name in enumerate(column_names):
                        min_val = data[:, i].min()
                        min_row = data[:, i].argmin()
                        min_values.append((col_name, min_val, min_row))
            
            # 显示结果
            result_text = "每一列的最小值及其所在行号：\n"
            for col_name, min_val, min_row in min_values:
                result_text += f"{col_name}: {min_val:.6e} (行号: {min_row})\n"
            
            QMessageBox.information(self, "最小值", result_text)
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"计算最小值时出错: {str(e)}")

    def calculate_memory_ratio(self, path):
        """计算内存比例。
        为所选数据集找到一个关键维度，dim_crit，以字节为单位
        然后计算并返回memory_ratio：关键维度的比例
        以字节为单位到系统上的可用内存。
        参数
        ----------
        path : STR
            self.hdf中数据集的路径。
        返回
        -------
        浮点数
            所选数据集的关键维度（以字节为单位）的比例
            到系统上的可用内存。
        """
        node = self.hdf[path]
        if node.ndim in [0, 1, 2]:
            dim_crit = node.nbytes
        elif node.ndim > 2 and node.shape[-1] in [3, 4]:
            size = node.shape[-3] * node.shape[-2] * node.shape[-1]
            dim_crit = node[tuple([0] * node.ndim)].nbytes * size
        else:
            size = node.shape[-2] * node.shape[-1]
            dim_crit = node[tuple([0] * node.ndim)].nbytes * size
        memory_ratio = dim_crit / psutil.virtual_memory().free
        return memory_ratio

    def check_node_size(self, memory_ratio, path):
        """检查memory_ratio > self.memory_ratio_limit。
        如果memory_ratio > self.memory_ratio_limit，则
        出现QMessageBox.warning，通知用户
        加载节点将消耗可用内存的百分比。用户可以
        选择继续加载节点，或取消并返回到
        树中的先前选择。
        参数
        ----------
        memory_ratio : 浮点数
            所选数据集的关键维度（以字节为单位）的比例
            到系统上的可用内存。
        path : STR
            self.hdf中数据集的路径。
        返回
        -------
        布尔值
            如果memory_ratio <= self.memory_ratio_limit，则返回True
            如果memory_ratio > self.memory_ratio_limit，如果用户按下对话框上的"是"，选择继续
            加载节点，则返回True。如果用户按下"否"
            在对话框上，选择取消加载节点并返回到
            树中的先前选择，则返回False。
        """
        if memory_ratio > self.memory_ratio_limit:
            msg = f"加载 {path} 将消耗 {int(100*memory_ratio):d}%"
            msg1 = " 的可用内存。"
            msg2 = "\n继续加载吗？"
            button = QMessageBox.warning(
                self,
                "内存警告",
                "".join([msg, msg1, msg2]),
                buttons=QMessageBox.Yes | QMessageBox.No,
                defaultButton=QMessageBox.No,
            )
            return button == QMessageBox.Yes
        return True