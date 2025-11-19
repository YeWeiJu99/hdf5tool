"""
包含HDF5图像和绘图视图模型。
"""

import h5py
from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt


class ImageModel(QAbstractItemModel):
    """
    包含HDF5文件中数据集数据的模型，
    以适合绘制为图像的形式。
    """

    def __init__(self, hdf):
        super().__init__()

        self.hdf = hdf
        self.node = None
        self.row_count = 0
        self.column_count = 0
        self.ndim = 0
        self.dims = ()
        self.image_view = None
        self.compound_names = None

    def update_node(self, path):
        """更新当前节点路径。"""
        self.compound_names = None

        self.beginResetModel()

        self.row_count = 0
        self.column_count = 0

        self.dims = ()

        self.node = self.hdf[path]

        self.image_view = None

        if not isinstance(self.node, h5py.Dataset) or self.node.dtype == "object":
            self.endResetModel()
            return

        self.ndim = self.node.ndim

        shape = self.node.shape

        self.compound_names = self.node.dtype.names

        if self.ndim == 0:
            self.row_count = 1
            self.column_count = 1

        elif self.ndim == 1:
            self.row_count = shape[0]

            if self.compound_names:
                self.column_count = len(self.compound_names)
            else:
                self.column_count = 1

        elif self.ndim == 2:
            self.row_count = shape[-2]
            self.column_count = shape[-1]
            self.dims = tuple([slice(None), slice(None)])
            self.image_view = self.node[self.dims]

        elif self.ndim > 2 and shape[-1] in [3, 4]:
            self.row_count = shape[-3]
            self.column_count = shape[-2]
            self.dims = tuple(
                ([0] * (self.ndim - 3)) + [slice(None), slice(None), slice(None)]
            )
            self.image_view = self.node[self.dims]

        else:
            self.row_count = shape[-2]
            self.column_count = shape[-1]
            self.dims = tuple(([0] * (self.ndim - 2)) + [slice(None), slice(None)])
            self.image_view = self.node[self.dims]

        self.endResetModel()

    def parent(self, childIndex=QModelIndex()):
        """创建并返回索引。"""
        return QModelIndex()

    def index(self, row, column, parentIndex=QModelIndex()):
        """创建并返回索引。"""
        return self.createIndex(row, column, parentIndex)

    def rowCount(self, parent=QModelIndex()):
        """返回行数。"""
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        """返回列数。"""
        return self.column_count

    def headerData(self, section, orientation, role):
        """返回有关表头的数据。"""
        if role == Qt.DisplayRole:
            if self.compound_names and orientation == Qt.Horizontal:
                return self.compound_names[section]
            else:
                return str(section)

        super().headerData(section, orientation, role)

    def data(self, index, role=Qt.DisplayRole):
        """返回None。

        子类化QAbstractItemModel时必须实现此函数。
        由于ImageView类不需要此函数，因此返回无效的QVariant。
        将来不应使用构造函数QVariant()，因此可以返回None，
        如文档中推荐的：
        https://doc.qt.io/qtforpython-6/considerations.html#qvariant。
        """
        if index.isValid() and role in (Qt.DisplayRole, Qt.ToolTipRole):
            return None

    def set_dims(self, dims):
        """设置模型的维度。

        如果编辑了HDF5Widget.dims_view中的维度，
        则调用此函数。模型的维度被更新以匹配输入维度。
        """
        self.beginResetModel()

        self.row_count = None
        self.column_count = None
        self.dims = []
        self.image_view = None

        from src.models.utils import get_dims_from_str
        self.dims = get_dims_from_str(dims)

        if len(self.dims) >= 2 and self.node.dtype != "object":
            self.image_view = self.node[self.dims]
            shape = self.image_view.shape
            if self.image_view.ndim == 2:
                self.row_count = shape[-2]
                self.column_count = shape[-1]

            elif self.image_view.ndim == 3 and shape[-1] in [3, 4]:
                self.row_count = shape[-3]
                self.column_count = shape[-2]

            else:
                self.image_view = None
                self.row_count = 1
                self.column_count = 1

        else:
            self.row_count = 1
            self.column_count = 1

        self.endResetModel()


