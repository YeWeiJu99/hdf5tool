"""
模型相关的工具函数。
"""


def get_dims_from_str(dims_as_str):
    """
    获取用户在hdf5widget.dims_view中输入的描述所需维度的字符串元组，
    并将其转换为可用于索引数据集中节点的整数和/或切片元组。

    从字符串创建切片的方法在此处给出：
    https://stackoverflow.com/questions/680826/python-create-slice-object-from-string/23895339

    参数
    ----------
    dims_as_str : 元组
        描述维度(dims)的字符串元组
        例如 ("0", "0", ":") 或 ("2:6:2", ":", "2", "3")。

    返回
    -------
    元组
       用于数组索引的整数和/或切片元组，
       例如 (0, 0, slice(None, None, None)) 或
       (slice(2, 6, 2), slice(None, None, None), 2, 3)，对应于上面给出的两个
       dims_as_str示例。

    示例
    --------
    >>> from hdf5view.models import get_dims_from_str
    >>> get_dims_from_str(("0", "0", ":"))
    (0, 0, slice(None, None, None))
    >>> get_dims_from_str(("2:6:2", ":", "2", "3"))
    (slice(2, 6, 2), slice(None, None, None), 2, 3)
    """
    dims = []
    for _i, value in enumerate(dims_as_str):
        try:
            v = int(value)
            dims.append(v)
        except (ValueError, TypeError):
            if ":" in value:
                value = value.strip()
                s = slice(
                    *map(
                        lambda x: int(x.strip()) if x.strip() else None,
                        value.split(":"),
                    )
                )
                dims.append(s)

    dims = tuple(dims)

    return dims