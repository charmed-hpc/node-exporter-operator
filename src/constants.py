# Copyright 2025 Vantage Compute Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""NodeExporterCharm Constants."""

from pathlib import Path

NODE_EXPORTER_PORT = 9100

NODE_EXPORTER_USER_NAME = "node_exporter"
NODE_EXPORTER_GROUP_NAME = "node_exporter"

NODE_EXPORTER_SYSTEMD_SERVICE_NAME = "node_exporter"

JOBS = [{"static_configs": [{"targets": [f"*:{NODE_EXPORTER_PORT}"]}]}]

NODE_EXPORTER_BIN = Path("/usr/bin/node_exporter")
NODE_EXPORTER_SYSTEMD_SERVICE_FILE = Path("/etc/systemd/system/node_exporter.service")
SYSCONFIG_DIR = Path("/etc/sysconfig")
NODE_EXPORTER_SYSCONFIG_FILE = SYSCONFIG_DIR / "node_exporter"
NODE_EXPORTER_VAR_LIB_DIR = Path("/var/lib/node_exporter")
NODE_EXPORTER_TEXTFILE_DIR = NODE_EXPORTER_VAR_LIB_DIR / "textfile_collector"
