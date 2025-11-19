"""
包含绘图视图类。
"""

import h5py
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QAbstractItemView, QScrollBar, QVBoxLayout
import pyqtgraph as pg


class PlotView(QAbstractItemView):
    """
    显示关联PlotModel的绘图视图。
    可以显示y(x)图，其中x可以是索引或数据集中的任意列。
    """
    def __init__(self, model, dims_model, settings=None):
        super().__init__()
        self.setModel(model)
        self.dims_model = dims_model
        # 绘图设置
        self.settings = settings if settings else {
            'x_column': 0,  # 默认第一列作为X轴
            'y_columns': [1],  # 默认第二列作为Y轴
            'points': 1000  # 默认显示1000个点
        }
        pg.setConfigOptions(antialias=True)
        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")
        pg.setConfigOption("leftButtonPan", False)

        # 主图形布局小部件
        graphics_layout_widget = pg.GraphicsLayoutWidget()
        self.plot_item = graphics_layout_widget.addPlot()

        # 创建用于移动图像帧的滚动条
        self.scrollbar = QScrollBar(Qt.Horizontal)
        layout = QVBoxLayout()
        layout.addWidget(graphics_layout_widget)
        layout.addWidget(self.scrollbar)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.init_signals()

        # self.pen = (0,0,200)
        self.pen = None
        self.symbolBrush = (0, 0, 255)
        self.symbolPen = "k"

    def init_signals(self):
        """初始化鼠标和滚动条信号。"""
        self.plot_item.scene().sigMouseMoved.connect(self.handle_mouse_moved)
        self.scrollbar.valueChanged.connect(self.handle_scroll)

    def update_plot(self):
        """更新显示的绘图。"""
        if isinstance(self.model().plot_view, type(None)):
            self.plot_item.setVisible(False)
            self.scrollbar.blockSignals(True)
            self.scrollbar.setVisible(False)
            self.scrollbar.blockSignals(False)
            return

        self.plot_item.setTitle(None)
        self.plot_item.enableAutoRange()
        self.set_up_plot()
        self.plot_item.showAxis("top")
        self.plot_item.showAxis("right")
        for i in ["bottom", "top", "left", "right"]:
            ax = self.plot_item.getAxis(i)
            ax.setPen(pg.mkPen(color="k", width=2))
            ax.setStyle(**{"tickAlpha": 255, "tickLength": -8})
        for i in ["bottom", "left"]:
            lab_font = QFont("Arial")
            lab_font.setPointSize(11)
            ax = self.plot_item.getAxis(i)
            ax.setTextPen("k")
            ax.setStyle(**{"tickFont": lab_font})
        for i in ["top", "right"]:
            self.plot_item.getAxis(i).setStyle(**{"showValues": False})

        if not self.plot_item.isVisible():
            self.plot_item.setVisible(True)
        if not self.scrollbar.isVisible():
            self.scrollbar.setVisible(True)

        if not isinstance(self.model().dims[0], slice):
            try:
                if not self.scrollbar.isVisible():
                    self.scrollbar.setVisible(True)
                self.scrollbar.setRange(0, self.model().node.shape[0] - 1)
                if self.scrollbar.sliderPosition() != self.model().dims[0]:
                    self.scrollbar.blockSignals(True)
                    self.scrollbar.setSliderPosition(self.model().dims[0])
                    self.scrollbar.blockSignals(False)
            except TypeError:
                if self.scrollbar.isVisible():
                    self.scrollbar.blockSignals(True)
                    self.scrollbar.setVisible(False)
                    self.scrollbar.blockSignals(False)
        else:
            self.scrollbar.blockSignals(True)
            self.scrollbar.setVisible(False)
            self.scrollbar.blockSignals(False)

    def set_up_plot(self):
        """设置显示的绘图，包括轴标签。"""
        c_n = self.model().compound_names

        # 清除之前的绘图和图例
        self.plot_item.clear()
        self.plot_item.addLegend()

        # 定义不同颜色的画笔，用于区分不同的曲线
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

        # 获取设置
        x_col = self.settings['x_column']
        y_cols = self.settings['y_columns']
        max_points = self.settings['points']

        if c_n:
            # 复合数据类型的情况
            if len(c_n) == 1:
                # 只有一列数据，绘制与索引的关系
                x_data = list(range(len(self.model().plot_view[c_n[0]])))
                y_data = self.model().plot_view[c_n[0]]

                # 限制点数 - 只减少显示的点数，但保持线的连续性
                if len(x_data) > max_points:
                    step = len(x_data) // max_points
                    # 绘制完整的线
                    self.plot_item.plot(
                        x_data,
                        y_data,
                        pen=colors[0],
                        name=c_n[0],
                    )
                    # 只显示部分点，不添加图例
                    x_plot = x_data[::step]
                    y_plot = y_data[::step]
                    # 绘制点
                    self.plot_item.plot(
                        x_plot,
                        y_plot,
                        pen=None,
                        symbol='o',
                        symbolSize=5,
                        symbolBrush=colors[0],
                        symbolPen='k',
                    )
                else:
                    # 数据量不大，直接绘制点线图
                    self.plot_item.plot(
                        x_data,
                        y_data,
                        pen=colors[0],
                        symbol='o',
                        symbolSize=5,
                        symbolBrush=colors[0],
                        symbolPen='k',
                        name=c_n[0],
                    )
            else:
                # 多列数据，使用设置中的列
                if x_col == -1:  # 索引选项（在HDF5Widget中设置x_col=-1表示索引）
                    # 使用索引作为X轴数据
                    data_length = len(self.model().plot_view[c_n[0]])
                    x_data = list(range(data_length))
                else:
                    # 注意：x_col是实际的列索引，不需要减1
                    x_data = self.model().plot_view[c_n[x_col]]

                # 为每一列y数据绘制曲线
                for i, y_col in enumerate(y_cols):
                    if y_col < len(c_n):
                        y_data = self.model().plot_view[c_n[y_col]]
                        color_idx = i % len(colors)

                        # 限制点数 - 只减少显示的点数，但保持线的连续性
                        if len(x_data) > max_points:
                            step = len(x_data) // max_points
                            # 绘制完整的线
                            self.plot_item.plot(
                                x_data,
                                y_data,
                                pen=colors[color_idx],
                                name=c_n[y_col],
                            )
                            # 只显示部分点，不添加图例
                            x_plot = x_data[::step]
                            y_plot = y_data[::step]
                            # 绘制点
                            self.plot_item.plot(
                                x_plot,
                                y_plot,
                                pen=None,
                                symbol='o',
                                symbolSize=5,
                                symbolBrush=colors[color_idx],
                                symbolPen='k',
                            )
                        else:
                            # 数据量不大，直接绘制点线图
                            self.plot_item.plot(
                                x_data,
                                y_data,
                                pen=colors[color_idx],
                                symbol='o',
                                symbolSize=5,
                                symbolBrush=colors[color_idx],
                                symbolPen='k',
                                name=c_n[y_col],
                            )
        else:
            # 简单数据类型的情况
            data = self.model().plot_view
            if data.ndim == 1:
                # 一维数据，绘制与索引的关系
                x_data = list(range(len(data)))
                y_data = data

                # 限制点数 - 只减少显示的点数，但保持线的连续性
                if len(x_data) > max_points:
                    step = len(x_data) // max_points
                    # 绘制完整的线
                    self.plot_item.plot(
                        x_data,
                        y_data,
                        pen=colors[0],
                        name="数据",
                    )
                    # 只显示部分点，不添加图例
                    x_plot = x_data[::step]
                    y_plot = y_data[::step]
                    # 绘制点
                    self.plot_item.plot(
                        x_plot,
                        y_plot,
                        pen=None,
                        symbol='o',
                        symbolSize=5,
                        symbolBrush=colors[0],
                        symbolPen='k',
                    )
                else:
                    # 数据量不大，直接绘制点线图
                    self.plot_item.plot(
                        x_data,
                        y_data,
                        pen=colors[0],
                        symbol='o',
                        symbolSize=5,
                        symbolBrush=colors[0],
                        symbolPen='k',
                        name="数据",
                    )
            elif data.ndim == 2 and data.shape[1] >= 2:
                # 二维数据，使用设置中的列
                if x_col == -1:  # 索引选项（在HDF5Widget中设置x_col=-1表示索引）
                    # 使用索引作为X轴数据
                    x_data = list(range(data.shape[0]))
                else:
                    x_data = data[:, x_col]

                # 为每一列y数据绘制曲线
                for i, y_col in enumerate(y_cols):
                    if y_col < data.shape[1]:
                        y_data = data[:, y_col]
                        color_idx = i % len(colors)

                        # 限制点数 - 只减少显示的点数，但保持线的连续性
                        if len(x_data) > max_points:
                            step = len(x_data) // max_points
                            # 绘制完整的线
                            self.plot_item.plot(
                                x_data,
                                y_data,
                                pen=colors[color_idx],
                                name=f"列{y_col+1}",
                            )
                            # 只显示部分点，不添加图例
                            x_plot = x_data[::step]
                            y_plot = y_data[::step]
                            # 绘制点
                            self.plot_item.plot(
                                x_plot,
                                y_plot,
                                pen=None,
                                symbol='o',
                                symbolSize=5,
                                symbolBrush=colors[color_idx],
                                symbolPen='k',
                            )
                        else:
                            # 数据量不大，直接绘制点线图
                            self.plot_item.plot(
                                x_data,
                                y_data,
                                pen=colors[color_idx],
                                symbol='o',
                                symbolSize=5,
                                symbolBrush=colors[color_idx],
                                symbolPen='k',
                                name=f"列{y_col+1}",
                            )
            else:
                # 其他情况，直接绘制数据
                self.plot_item.plot(
                    data,
                    pen=colors[0],
                    symbol='o',
                    symbolSize=5,
                    symbolBrush=colors[0],
                    symbolPen='k',
                    name="数据",
                )

        # 设置X轴和Y轴标签
        # 优先使用自定义标签
        custom_x_label = self.settings.get('custom_x_label', '')
        if custom_x_label:
            x_label = custom_x_label
        else:
            if c_n:
                # 复合数据类型，使用列名作为标签
                if x_col == -1:  # 索引选项（在HDF5Widget中设置x_col=-1表示索引）
                    x_label = "索引"
                elif x_col < len(c_n):  # 直接使用列索引
                    x_label = c_n[x_col]
                else:
                    x_label = "索引"
            else:
                # 简单数据类型，使用列索引作为标签
                if x_col == -1:  # 索引选项
                    x_label = "索引"
                else:
                    # 获取数据形状来确定列数
                    data = self.model().plot_view
                    if hasattr(data, 'shape') and len(data.shape) > 1:
                        column_count = data.shape[1]
                    else:
                        column_count = 1
                    x_label = f"列{x_col+1}" if column_count > 1 else "索引"

        # 设置标题 - 优先使用自定义标题
        custom_title = self.settings.get('custom_title', '')
        if custom_title:
            self.plot_item.setTitle(custom_title)
        else:
            self.plot_item.setTitle(self.model().node.name.split("/")[-1])
        self.plot_item.titleLabel.item.setFont(QFont("Arial", 14, QFont.Bold))

        self.plot_item.setLabel(
            "bottom", x_label, **{"font-size": "14pt", "font": "Arial"}
        )

        # 设置Y轴标签
        # 优先使用自定义标签
        custom_y_label = self.settings.get('custom_y_label', '')
        if custom_y_label:
            y_label = custom_y_label
        else:
            y_label = "值"
        self.plot_item.setLabel(
            "left", y_label, **{"font-size": "14pt", "font": "Arial"}
        )

    def handle_scroll(self, value):
        """在滚动时更改图像帧。"""
        self.dims_model.beginResetModel()
        self.dims_model.shape[0] = str(value)
        self.dims_model.endResetModel()
        self.dims_model.dataChanged.emit(QModelIndex(), QModelIndex(), [])

    def handle_mouse_moved(self, pos):
        """当鼠标在图像场景中移动时，
        更新光标位置。
        """
        if self.plot_item.isVisible():
            vb = self.plot_item.getViewBox()
            x_lim, y_lim = vb.viewRange()
            x_min, x_max = x_lim
            y_min, y_max = y_lim
            scene_pos = vb.mapSceneToView(pos)
            x = scene_pos.x()
            y = scene_pos.y()
            if x_min <= x < x_max and y_min <= y < y_max:
                msg1 = f"X={x:.3e} Y={y:.3e}"
                self.window().status.showMessage(msg1)
                vb.setCursor(Qt.CrossCursor)
            else:
                self.window().status.showMessage("")
                vb.setCursor(Qt.ArrowCursor)

    def horizontalOffset(self):
        """返回零。"""
        return 0

    def verticalOffset(self):
        """返回零。"""
        return 0

    def moveCursor(self, cursorAction, modifiers):
        """返回QModelIndex。"""
        return QModelIndex()