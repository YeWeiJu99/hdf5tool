"""
模型模块重定向文件。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.tree_model import TreeModel
from src.models.table_models import (
    AttributesTableModel,
    DatasetTableModel,
    DataTableModel,
    DimsTableModel
)
from src.models.view_models import (
    ImageModel,
    PlotModel
)
from src.models.utils import get_dims_from_str

# 导出所有类，以保持向后兼容性
__all__ = [
    'TreeModel',
    'AttributesTableModel',
    'DatasetTableModel',
    'DataTableModel',
    'DimsTableModel',
    'ImageModel',
    'PlotModel',
    'get_dims_from_str'
]