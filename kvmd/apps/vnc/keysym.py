# ========================================================================== #
#                                                                            #
#    KVMD - The main Pi-KVM daemon.                                          #
#                                                                            #
#    Copyright (C) 2020  Maxim Devaev <mdevaev@gmail.com>                    #
#                                                                            #
#    This program is free software: you can redistribute it and/or modify    #
#    it under the terms of the GNU General Public License as published by    #
#    the Free Software Foundation, either version 3 of the License, or       #
#    (at your option) any later version.                                     #
#                                                                            #
#    This program is distributed in the hope that it will be useful,         #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#    GNU General Public License for more details.                            #
#                                                                            #
#    You should have received a copy of the GNU General Public License       #
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.  #
#                                                                            #
# ========================================================================== #


import pkgutil
import functools

from typing import Dict

import Xlib.keysymdef

from ...logging import get_logger

from ... import keymap


# =====
def build_symmap(path: str) -> Dict[int, str]:
    # https://github.com/qemu/qemu/blob/95a9457fd44ad97c518858a4e1586a5498f9773c/ui/keymaps.c

    symmap: Dict[int, str] = {}
    for (x11_code, at1_code) in keymap.X11_TO_AT1.items():
        symmap[x11_code] = keymap.AT1_TO_WEB[at1_code]

    for (x11_code, at1_code) in _read_keyboard_layout(path).items():
        if (web_name := keymap.AT1_TO_WEB.get(at1_code)) is not None:  # noqa: E203,E231
            # mypy bug
            symmap[x11_code] = web_name  # type: ignore
    return symmap


# =====
@functools.lru_cache()
def _get_keysyms() -> Dict[str, int]:
    keysyms: Dict[str, int] = {}
    for (loader, module_name, _) in pkgutil.walk_packages(Xlib.keysymdef.__path__):
        module = loader.find_module(module_name).load_module(module_name)
        for keysym_name in dir(module):
            if keysym_name.startswith("XK_"):
                short_name = keysym_name[3:]
                if short_name.startswith("XF86_"):
                    short_name = "XF86" + short_name[5:]
                # assert short_name not in keysyms, short_name
                keysyms[short_name] = int(getattr(module, keysym_name))
    return keysyms


def _resolve_keysym(name: str) -> int:
    code = _get_keysyms().get(name)
    if code is not None:
        return code
    if len(name) == 5 and name[0] == "U":  # Try unicode Uxxxx
        try:
            return int(name[1:], 16)
        except ValueError:
            pass
    return 0


def _read_keyboard_layout(path: str) -> Dict[int, int]:  # Keysym to evdev (at1)
    logger = get_logger(0)
    logger.info("Reading keyboard layout %s ...", path)

    with open(path) as layout_file:
        lines = list(map(str.strip, layout_file.read().split("\n")))

    layout: Dict[int, int] = {}
    for (number, line) in enumerate(lines):
        if len(line) == 0 or line.startswith(("#", "map ", "include ")):
            continue

        parts = line.split()
        if len(parts) >= 2:
            if (code := _resolve_keysym(parts[0])) != 0:  # noqa: E203,E231
                try:
                    layout[code] = int(parts[1], 16)
                except ValueError as err:
                    logger.error("Can't parse layout line #%d: %s", number, str(err))
    return layout
