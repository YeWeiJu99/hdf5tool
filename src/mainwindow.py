"""
包含主应用程序窗口的布局和功能。
"""

import os
from datetime import datetime

import h5py
from PySide6.QtCore import QRect, QSettings, Qt, QUrl
from PySide6.QtGui import QAction, QDesktopServices, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QDockWidget, QFileDialog, QMainWindow, 
    QMessageBox, QTabWidget
)

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from __init__ import __version__
from src.views import HDF5Widget
from src.resources import get_icon

WINDOW_TITLE = "HDF5Tool"
MAX_RECENT_FILES = 10


class MainWindow(QMainWindow):
    """定义hdf5tool应用程序的主窗口。"""

    def __init__(self, app):
        super().__init__()

        self.recent_file_actions = []

        self.setAcceptDrops(True)

        self.app = app
        self.setWindowTitle(WINDOW_TITLE)
        
        # 设置窗口图标
        self.setWindowIcon(get_icon("hdf5tool.svg"))

        self.init_actions()
        self.init_menus()
        self.init_toolbars()
        self.init_statusbar()
        self.init_dock_widgets()
        self.init_central_widget()

        self.load_settings()
        self.update_file_menus()

    def init_actions(self):
        """初始化动作。"""
        self.open_action = QAction(
            get_icon("folder-open.svg"),
            "打开(&O)...",
            self,
            shortcut=QKeySequence.Open,
            statusTip="打开文件",
            triggered=self.handle_open_file,
        )

        for _i in range(MAX_RECENT_FILES):
            self.recent_file_actions.append(
                QAction(
                    self,
                    visible=False,
                    triggered=self.handle_open_recent_file,
                )
            )

        self.close_action = QAction(
            "关闭(&C)",
            self,
            shortcut=QKeySequence.Close,
            statusTip="关闭文件",
            triggered=self.handle_close_file,
        )
        self.close_action.setEnabled(False)

        self.close_all_action = QAction(
            "全部关闭(&A)",
            self,
            statusTip="关闭所有文件",
            triggered=self.handle_close_all_files,
        )
        self.close_all_action.setEnabled(False)

        self.quit_action = QAction(
            "退出(&Q)",
            self,
            shortcut=QKeySequence.Quit,
            statusTip="退出应用程序",
            triggered=self.close,
        )

        self.prefs_action = QAction(
            "首选项(&P)...",
            self,
            shortcut=QKeySequence.Preferences,
            statusTip="首选项",
            triggered=self.handle_open_prefs,
        )

        self.about_action = QAction(
            "关于(&A)...",
            self,
            statusTip="关于",
            triggered=self.handle_open_about,
        )

        self.docs_action = QAction(
            get_icon("hdf5tool.ico"),
            "说明(&D)",
            self,
            statusTip="说明",
            triggered=self.handle_open_docs,
            shortcut=QKeySequence.HelpContents,
        )

        #
        # 绘图动作
        #

        self.add_plot_action = QAction(
            get_icon("plot.svg"),
            "添加绘图(&P)",
            self,
            statusTip="添加绘图",
            triggered=self.handle_add_plot,
        )

        self.add_image_action = QAction(
            get_icon("image.svg"),
            "添加图像(&I)",
            self,
            statusTip="添加图像视图",
            triggered=self.handle_add_image,
        )

    def init_menus(self):
        """初始化菜单。"""
        menu = self.menuBar()

        # 文件菜单
        self.file_menu = menu.addMenu("文件(&F)")
        self.file_menu.addAction(self.open_action)

        # 添加最近文件子菜单和项目
        self.recent_menu = self.file_menu.addMenu("最近打开(&R)")

        for action in self.recent_file_actions:
            self.recent_menu.addAction(action)

        self.file_menu.addSeparator()
        self.file_menu.addAction(self.close_action)
        self.file_menu.addAction(self.close_all_action)

        self.file_menu.addSeparator()
        self.file_menu.addAction(self.quit_action)

        # 编辑菜单 - 待完成
        # self.edit_menu = menu.addMenu('&Edit')
        # self.edit_menu.addAction(self.prefs_action)

        # 视图菜单
        self.view_menu = menu.addMenu("视图(&V)")

        # 帮助菜单
        self.help_menu = menu.addMenu("帮助(&H)")
        self.help_menu.addAction(self.docs_action)
        self.help_menu.addAction(self.about_action)

    def init_toolbars(self):
        """初始化工具栏。"""
        self.file_toolbar = self.addToolBar("文件")
        self.file_toolbar.setObjectName("file_toolbar")
        self.file_toolbar.addAction(self.open_action)

        self.plots_toolbar = self.addToolBar("绘图")
        self.plots_toolbar.setObjectName("plots_toolbar")
        self.plots_toolbar.addAction(self.add_plot_action)
        self.plots_toolbar.addAction(self.add_image_action)

        self.plots_toolbar.setEnabled(False)

    def init_statusbar(self):
        """初始化状态栏。"""
        self.status = self.statusBar()

    def init_dock_widgets(self):
        """初始化停靠窗口。"""
        MIN_DOCK_WIDTH = 240

        self.tree_dock = QDockWidget("文件结构", self)
        self.tree_dock.setObjectName("tree_dock")
        self.tree_dock.setMinimumWidth(MIN_DOCK_WIDTH)

        self.attrs_dock = QDockWidget("属性集", self)
        self.attrs_dock.setObjectName("attrs_dock")
        self.attrs_dock.setMinimumWidth(MIN_DOCK_WIDTH)

        self.dataset_dock = QDockWidget("数据集", self)
        self.dataset_dock.setObjectName("dataset_dock")
        self.dataset_dock.setMinimumWidth(MIN_DOCK_WIDTH)

        self.plot_settings_dock = QDockWidget("绘图设置", self)
        self.plot_settings_dock.setObjectName("plot_settings_dock")
        self.plot_settings_dock.setMinimumWidth(MIN_DOCK_WIDTH)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.tree_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.attrs_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dataset_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.plot_settings_dock)

        self.view_menu.addActions(
            [
                self.tree_dock.toggleViewAction(),
                self.attrs_dock.toggleViewAction(),
                self.dataset_dock.toggleViewAction(),
                self.plot_settings_dock.toggleViewAction(),
            ]
        )

    def init_central_widget(self):
        """初始化中央部件。"""
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.handle_close_file)
        self.tabs.currentChanged.connect(self.handle_tab_changed)

        self.setCentralWidget(self.tabs)

    def open_file(self, filename):
        """打开hdf5文件。"""
        try:
            hdf = h5py.File(filename, "r")
        except OSError as e:
            hdf = None
            QMessageBox.critical(
                self, "文件加载错误", f"<p>{e}</p><p>{filename}</p>"
            )

        # 从最近文件列表中移除文件名。如果有效，
        # 它将被添加回列表顶部。
        if filename in self.recent_files:
            self.recent_files.remove(filename)

        if hdf:
            # 将文件名添加到最近文件列表顶部
            self.recent_files.insert(0, filename)

            # 确保保留的最近文件不超过MAX_RECENT_FILES：
            if len(self.recent_files) > MAX_RECENT_FILES:
                self.recent_files = self.recent_files[:MAX_RECENT_FILES]

            # 为文件创建新的小部件和选项卡
            # 并选择它。
            hdf_widget = HDF5Widget(hdf)
            hdf_widget.tree_view.selectionModel().selectionChanged.connect(
                self.handle_tree_selection_changed
            )

            index = self.tabs.addTab(hdf_widget, os.path.basename(filename))
            self.tabs.setCurrentIndex(index)

        self.update_file_menus()

    def load_settings(self):
        """从设置文件加载应用程序设置。"""
        settings = QSettings()

        # 恢复窗口几何形状
        geometry = settings.value("geometry")

        if geometry and not geometry.isEmpty():
            self.restoreGeometry(geometry)
        else:
            screen = self.app.primaryScreen()
            geometry = screen.availableGeometry()
            self.setGeometry(
                QRect(0, 0, int(geometry.width() * 0.8), int(geometry.height() * 0.7))
            )

        # 恢复窗口状态
        window_state = settings.value("windowState")

        if window_state and not window_state.isEmpty():
            self.restoreState(window_state)

        # 加载最近文件列表
        self.recent_files = settings.value("recentFiles") or []
        if isinstance(self.recent_files, str):
            self.recent_files = [self.recent_files]

    def save_settings(self):
        """将应用程序设置保存到文件。"""
        settings = QSettings()

        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.setValue("recentFiles", self.recent_files)

    def get_dropped_files(self, event):
        """获取拖放到应用程序上的文件列表。"""
        return [
            url.toLocalFile()
            for url in event.mimeData().urls()
            if os.path.isfile(url.toLocalFile())
        ]

    def update_file_menus(self):
        """更新文件菜单，启用/禁用选项。"""
        count = self.tabs.count()
        self.close_action.setEnabled(count > 0)
        self.close_all_action.setEnabled(count > 1)

        for index, filename in enumerate(self.recent_files):
            action = self.recent_file_actions[index]
            action.setText(filename)
            action.setVisible(True)

    #
    # 槽函数
    #

    def handle_tab_changed(self, index):
        """当选项卡更改时，适当地设置停靠窗口中的视图。"""
        title = WINDOW_TITLE

        hdf5widget = self.tabs.currentWidget()

        if hdf5widget:
            title = f"{title} - {hdf5widget.hdf.filename}"

            self.tree_dock.setWidget(hdf5widget.tree_view)
            self.attrs_dock.setWidget(hdf5widget.attrs_view)
            self.dataset_dock.setWidget(hdf5widget.dataset_view)
            self.plot_settings_dock.setWidget(hdf5widget.plot_settings_view)
        else:
            self.tree_dock.setWidget(None)
            self.attrs_dock.setWidget(None)
            self.dataset_dock.setWidget(None)
            self.plot_settings_dock.setWidget(None)

        self.setWindowTitle(title)
        self.tabs.setMovable(bool(self.tabs.count() > 1))

        # 启用/禁用绘图工具栏
        self.handle_tree_selection_changed()

    def handle_open_file(self):
        """打开文件。"""
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "QFileDialog.getOpenFileName()",
            "",
            "HDF5文件 (*.hdf *.h5 *.hdf5);; 所有文件 (*.*)",
            options=options,
        )

        if filename:
            self.open_file(filename)

    def handle_open_recent_file(self):
        """从最近文件列表中打开文件。"""
        self.open_file(self.sender().text())

    def handle_close_file(self, index=None):
        """关闭文件。"""
        if index is None:
            index = self.tabs.currentIndex()

        widget = self.tabs.widget(index)
        self.tabs.removeTab(index)

        # TODO: 清理/关闭文件
        # widget.close_file()
        widget.deleteLater()

        # 更新关闭/全部关闭菜单项
        self.update_file_menus()

    def handle_close_all_files(self):
        """关闭所有打开的文件。"""
        count = self.tabs.count()
        for index in reversed(range(count)):
            self.handle_close_file(index)

    def handle_open_prefs(self):
        """显示首选项对话框。"""
        QMessageBox.information(self, "首选项", "<p>待完成...</p>")

    def handle_open_about(self):
        """显示关于对话框。"""
        y = datetime.now().year
        url1 = "https://github.com/tgwoodcock/hdf5view"
        url2 = "wait"
        s1 = "hdf5view开发者"
        s2 = "GitHub"
        QMessageBox.about(
            self,
            f"关于 {WINDOW_TITLE}",
            (
                f"<p>hdf5tool {__version__}</p>"
                f"<p>项目致敬:<a href={url1}>{s1}</a></p>"
                f"<p>项目源码:<a href={url2}>{s2}</a></p>"
            ),
        )

    def handle_open_docs(self):
        """打开本地README文档。"""
        readme_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")
        if os.path.exists(readme_path):
            url = QUrl.fromLocalFile(readme_path)
            if not QDesktopServices.openUrl(url):
                QMessageBox.warning(self, "打开文档", "无法打开README文档")
        else:
            QMessageBox.warning(self, "打开文档", "README文档不存在")

    def handle_tree_selection_changed(self):
        """
        当树选择更改时，
        启用/禁用绘图工具栏。
        """
        self.plots_toolbar.setEnabled(False)

        hdf5widget = self.tabs.currentWidget()

        if not hdf5widget:
            return

        indexes = hdf5widget.tree_view.selectedIndexes()

        if not indexes:
            return

        index = indexes[0]
        path = hdf5widget.tree_model.itemFromIndex(index).data(Qt.UserRole)
        obj = hdf5widget.hdf[path]
        self.plots_toolbar.setEnabled(isinstance(obj, h5py.Dataset))



    def handle_add_plot(self):
        """显示绘图窗口。"""
        hdf5widget = self.tabs.currentWidget()
        hdf5widget.add_plot()

    def handle_add_image(self):
        """显示图像窗口。"""
        hdf5widget = self.tabs.currentWidget()
        hdf5widget.add_image()

    #
    # 事件
    #

    def dragEnterEvent(self, event):
        """接受任何拖放的文件。"""
        event.accept() if self.get_dropped_files(event) else event.ignore()

    def dropEvent(self, event):
        """打开拖放的文件。"""
        for file in self.get_dropped_files(event):
            self.open_file(file)

    def closeEvent(self, event):
        """关闭应用程序时进行清理。"""
        self.handle_close_all_files()
        self.save_settings()
        super().closeEvent(event)