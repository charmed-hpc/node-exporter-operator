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

"""Node Exporter Charm."""

import logging

import ops
from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider

import node_exporter_ops as neo
from constants import JOBS, NODE_EXPORTER_PORT

logger = logging.getLogger(__name__)


class NodeExporterCharm(ops.CharmBase):
    """Charm the service."""

    def __init__(self, *args):
        """Initialize charm."""
        super().__init__(*args)
        self.metrics_endpoint = MetricsEndpointProvider(self, jobs=JOBS)

        # juju core hooks
        self.framework.observe(self.on.install, self._on_install)
        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.stop, self._on_stop)

    def _on_install(self, event: ops.InstallEvent) -> None:
        """Install node_exporter."""
        self.unit.status = ops.MaintenanceStatus("Installing node-exporter...")

        node_exporter_version = self.model.config.get("node-exporter-version")
        if (
            isinstance(node_exporter_version, str)
            and (node_exporter_version is not None)
            and (node_exporter_version != "")
        ):
            neo.install(node_exporter_version)
            self.unit.set_workload_version(neo.version())
            self.unit.open_port("tcp", NODE_EXPORTER_PORT)
            self.unit.status = ops.ActiveStatus("node-exporter installed")
        else:
            self.unit.status = ops.BlockedStatus("Need node-exporter-version config to continue.")
            event.defer()

    def _on_start(self, event: ops.StartEvent) -> None:
        """Start node_exporter."""
        self.unit.status = ops.MaintenanceStatus("Starting node-exporter...")
        neo.start()
        self.unit.status = ops.ActiveStatus()

    def _on_stop(self, event: ops.StopEvent) -> None:
        """Stop, disable, and remove node_exporter."""
        self.unit.status = ops.MaintenanceStatus("Uninstalling node-exporter...")
        neo.uninstall()


if __name__ == "__main__":
    ops.main(NodeExporterCharm)
