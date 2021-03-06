# ========================================================================== #
#                                                                            #
#    KVMD - The main Pi-KVM daemon.                                          #
#                                                                            #
#    Copyright (C) 2018  Maxim Devaev <mdevaev@gmail.com>                    #
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


import dataclasses

from typing import List
from typing import Dict


# =====
class IpmiPasswdError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__("Incorrect IPMI passwd file: " + msg)


@dataclasses.dataclass(frozen=True)
class IpmiUserCredentials:
    ipmi_user: str
    ipmi_passwd: str
    kvmd_user: str
    kvmd_passwd: str


class IpmiAuthManager:
    def __init__(self, path: str) -> None:
        with open(path) as passwd_file:
            self.__credentials = self.__parse_passwd_file(passwd_file.read().split("\n"))

    def __contains__(self, ipmi_user: str) -> bool:
        return (ipmi_user in self.__credentials)

    def __getitem__(self, ipmi_user: str) -> str:
        return self.__credentials[ipmi_user].ipmi_passwd

    def get_credentials(self, ipmi_user: str) -> IpmiUserCredentials:
        return self.__credentials[ipmi_user]

    def __parse_passwd_file(self, lines: List[str]) -> Dict[str, IpmiUserCredentials]:
        credentials: Dict[str, IpmiUserCredentials] = {}
        for (number, line) in enumerate(lines):
            if len(line.strip()) == 0 or line.lstrip().startswith("#"):
                continue

            if " -> " not in line:
                raise IpmiPasswdError(f"Missing ' -> ' operator at line #{number}")

            (left, right) = map(str.lstrip, line.split(" -> ", 1))
            for (name, pair) in [("left", left), ("right", right)]:
                if ":" not in pair:
                    raise IpmiPasswdError(f"Missing ':' operator in {name} credentials at line #{number}")

            (ipmi_user, ipmi_passwd) = left.split(":")
            ipmi_user = ipmi_user.strip()
            if len(ipmi_user) == 0:
                raise IpmiPasswdError(f"Empty IPMI user (left) at line #{number}")

            (kvmd_user, kvmd_passwd) = right.split(":")
            kvmd_user = kvmd_user.strip()
            if len(kvmd_user) == 0:
                raise IpmiPasswdError(f"Empty KVMD user (left) at line #{number}")

            if ipmi_user in credentials:
                raise IpmiPasswdError(f"Found duplicating user {ipmi_user!r} (left) at line #{number}")

            credentials[ipmi_user] = IpmiUserCredentials(
                ipmi_user=ipmi_user,
                ipmi_passwd=ipmi_passwd,
                kvmd_user=kvmd_passwd,
                kvmd_passwd=kvmd_passwd,
            )
        return credentials
