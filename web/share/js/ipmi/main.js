/*****************************************************************************
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
*****************************************************************************/


"use strict";


import {$, tools} from "../tools.js";


export function main() {
	__loadKvmdInfo();
}

function __loadKvmdInfo() {
	let http = tools.makeRequest("GET", "/api/info", function() {
		if (http.readyState === 4) {
			if (http.status === 200) {
				let port = JSON.parse(http.responseText).result.extras.ipmi.port;
				let host = window.location.hostname;
				let site = `${window.location.protocol}//${window.location.host}`;
				$("ipmi-text").innerHTML = `
					<span class="code-comment"># Power on the server if it's off:<br>
					$</span> ipmitool -I lanplus -U admin -P admin -H ${host} -p ${port} power on<br>
					<span class="code-comment">$</span> curl -XPOST -HX-KVMD-User:admin -HX-KVMD-Passwd:admin -k \\<br>
					&nbsp;&nbsp;&nbsp;&nbsp;${site}/api/atx/power?action=on<br>
					<br>
					<span class="code-comment"># Soft power off the server if it's on:<br>
					$</span> ipmitool -I lanplus -U admin -P admin -H ${host} -p ${port} power soft<br>
					<span class="code-comment">$</span> curl -XPOST -HX-KVMD-User:admin -HX-KVMD-Passwd:admin -k \\<br>
					&nbsp;&nbsp;&nbsp;&nbsp;${site}/api/atx/power?action=off<br>
					<br>
					<span class="code-comment"># Hard power off the server if it's on:<br>
					$</span> ipmitool -I lanplus -U admin -P admin -H ${host} -p ${port} power off<br>
					<span class="code-comment">$</span> curl -XPOST -HX-KVMD-User:admin -HX-KVMD-Passwd:admin -k \\<br>
					&nbsp;&nbsp;&nbsp;&nbsp;${site}/api/atx/power?action=off_hard<br>
					<br>
					<span class="code-comment"># Hard reset the server if it's on:<br>
					$</span> ipmitool -I lanplus -U admin -P admin -H ${host} -p ${port} power reset<br>
					<span class="code-comment">$</span> curl -XPOST -HX-KVMD-User:admin -HX-KVMD-Passwd:admin -k \\<br>
					&nbsp;&nbsp;&nbsp;&nbsp;${site}/api/atx/power?action=reset_hard<br>
					<br>
					<span class="code-comment"># Check the power status:<br>
					$</span> ipmitool -I lanplus -U admin -P admin -H ${host} -p ${port} power status<br>
					<span class="code-comment">$</span> curl -HX-KVMD-User:admin -HX-KVMD-Passwd:admin -k \\<br>
					&nbsp;&nbsp;&nbsp;&nbsp;${site}/api/atx
				`;
			} else if (http.status === 401 || http.status === 403) {
				document.location.href = "/login";
			} else {
				setTimeout(__loadKvmdInfo, 1000);
			}
		}
	});
}
