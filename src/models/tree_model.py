"""
包含HDF5文件结构树形模型。
"""

import h5py
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QStandardItem, QStandardItemModel, QBrush

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.resources import get_icon


class TreeModel(QStandardItemModel):
    """显示HDF5文件结构的树形模型。"""

    def __init__(self, hdf):
        super().__init__()

        self.hdf = hdf
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["对象", "属性", "数据集"])

        # 添加根节点和直接子节点
        root = self.add_node(self, "/", self.hdf)
        for name, node in self.hdf.items():
            self.add_node(root, name, node)

    def add_node(self, parent_item, name, node):
        """返回描述节点的树项。"""
        if name != "/":
            path = f"{parent_item.data(Qt.UserRole)}/{name}"
        else:
            path = "/"

        tree_item = QStandardItem(name)
        tree_item.setData(path, Qt.UserRole)
        tree_item.setToolTip(path)

        num_attrs = len(node.attrs)
        if num_attrs > 0:
            attrs_item = QStandardItem(str(num_attrs))
        else:
            attrs_item = QStandardItem("")

        attrs_item.setForeground(QBrush(Qt.darkGray))

        if isinstance(node, h5py.Dataset):
            tree_item.setIcon(get_icon("dataset.svg"))
            dataset_item = QStandardItem(str(node.shape))

        elif isinstance(node, h5py.Group):
            tree_item.setIcon(get_icon("folder.svg"))
            dataset_item = QStandardItem("")

        dataset_item.setForeground(QBrush(Qt.darkGray))

        parent_item.appendRow([tree_item, attrs_item, dataset_item])
        return tree_item

    def handle_expanded(self, index):
        """动态填充树视图。"""
        item = self.itemFromIndex(index)

        if not item.hasChildren():
            return

        item.setIcon(get_icon("folder-open.svg"))

        for row in range(item.rowCount()):
            child_item = item.child(row, 0)

            if not child_item or child_item.hasChildren():
                continue

            path = child_item.data(Qt.UserRole)
            child_node = self.hdf[path]

            if isinstance(child_node, h5py.Group):
                for name, node in child_node.items():
                    self.add_node(child_item, name, node)

    def handle_collapsed(self, index):
        """折叠组时更新图标。"""
        item = self.itemFromIndex(index)
        item.setIcon(get_icon("folder.svg"))