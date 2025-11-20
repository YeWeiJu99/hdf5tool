"""
包含HDF5属性、数据集和数据表格模型。
"""

import h5py
from PySide6.QtCore import (
    QAbstractItemModel, QAbstractTableModel, QModelIndex, Qt
)
from PySide6.QtGui import QBrush, QColor

INVALID_QModelIndex = QModelIndex()


class AttributesTableModel(QAbstractTableModel):
    """
    包含HDF5文件中数据集任何属性的模型。
    """

    HEADERS = ("名称", "值", "类型")

    def __init__(self, hdf):
        super().__init__()

        self.hdf = hdf
        self.node = None
        self.column_count = 3
        self.row_count = 0

    def update_node(self, path):
        """更新当前节点路径。"""
        self.beginResetModel()
        self.node = self.hdf[path]

        self.keys = list(self.node.attrs.keys())
        self.values = list(self.node.attrs.values())

        self.row_count = len(self.keys)
        self.endResetModel()

    def rowCount(self, parent=INVALID_QModelIndex):
        """返回行数。"""
        return self.row_count

    def columnCount(self, parent=INVALID_QModelIndex):
        """返回列数。"""
        return self.column_count

    def headerData(self, section, orientation, role):
        """返回有关表头的数据。"""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.HEADERS[section]
            else:
                return str(section)

    def data(self, index, role=Qt.DisplayRole):
        """返回用于显示的属性。"""
        if index.isValid():
            column = index.column()
            row = index.row()

            if role in (Qt.DisplayRole, Qt.ToolTipRole):
                if column == 0:
                    return self.keys[row]
                elif column == 1:
                    try:
                        return self.values[row].decode()
                    except AttributeError:
                        return str(self.values[row])
                elif column == 2:
                    return str(type(self.values[row]))


class DatasetTableModel(QAbstractTableModel):
    """
    包含HDF5文件中数据集各种描述符的模型，
    当前这些描述符是：
    'name', 'dtype', 'ndim', 'shape', 'maxshape',
    'chunks', 'compression', 'shuffle', 'fletcher32'
    和 'scaleoffset'。
    """

    HEADERS = ("名称", "值")

    def __init__(self, hdf):
        super().__init__()

        self.hdf = hdf
        self.node = None
        self.column_count = 2
        self.row_count = 0

    def update_node(self, path):
        """更新当前节点路径。"""
        self.keys = []
        self.values = []

        self.beginResetModel()
        self.node = self.hdf[path]

        if not isinstance(self.node, h5py.Dataset):
            self.endResetModel()
            return

        self.keys = (
            "name",
            "dtype",
            "ndim",
            "shape",
            "maxshape",
            "chunks",
            "compression",
            "shuffle",
            "fletcher32",
            "scaleoffset",
        )

        compound_names = self.node.dtype.names

        if compound_names:
            self.values = (
                str(self.node.name),
                str(self.node.dtype),
                str(self.node.ndim),
                f"{self.node.shape}  (ncols={len(compound_names)})",
                str(self.node.maxshape),
                str(self.node.chunks),
                str(self.node.compression),
                str(self.node.shuffle),
                str(self.node.fletcher32),
                str(self.node.scaleoffset),
            )

        else:
            self.values = (
                str(self.node.name),
                str(self.node.dtype),
                str(self.node.ndim),
                str(self.node.shape),
                str(self.node.maxshape),
                str(self.node.chunks),
                str(self.node.compression),
                str(self.node.shuffle),
                str(self.node.fletcher32),
                str(self.node.scaleoffset),
            )

        self.row_count = len(self.keys)
        self.endResetModel()

    def rowCount(self, parent=INVALID_QModelIndex):
        """返回行数。"""
        return self.row_count

    def columnCount(self, parent=INVALID_QModelIndex):
        """返回列数。"""
        return self.column_count

    def headerData(self, section, orientation, role):
        """返回有关表头的数据。"""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.HEADERS[section]
            else:
                return str(section)

    def data(self, index, role=Qt.DisplayRole):
        """返回用于显示的数据集属性。"""
        if index.isValid():
            column = index.column()
            row = index.row()

            if isinstance(self.node, h5py.Dataset):
                if role in (Qt.DisplayRole, Qt.ToolTipRole):
                    if column == 0:
                        return self.keys[row]
                    elif column == 1:
                        return self.values[row]

                if (
                    role == Qt.ForegroundRole
                    and row == 3
                    and column == 1
                    and self.node.dtype.names
                ):
                    return QColor("red")


