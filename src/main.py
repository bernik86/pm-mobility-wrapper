#!/usr/bin/env python3
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
import json
import subprocess
import os

# pylint: disable=import-error, no-name-in-module
from PySide6.QtWidgets import QApplication
# pylint: enable=import-error, no-name-in-module

from gui.gui import MainWindow


def load_config() -> tuple[dict[str, str], str]:

    file_path = os.path.dirname(__file__)
    config_fn = os.path.join(file_path, 'default.conf')
    with open(config_fn, "rt", encoding="utf-8") as conf_file:
        config = json.load(conf_file)

    remove = []
    for name, pkg_mgr in config.items():
        try:
            with subprocess.Popen(pkg_mgr['version'].split(),
                                  stdout=subprocess.PIPE) as process:

                _, errs = process.communicate(timeout=15)

                if errs is not None:
                    raise FileNotFoundError

        except FileNotFoundError:
            print(f"Package manager {name} not found!")
            remove.append(name)
            continue

    for name in remove:
        config.pop(name)

    return config, remove


def main():

    config, _ = load_config()

    app = QApplication()
    app.window = MainWindow(config)
    app.exec()

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
