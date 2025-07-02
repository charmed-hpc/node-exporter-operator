#!/usr/bin/env python3
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

"""Node Exporter Lifecycle."""

import logging
import shutil
import subprocess
import tarfile
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib import request

from constants import (
    NODE_EXPORTER_BIN,
    NODE_EXPORTER_GROUP_NAME,
    NODE_EXPORTER_PORT,
    NODE_EXPORTER_SYSCONFIG_FILE,
    NODE_EXPORTER_SYSTEMD_SERVICE_FILE,
    NODE_EXPORTER_SYSTEMD_SERVICE_NAME,
    NODE_EXPORTER_TEXTFILE_DIR,
    NODE_EXPORTER_USER_NAME,
    NODE_EXPORTER_VAR_LIB_DIR,
    SYSCONFIG_DIR,
)

logger = logging.getLogger()


class NodeExporterOpsError(Exception):
    """Exception raised when an `node-exporter`-related operation on the unit has failed."""

    @property
    def message(self) -> str:
        """Return message passed as argument to exception."""
        return self.args[0]


def install(version: str, arch: str = "amd64") -> None:
    """Download appropriate files and install node-exporter.

    This function downloads the package, extracts it to /usr/bin/, create
    node-exporter user and group, and creates the systemd service unit.

    Args:
        version: a string representing the version to install.
        arch: the hardware architecture (e.g. amd64, armv7).
    """
    logger.debug(f"## Installing node_exporter {version}")

    # Download file
    url = f"https://github.com/prometheus/node_exporter/releases/download/v{version}/node_exporter-{version}.linux-{arch}.tar.gz"
    logger.debug(f"## Downloading {url}")
    output = Path("/tmp/node-exporter.tar.gz")
    fname, headers = request.urlretrieve(url, output)

    # Extract it
    tar = tarfile.open(output, "r")
    with TemporaryDirectory(prefix="omni") as tmp_dir:
        logger.debug(f"## Extracting {tar} to {tmp_dir}")
        tar.extractall(path=tmp_dir)

        logger.debug("## Installing node_exporter")
        source = Path(tmp_dir) / f"node_exporter-{version}.linux-{arch}/node_exporter"
        shutil.copy2(source, NODE_EXPORTER_BIN)

    # clean up
    output.unlink()

    _create_node_exporter_user_group()
    _create_systemd_service_unit()
    _render_sysconfig()


def start() -> None:
    """Start node_exporter via systemctl."""
    logger.debug("## Starting node_exporter")
    try:
        subprocess.call(["systemctl", "start", NODE_EXPORTER_SYSTEMD_SERVICE_NAME])
    except subprocess.CalledProcessError:
        msg = "Error starting node exporter."
        logger.error(msg)
        raise NodeExporterOpsError(msg)


def uninstall() -> None:
    """Uninstall node_exporter."""
    logger.debug("## Uninstalling node_exporter")
    try:
        subprocess.call(["systemctl", "stop", NODE_EXPORTER_SYSTEMD_SERVICE_NAME])
        subprocess.call(["systemctl", "disable", NODE_EXPORTER_SYSTEMD_SERVICE_NAME])
    except subprocess.CalledProcessError:
        logger.error("Error stopping node exporter.")

    paths_to_unlink = [
        NODE_EXPORTER_BIN,
        NODE_EXPORTER_SYSTEMD_SERVICE_FILE,
        NODE_EXPORTER_SYSCONFIG_FILE,
    ]
    for node_exporter_path in paths_to_unlink:
        if node_exporter_path.exists():
            node_exporter_path.unlink()

    if NODE_EXPORTER_VAR_LIB_DIR.exists():
        shutil.rmtree(NODE_EXPORTER_VAR_LIB_DIR)

    try:
        subprocess.call(["userdel", NODE_EXPORTER_USER_NAME])
        subprocess.call(["groupdel", NODE_EXPORTER_GROUP_NAME])
    except subprocess.CalledProcessError:
        logger.error("Error removing node exporter user and group.")


def _create_node_exporter_user_group() -> None:
    logger.debug(f"## Creating '{NODE_EXPORTER_GROUP_NAME}' group")
    try:
        subprocess.call(["groupadd", NODE_EXPORTER_GROUP_NAME])
    except subprocess.CalledProcessError:
        msg = f"Error creating group: '{NODE_EXPORTER_GROUP_NAME}'."
        logger.error(msg)
        raise NodeExporterOpsError(msg)

    logger.debug(f"## Creating '{NODE_EXPORTER_USER_NAME}' user")
    cmd = [
        "useradd",
        "--system",
        "--no-create-home",
        f"--gid={NODE_EXPORTER_USER_NAME}",
        "--shell=/usr/sbin/nologin",
        f"{NODE_EXPORTER_USER_NAME}",
    ]
    try:
        subprocess.call(cmd)
    except subprocess.CalledProcessError:
        msg = f"Error creating user: '{NODE_EXPORTER_USER_NAME}'."
        logger.error(msg)
        raise NodeExporterOpsError(msg)


def _create_systemd_service_unit() -> None:
    """Create the node_exporter systemd service unit."""
    logger.debug("## Creating systemd service unit for node_exporter")

    service = f"{NODE_EXPORTER_SYSTEMD_SERVICE_NAME}.service"
    shutil.copyfile(
        Path("./src/templates") / f"{NODE_EXPORTER_SYSTEMD_SERVICE_NAME}.service",
        f"{NODE_EXPORTER_SYSTEMD_SERVICE_FILE}",
    )

    try:
        subprocess.call(["systemctl", "daemon-reload"])
        subprocess.call(["systemctl", "enable", service])
    except subprocess.CalledProcessError:
        msg = f"Error creating node_exporter service: '{NODE_EXPORTER_SYSTEMD_SERVICE_NAME}'."
        logger.error(msg)
        raise NodeExporterOpsError(msg)


def _render_sysconfig() -> None:
    """Render the sysconfig file."""
    logger.debug("## Writing sysconfig file")

    if not SYSCONFIG_DIR.exists():
        SYSCONFIG_DIR.mkdir()

    if not NODE_EXPORTER_TEXTFILE_DIR.exists():
        NODE_EXPORTER_TEXTFILE_DIR.mkdir(parents=True)

    shutil.chown(
        NODE_EXPORTER_VAR_LIB_DIR,
        user=NODE_EXPORTER_USER_NAME,
        group=NODE_EXPORTER_GROUP_NAME,
    )
    shutil.chown(
        NODE_EXPORTER_TEXTFILE_DIR,
        user=NODE_EXPORTER_USER_NAME,
        group=NODE_EXPORTER_GROUP_NAME,
    )

    template_file = Path("./src/templates/node_exporter.tmpl")

    if NODE_EXPORTER_SYSCONFIG_FILE.exists():
        NODE_EXPORTER_SYSCONFIG_FILE.unlink()

    NODE_EXPORTER_SYSCONFIG_FILE.write_text(
        template_file.read_text().format(listen_address=f"0.0.0.0:{NODE_EXPORTER_PORT}")
    )


def version() -> str:
    """Return the node_exporter version."""
    vers = ""
    try:
        vers = subprocess.check_output(["node_exporter", "--version"], text=True)
    except subprocess.CalledProcessError:
        msg = "Error getting node_expoter version."
        logger.error(msg)
        raise NodeExporterOpsError(msg)
    return vers.split()[2]