class DataTableModel(QAbstractTableModel):
    """包含HDF5文件中数据集数据的模型。"""

    def __init__(self, hdf):
        super().__init__()

        self.hdf = hdf
        self.node = None
        self.row_count = 0
        self.column_count = 0
        self.ndim = 0
        self.dims = ()
        self.data_view = None
        self.compound_names = None

    def update_node(self, path):
        """更新当前节点路径。"""
        self.compound_names = None

        self.beginResetModel()

        self.row_count = 0
        self.column_count = 0

        self.dims = ()

        self.node = self.hdf[path]

        if not isinstance(self.node, h5py.Dataset):
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
            self.dims = tuple([slice(None)])

        elif self.ndim == 2:
            self.row_count = shape[-2]
            self.column_count = shape[-1]
            self.dims = tuple([slice(None), slice(None)])

        elif self.ndim > 2 and shape[-1] in [3, 4]:
            self.row_count = shape[-3]
            self.column_count = shape[-2]
            self.dims = tuple(
                ([0] * (self.ndim - 3)) + [slice(None), slice(None), slice(None)]
            )

        else:
            self.row_count = shape[-2]
            self.column_count = shape[-1]
            self.dims = tuple(([0] * (self.ndim - 2)) + [slice(None), slice(None)])

        self.data_view = self.node[self.dims]
        self.endResetModel()

    def rowCount(self, parent=INVALID_QModelIndex):
        """返回行数。"""
        return self.row_count

    def columnCount(self, parent=INVALID_QModelIndex):
        """返回列数。"""
        return self.column_count

    def headerData(self, section, orientation, role):
        """返回有关表头的数据。"""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if self.compound_names:
                    return self.compound_names[section]
                else:
                    if self.ndim in [0, 1]:
                        return None

                    if self.ndim == 2:
                        w = list(range(self.node.shape[1]))
                        w_e = w[self.dims[1]]
                        if isinstance(w_e, int):
                            w_e = [w_e]
                        return str(w_e[section])

                    s_loc = [i for i, j in enumerate(self.dims) if isinstance(j, slice)]
                    if self.ndim > 2:
                        if len(s_loc) >= 2:
                            idx = 1
                            w = list(range(self.node.shape[s_loc[idx]]))
                            w_e = w[self.dims[s_loc[idx]]]
                            if isinstance(w_e, int):
                                w_e = [w_e]
                            return str(w_e[section])
                        return None

            elif orientation == Qt.Vertical:
                if self.ndim == 0:
                    return None

                if self.ndim in [1, 2]:
                    w = list(range(self.node.shape[0]))
                    w_e = w[self.dims[0]]
                    if isinstance(w_e, int):
                        w_e = [w_e]

                    return str(w_e[section])

                s_loc = [i for i, j in enumerate(self.dims) if isinstance(j, slice)]
                if self.ndim > 2:
                    if len(s_loc) >= 1:
                        idx = 0
                        w = list(range(self.node.shape[s_loc[idx]]))
                        w_e = w[self.dims[s_loc[idx]]]
                        if isinstance(w_e, int):
                            w_e = [w_e]
                        return str(w_e[section])
                    return None

        super().headerData(section, orientation, role)

    def data(self, index, role=Qt.DisplayRole):
        """返回用于显示的表数据。"""
        if index.isValid() and role in (Qt.DisplayRole, Qt.ToolTipRole):
            if self.compound_names:
                name = self.compound_names[index.column()]
                if self.data_view.ndim == 0:
                    try:
                        q = self.data_view[name].decode()
                    except AttributeError:
                        q = str(self.data_view[name])
                else:
                    try:
                        q = self.data_view[index.row()][name].decode()
                    except AttributeError:
                        q = str(self.data_view[index.row()][name])

                return q

            if self.ndim == 0:
                try:
                    q = self.data_view.decode()
                except (AttributeError, TypeError):
                    q = str(self.data_view)
            else:
                if self.data_view.ndim == 0:
                    try:
                        q = self.data_view.decode()
                    except AttributeError:
                        q = str(self.data_view)
                elif self.data_view.ndim == 1:
                    try:
                        q = self.data_view[index.row()].decode()
                    except AttributeError:
                        q = str(self.data_view[index.row()])
                elif self.data_view.ndim >= 2:
                    try:
                        q = self.data_view[index.row(), index.column()].decode()
                    except AttributeError:
                        q = str(self.data_view[index.row(), index.column()])

            return q

    def set_dims(self, dims):
        """设置模型的维度。

        如果编辑了HDF5Widget.dims_view中的维度，
        则调用此函数。模型的维度被更新以匹配输入维度。
        """
        self.beginResetModel()

        self.row_count = None
        self.column_count = None

        self.dims = []
        self.shape = self.node.shape

        from src.models.utils import get_dims_from_str
        self.dims = get_dims_from_str(dims)

        if self.compound_names:
            if isinstance(self.dims[1], int):
                self.compound_names = tuple([self.node.dtype.names[self.dims[1]]])
            else:
                self.compound_names = self.node.dtype.names[self.dims[1]]
            self.column_count = len(self.compound_names)
            if isinstance(self.dims[0], int):
                dims = list(self.dims)
                dims[0] = slice(dims[0], dims[0] + 1, None)
                self.dims = tuple(dims)
            self.data_view = self.node[self.dims[0]][list(self.compound_names)]
            if self.data_view.ndim == 0:
                self.row_count = 1
            else:
                self.row_count = self.data_view.shape[0]

            self.endResetModel()
            return

        if self.ndim == 2 and isinstance(self.dims[0], int):
            dims = list(self.dims)
            dims[0] = slice(dims[0], dims[0] + 1, None)
            self.dims = tuple(dims)

        self.data_view = self.node[self.dims]

        try:
            self.row_count = self.data_view.shape[0]
        except IndexError:
            self.row_count = 1

        try:
            self.column_count = self.data_view.shape[1]
        except IndexError:
            self.column_count = 1

        self.endResetModel()


