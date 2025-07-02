# Node Exporter Operator Charm

Prometheus [node exporter](https://github.com/prometheus/node_exporter) for
machine metrics.

## Quickstart

Deploy the `node-exporter` charm and relate it to the units you want
to export the metrics for:

```bash
juju deploy node-exporter
```

## Build/Dev

### Build the Charms
This project uses [`uv`](https://docs.astral.sh/uv/) in combination with [`just`](https://github.com/casey/just)
to drive [`charmcraft`](https://canonical-charmcraft.readthedocs-hosted.com/en/stable/) to build the `node-exporter` [charm](https://juju.is/charms-architecture) in [`lxd`](https://canonical.com/lxd) containers.

Once you have `charmcraft`, `lxd`, `just`, and `uv` installed you are ready to build.

Build the charm using the following command.
```bash
just pack
```

## License

The charm is maintained under the Apache v2 license. See `LICENSE` file in this
directory for full preamble.

Copyright &copy; 2025 Vantage Compute Corporation