class PlotModel(QAbstractItemModel):
    """
    包含HDF5文件数据集数据的模型，
    以适合绘制为y(x)的形式，其中x通常是索引。
    """

    def __init__(self, hdf):
        super().__init__()

        self.hdf = hdf
        self.node = None
        self.row_count = 0
        self.column_count = 0
        self.ndim = 0
        self.dims = ()
        self.plot_view = None
        self.compound_names = None

    def update_node(self, path):
        """更新当前节点路径。"""
        self.beginResetModel()

        self.node = self.hdf[path]
        self.row_count = 0
        self.column_count = 0
        self.ndim = 0
        self.dims = ()
        self.plot_view = None
        self.compound_names = None

        if not isinstance(self.node, h5py.Dataset) or self.node.dtype == "object":
            self.endResetModel()
            return

        self.ndim = self.node.ndim

        shape = self.node.shape

        self.compound_names = self.node.dtype.names

        if self.ndim == 0:
            self.row_count = 1
            self.column_count = 1
            self.endResetModel()
            return

        if self.ndim == 1:
            self.row_count = shape[0]
            self.dims = tuple([slice(None)])

            if self.compound_names:
                self.column_count = len(self.compound_names)
                self.plot_view = self.node[self.dims[0]]
                self.endResetModel()
                return

        elif self.ndim == 2:
            self.row_count = shape[-2]
            self.column_count = shape[-1]
            self.dims = tuple([slice(None), slice(None)])

        elif self.ndim > 2 and shape[-1] in [3, 4]:
            self.row_count = shape[-3]
            self.column_count = shape[-2]
            self.dims = tuple(([0] * (self.ndim - 3)) + [slice(None), slice(None), 0])

        else:
            self.row_count = shape[-2]
            self.column_count = shape[-1]
            self.dims = tuple(([0] * (self.ndim - 2)) + [slice(None), slice(None)])

        self.plot_view = self.node[self.dims]
        self.endResetModel()

    def parent(self, childIndex=QModelIndex()):
        """创建并返回索引。"""
        return QModelIndex()

    def index(self, row, column, parentIndex=QModelIndex()):
        """创建并返回索引。"""
        return self.createIndex(row, column, parentIndex)

    def rowCount(self, parent=QModelIndex()):
        """返回行数。"""
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        """返回列数。"""
        return self.column_count

    def headerData(self, section, orientation, role):
        """返回有关表头的数据。"""
        if role == Qt.DisplayRole:
            if self.compound_names and orientation == Qt.Horizontal:
                return self.compound_names[section]
            else:
                return str(section)

        super().headerData(section, orientation, role)

    def data(self, index, role=Qt.DisplayRole):
        """返回None。

        子类化QAbstractItemModel时必须实现此函数。
        由于PlotView类不需要此函数，因此返回无效的QVariant。
        将来不应使用构造函数QVariant()，因此可以返回None，
        如文档中推荐的：
        https://doc.qt.io/qtforpython-6/considerations.html#qvariant。
        """
        if index.isValid() and role in (Qt.DisplayRole, Qt.ToolTipRole):
            return None

    def set_dims(self, dims):
        """设置模型的维度。

        如果编辑了HDF5Widget.dims_view中的维度，
        则调用此函数。模型的维度被更新以匹配输入维度。
        """
        self.beginResetModel()

        self.row_count = None
        self.column_count = None
        self.dims = ()
        self.plot_view = None

        from src.models.utils import get_dims_from_str
        self.dims = get_dims_from_str(dims)

        if len(self.dims) >= 1 and self.node.dtype != "object":
            if not any(isinstance(i, slice) for i in self.dims):
                self.row_count = 1
                self.column_count = 1
                self.endResetModel()
                return

            if not self.compound_names:
                self.plot_view = self.node[self.dims]
                shape = self.plot_view.shape
                self.row_count = shape[0]

                if self.plot_view.ndim == 1:
                    self.column_count = 1

                elif self.plot_view.ndim == 2:
                    self.column_count = shape[1]

                else:
                    self.plot_view = None
                    self.column_count = 1

            else:
                # 对于复合数据类型，直接使用整个数据视图
                self.plot_view = self.node[self.dims[0]]
                self.row_count = self.plot_view.shape[0]
                self.column_count = len(self.compound_names)

        else:
            self.row_count = 1
            self.column_count = 1

        self.endResetModel()