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
import subprocess


def list_all_pkgs(pkg_mgr: dict[str, str]) -> list[bytes]:

    command = pkg_mgr["list"].split()
    outs, errs = run(command)
    if errs is not None:
        return [b"Error listing packages"]

    return sorted(outs.split(b'\n'))


def search_pkg(pkg_mgr: dict[str, str], search_word: str) -> list[bytes]:

    command = pkg_mgr["search"].split()
    if pkg_mgr["type"] == "apk-like":
        search_word = f'*{search_word}*'
    command.append(search_word)

    outs, errs = run(command)
    if errs is not None:
        return [b"Error searching packages"]

    return sorted(outs.split(b'\n'))


def pkg_info(pkg_mgr: dict[str, str], pkg_name: str) -> bytes:

    command = pkg_mgr["info"].split()
    command.append(pkg_name)

    outs, errs = run(command)
    if errs is not None:
        return [b"Error getting information about package"]

    return outs


def run(command: list[str]) -> tuple[bytes, bytes]:

    with subprocess.Popen(command, stdout=subprocess.PIPE) as process:
        outps, errs = process.communicate(timeout=300)

    return outps, errs
