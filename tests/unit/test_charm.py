# Copyright 2025 (c) Vantage Compute Corporation
"""Node Exporter Operator Charm Tests."""

from unittest.mock import patch

from ops.model import ActiveStatus, BlockedStatus
from ops.testing import Harness
from pyfakefs.fake_filesystem_unittest import TestCase

from charm import NodeExporterCharm
from constants import NODE_EXPORTER_PORT


class TestCharm(TestCase):
    def setUp(self):
        self.harness = Harness(NodeExporterCharm)
        self.addCleanup(self.harness.cleanup)
        self.setUpPyfakefs()
        self.harness.begin()

    @patch("node_exporter_ops.install")
    @patch("node_exporter_ops.version", return_value="v1.0.0")
    def test_install_hook_success(self, patched_version, patched_install):
        """Test that the version is set correctly and the port opened."""
        self.harness.add_relation("juju-info", "juju-info")
        self.harness.update_config({"node-exporter-version": "v1.0.0"})

        # Patch set_workload_version and open_port before emitting install
        with (
            patch.object(self.harness.charm.unit, "set_workload_version") as mock_set_version,
            patch.object(self.harness.charm.unit, "open_port") as mock_open_port,
        ):
            self.harness.charm.on.install.emit()
            mock_set_version.assert_called_with("v1.0.0")
            mock_open_port.assert_called_with("tcp", NODE_EXPORTER_PORT)

        self.assertEqual(self.harness.charm.unit.status, ActiveStatus("node-exporter installed"))

    @patch("node_exporter_ops.install")
    @patch("node_exporter_ops.version", return_value="")
    @patch("ops.framework.EventBase.defer")
    def test_install_hook_fail_no_version_config(self, defer, *_):
        """Test that the install hook defers if node-exporter-version charm config is empty."""
        self.harness.add_relation("juju-info", "juju-info")
        self.harness.update_config({"node-exporter-version": ""})

        self.harness.charm.on.install.emit()

        defer.assert_called()
        self.assertEqual(
            self.harness.charm.unit.status,
            BlockedStatus("Need node-exporter-version config to continue."),
        )

    @patch("charm.NodeExporterCharm._on_install")
    @patch("node_exporter_ops.start")
    def test_start_hook(self, patched_start, *_):
        """Test that the version is set correctly and the port opened."""
        self.harness.add_relation("juju-info", "juju-info")

        self.harness.charm.on.start.emit()

        patched_start.assert_called()
        self.assertEqual(self.harness.charm.unit.status, ActiveStatus())