class DimsTableModel(QAbstractTableModel):
    """
    包含数据集当前维度的模型。
    此模型是可编辑的，允许用户更改数据集的索引，
    从而查看不同的切片。
    """

    def __init__(self, hdf):
        super().__init__()

        self.hdf = hdf
        self.node = None
        self.column_count = 0
        self.row_count = 1
        self.shape = ()
        self.compound_names = None

    def update_node(self, path, now_on_PlotView=False):
        """更新当前节点路径。"""
        self.compound_names = None
        self.column_count = 0
        self.shape = []

        self.beginResetModel()
        self.node = self.hdf[path]

        if not isinstance(self.node, h5py.Dataset) or self.node.dtype == "object":
            self.endResetModel()
            return

        self.compound_names = self.node.dtype.names

        if self.node.ndim == 1:
            if self.compound_names:
                self.shape = [":", ":"]
                self.column_count = 2
                if now_on_PlotView:
                    self.shape[-1] = "0"

            else:
                self.shape = [":"]
                self.column_count = 1

        elif self.node.ndim == 2:
            self.shape = [":", ":"]
            self.column_count = 2
            if now_on_PlotView:
                self.shape[-1] = "0"

        elif self.node.ndim > 2:
            if self.node.shape[-1] in [3, 4]:
                self.shape = (["0"] * (self.node.ndim - 3)) + [":", ":", ":"]
                self.column_count = len(self.shape)
                if now_on_PlotView:
                    self.shape[-2] = "0"
                    self.shape[-1] = "0"

            else:
                self.shape = (["0"] * (self.node.ndim - 2)) + [":", ":"]
                self.column_count = len(self.shape)
                if now_on_PlotView:
                    self.shape[-1] = "0"

        self.endResetModel()

    def rowCount(self, parent=INVALID_QModelIndex):
        """返回行数。"""
        return self.row_count

    def columnCount(self, parent=INVALID_QModelIndex):
        """返回列数。"""
        return self.column_count

    def headerData(self, section, orientation, role):
        """返回有关表头的数据。"""
        if role == Qt.DisplayRole:
            return str(section)

    def data(self, index, role=Qt.DisplayRole):
        """返回用于显示的维度属性。"""
        if index.isValid():
            if role == Qt.DisplayRole:
                return self.shape[index.column()]

            elif role == Qt.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignVCenter + Qt.AlignmentFlag.AlignHCenter

    def flags(self, index):
        """返回特定索引的标志。"""
        flags = super().flags(index)
        flags |= Qt.ItemIsEditable
        return flags

    def setData(self, index, value, role):
        """更新维度数据。"""
        if index.isValid() and role == Qt.EditRole:
            column = index.column()
            value = value.strip()

            if ":" not in value:
                try:
                    num = int(value)
                    if self.compound_names and column == 1:
                        if num < 0 or num >= len(self.node.dtype.names):
                            return False
                    else:
                        if num < 0 or num >= self.node.shape[column]:
                            return False

                except ValueError:
                    return False

            self.shape[column] = value
            self.dataChanged.emit(index, index, [])
            return True

        return False