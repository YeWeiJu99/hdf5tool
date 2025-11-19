"""
包含图像视图类。
"""

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QAbstractItemView, QScrollBar, QVBoxLayout
import pyqtgraph as pg


class ImageView(QAbstractItemView):
    """
    显示关联ImageModel的灰度或rgb(a)图像视图。
    如果hdf5文件的节点具有ndim > 2，则显示的图像可以
    通过更改切片（DimsTableModel）进行更改。提供了滚动条
    也可以用于滚动第一个轴中的图像。
    """
    def __init__(self, model, dims_model):
        super().__init__()
        self.setModel(model)
        self.dims_model = dims_model
        pg.setConfigOptions(antialias=True)
        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")
        pg.setConfigOption("leftButtonPan", False)

        # 主图形布局小部件
        graphics_layout_widget = pg.GraphicsLayoutWidget()

        # 图形布局小部件视图框
        self.viewbox = graphics_layout_widget.addViewBox()
        self.viewbox.setAspectLocked(True)
        self.viewbox.invertY(True)

        # 将图像项添加到视图框
        self.image_item = pg.ImageItem(border="w")
        self.viewbox.addItem(self.image_item)
        self.image_item.setOpts(axisOrder="row-major")

        # 创建用于移动图像帧的滚动条
        self.scrollbar = QScrollBar(Qt.Horizontal)
        layout = QVBoxLayout()
        layout.addWidget(graphics_layout_widget)
        layout.addWidget(self.scrollbar)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.init_signals()

    def init_signals(self):
        """初始化鼠标和滚动条信号。"""
        self.image_item.scene().sigMouseMoved.connect(self.handle_mouse_moved)
        self.scrollbar.valueChanged.connect(self.handle_scroll)

    def update_image(self):
        """更新显示的图像。"""
        if isinstance(self.model().image_view, type(None)):
            if self.viewbox.isVisible():
                self.viewbox.setVisible(False)
            if self.scrollbar.isVisible():
                self.scrollbar.blockSignals(True)
                self.scrollbar.setVisible(False)
                self.scrollbar.blockSignals(False)
            return

        self.image_item.setImage(self.model().image_view)
        if not self.viewbox.isVisible():
            self.viewbox.setVisible(True)
        if not self.scrollbar.isVisible():
            self.scrollbar.setVisible(True)

        if self.model().ndim > 2:
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
        if self.viewbox.isVisible():
            try:
                max_y, max_x = self.image_item.image.shape
            except ValueError:
                max_y, max_x = self.image_item.image.shape[:2]
            scene_pos = self.viewbox.mapSceneToView(pos)
            x = int(scene_pos.x())
            y = int(scene_pos.y())
            if 0 <= x < max_x and 0 <= y < max_y:
                iv = self.model().image_view[y, x]
                msg1 = f"X={x} Y={y}, 值="
                try:
                    msg2 = f"{iv:.3e}"
                except TypeError:
                    try:
                        msg2 = f"[{iv[0]:.3e}, {iv[1]:.3e}, {iv[2]:.3e}, {iv[3]:.3e}]"
                    except IndexError:
                        msg2 = f"[{iv[0]:.3e}, {iv[1]:.3e}, {iv[2]:.3e}]"
                self.window().status.showMessage(msg1 + msg2)
                self.viewbox.setCursor(Qt.CrossCursor)
            else:
                self.window().status.showMessage("")
                self.viewbox.setCursor(Qt.ArrowCursor)

    def horizontalOffset(self):
        """返回零。"""
        return 0

    def verticalOffset(self):
        """返回零。"""
        return 0

    def moveCursor(self, cursorAction, modifiers):
        """返回QModelIndex。"""
        return QModelIndex()