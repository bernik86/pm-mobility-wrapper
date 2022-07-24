#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 bernik86.
#
# This file is part of PM Mobility Wrapper
# (see https://github.com/bernik86/pm-mobility-wrapper).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
from functools import partial

# pylint: disable=import-error, no-name-in-module
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QDockWidget
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QScroller
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt


from commands.get_data import list_all_pkgs
from commands.get_data import pkg_info
from commands.get_data import search_pkg
from commands.apply_changes import refresh_repos
from commands.apply_changes import upgrade_system
from commands.apply_changes import apply_changes
# pylint: enable=import-error, no-name-in-module

COLOR_INSTALLED = Qt.green
COLOR_MARKED_INSTALL = Qt.yellow
COLOR_MARKED_REMOVE = Qt.red


class MainWindow(QMainWindow):

    def __init__(self, config: dict[str, str]):
        super().__init__()
        self.showMaximized()
        self.setWindowTitle("PM Mobility Wrapper V0.1")

        self.config = config
        self.pkg_mgr = next(name for name in config)

        self.marked_pkgs = {}
        self.marked_pkgs['to_install'] = set()
        self.marked_pkgs['to_remove'] = set()

        self.search_bar_widgets = self.search_bar()
        self.dock = QDockWidget()
        self.dock.setWidget(self.search_bar_widgets[0])
        self.dock.setFeatures(QDockWidget.NoDockWidgetFeatures)

        actions = self.actions()
        self.apply_button = actions[1]

        self.addDockWidget(Qt.TopDockWidgetArea, self.dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, actions[0])

        self.pkg_list = QListWidget()
        self.pkg_list.itemClicked.connect(self.item_clicked)
        self.pkg_list.setSelectionMode(QAbstractItemView.NoSelection)
        self.pkg_last_selected = None

        scroll = QScroller()
        scroll.grabGesture(self.pkg_list,
                           gestureType=QScroller.ScrollerGestureType.TouchGesture)

        self.setCentralWidget(self.pkg_list)
        self.show()

    def search(self):
        text = self.search_bar_widgets[1].text()

        if not text:
            pkg_list = list_all_pkgs(self.config[self.pkg_mgr])
        else:
            pkg_list = search_pkg(self.config[self.pkg_mgr], text)

        self.populate_list(pkg_list)

    def populate_list(self, pkg_list: list[bytes]):

        self.pkg_list.clear()
        pkg_mgr = self.config[self.pkg_mgr]
        row = 0
        for line in pkg_list:
            if len(line) == 0:
                continue

            pkg = parse_line(line.decode('utf-8'), pkg_mgr["type"])

            if pkg[0] == b'None':
                continue

            item = QListWidgetItem(pkg[0])
            if pkg[2]:
                if pkg[0] in self.marked_pkgs['to_remove']:
                    item.setBackground(COLOR_MARKED_REMOVE)
                else:
                    item.setBackground(COLOR_INSTALLED)

            elif pkg[0] in self.marked_pkgs['to_install']:
                item.setBackground(COLOR_MARKED_INSTALL)

            self.pkg_list.addItem(item)
            row += 1

    def search_bar(self) -> tuple[QWidget, QLineEdit, QComboBox]:

        widget = QWidget()
        v_layout = QVBoxLayout(widget)

        upgrade = QPushButton("Upgrade")
        upgrade.setMaximumWidth(100)
        upgrade.clicked.connect(partial(upgrade_system,
                                        self.config[self.pkg_mgr]))

        mgr_list = QComboBox()
        mgr_list.addItems(self.config)
        mgr_list.setMaximumWidth(500)

        refresh = QPushButton("Refresh")
        refresh.setMaximumWidth(100)
        refresh.clicked.connect(partial(refresh_repos,
                                        self.config[self.pkg_mgr]))

        layout_select = QHBoxLayout()
        layout_select.addWidget(upgrade)
        layout_select.addWidget(mgr_list)
        layout_select.addWidget(refresh)

        layout = QHBoxLayout()
        edit = QLineEdit()
        edit.setMaximumWidth(500)
        edit.returnPressed.connect(self.search)

        clear = QPushButton("⌦")
        clear.setMaximumWidth(100)
        clear.clicked.connect(edit.clear)

        search = QPushButton("Search")
        search.setMaximumWidth(100)
        search.clicked.connect(self.search)

        layout.addWidget(clear)
        layout.addWidget(edit)
        layout.addWidget(search)

        v_layout.addLayout(layout_select)
        v_layout.addLayout(layout)

        return widget, edit, mgr_list

    def actions(self) -> tuple[QDockWidget, QPushButton]:
        widget = QWidget()
        v_layout = QVBoxLayout(widget)
        layout = QHBoxLayout()

        clear_sel = QPushButton('Unmark')
        clear_sel.setMaximumWidth(100)
        clear_sel.clicked.connect(self.clear_pkg_selection)

        info = QPushButton('Info')
        info.setMaximumWidth(100)
        info.clicked.connect(self.info_clicked)

        mark_pkg = QPushButton('Mark')
        mark_pkg.setMaximumWidth(100)
        mark_pkg.clicked.connect(self.mark_pkgs)

        layout.addWidget(clear_sel)
        layout.addWidget(info)
        layout.addWidget(mark_pkg)

        layout_apply = QHBoxLayout()
        apply_chgs = QPushButton('Apply')
        apply_chgs.setMaximumWidth(327)
        apply_chgs.setEnabled(False)
        apply_chgs.clicked.connect(self.apply_changes)
        layout_apply.addWidget(apply_chgs)

        v_layout.addLayout(layout)
        v_layout.addLayout(layout_apply)

        dock = QDockWidget()
        dock.setWidget(widget)
        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        return dock, apply_chgs

    def clear_pkg_selection(self):

        self.apply_button.setEnabled(False)

        def find_item_and_reset_background(marked: set[str], background=Qt.white):
            for mkd in marked:
                items = self.pkg_list.findItems(mkd, Qt.MatchFixedString)
                for i in items:
                    i.setBackground(background)

        find_item_and_reset_background(self.marked_pkgs['to_install'])
        find_item_and_reset_background(self.marked_pkgs['to_remove'], COLOR_INSTALLED)

        self.marked_pkgs['to_install'] = set()
        self.marked_pkgs['to_remove'] = set()

    def mark_pkgs(self):
        self.apply_button.setEnabled(True)
        sel_items = self.pkg_list.selectedItems()

        for item in sel_items:
            if item.background() == COLOR_INSTALLED:
                self.marked_pkgs['to_remove'].add(item.text())
                item.setBackground(COLOR_MARKED_REMOVE)
            else:
                self.marked_pkgs['to_install'].add(item.text())
                item.setBackground(COLOR_MARKED_INSTALL)

        self.pkg_list.selectionModel().clear()

    def apply_changes(self):
        self.apply_button.setEnabled(False)
        apply_changes(self.config[self.pkg_mgr], self.marked_pkgs)
        self.pkg_list.clear()
        self.search_bar_widgets[1].clear()

    def item_clicked(self, item: QListWidgetItem):
        self.pkg_list.setSelectionMode(QAbstractItemView.MultiSelection)
        item.setSelected(not item.isSelected())
        self.pkg_last_selected = item.text()
        self.pkg_list.setSelectionMode(QAbstractItemView.NoSelection)

    def info_clicked(self):
        info = b"No package selected"
        if self.pkg_last_selected is not None:
            info = pkg_info(self.config[self.pkg_mgr], self.pkg_last_selected)
        info_dialog = QMessageBox()
        info_dialog.setWindowModality(Qt.ApplicationModal)
        info_dialog.setWindowTitle(f"Package details: {self.pkg_last_selected}")
        info_dialog.setText(info.decode("utf-8"))
        info_dialog.exec()


def parse_line(line: bytes, mgr_type: str) -> tuple[bytes, bytes, bool, bytes]:

    pkg = line.split()
    if mgr_type == "pacman-like":

        # pacman format: <repo>/<name> <vers> [installed]
        if line[0].isspace():
            return (b'None', b'None', False, b'None')

        repo, name = pkg[0].split('/')
        vers = pkg[1]
        inst = False
        if pkg[-1].startswith('[') and pkg[-1].endswith(']'):
            inst = True

    elif mgr_type == "apk-like":

        # APK format: <name>-<vers>-r* <discarded> [installed]
        pkg_apk = pkg[0].rsplit("-", maxsplit=2)
        name = pkg_apk[0]
        vers = pkg_apk[1]
        inst = False
        if pkg[-1].startswith('[') and pkg[-1].endswith(']'):
            inst = True
        repo = None

    return name, vers, inst, repo
