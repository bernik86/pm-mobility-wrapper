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

from subprocess import PIPE, run


def refresh_repos(pkg_mgr: dict[str, str]):

    command = f'{pkg_mgr["terminal"]} "sudo {pkg_mgr["update"]}"'
    run(command, stdin=PIPE, stderr=PIPE, stdout=PIPE, shell=True, check=True)


def upgrade_system(pkg_mgr: dict[str, str]):

    command = f'{pkg_mgr["terminal"]} "sudo {pkg_mgr["upgrade"]}"'
    run(command, stdin=PIPE, stderr=PIPE, stdout=PIPE, shell=True, check=True)


def apply_changes(pkg_mgr: dict[str, str], marked: dict[str, set[str]]):

    if len(marked['to_remove']):
        remove_list = ' '.join(marked['to_remove'])
        command = f'{pkg_mgr["terminal"]} "sudo {pkg_mgr["remove"]} {remove_list}"'
        run(command, stdin=PIPE, stderr=PIPE, stdout=PIPE, shell=True, check=True)

    if len(marked['to_install']):
        add_list = ' '.join(marked['to_install'])
        command = f'{pkg_mgr["terminal"]} "sudo {pkg_mgr["install"]} {add_list}"'
        run(command, stdin=PIPE, stderr=PIPE, stdout=PIPE, shell=True, check=True)
