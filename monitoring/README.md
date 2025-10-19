# GPU Monitoring Stack

This folder contains a self-contained Prometheus + Grafana + NVIDIA DCGM exporter stack for monitoring local GPU utilisation, temperatures, and memory pressure.

## Prerequisites

- Docker Engine with Compose plugin (or Docker Desktop).
- NVIDIA drivers plus the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).
- Ability to run Linux containers (Linux host or Windows with WSL2).
- An NVIDIA developer account (free) to pull images from nvcr.io: run `docker login nvcr.io` once before starting the stack.

Verify that Docker can see the GPU:

```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```

## Quick start

```bash
cd monitoring
# Start Prometheus, Grafana, and the GPU exporter
DOCKER_DEFAULT_PLATFORM=linux/amd64 docker compose -f docker-compose.gpu-monitor.yml up -d

# Check service status
DOCKER_DEFAULT_PLATFORM=linux/amd64 docker compose -f docker-compose.gpu-monitor.yml ps
```

Services exposed locally:

| Service     | URL                   | Notes                                 |
|-------------|-----------------------|---------------------------------------|
| Prometheus  | http://localhost:9090 | Scrapes metrics every 15 seconds      |
| Grafana     | http://localhost:3000 | Login `admin` / `admin` (change ASAP) |
| GPU Exporter| http://localhost:9400 | Raw DCGM metrics                      |

Grafana autoloads the `GPU Monitoring / GPU Overview` dashboard shipped in this repo. You can import NVIDIA's official dashboards later if you prefer.

## Alerting and extensions

- Add alert rules to `monitoring/prometheus.yml` (for example, GPU temp or utilisation thresholds) and restart the stack.
- To integrate with an existing Prometheus instance, add `gpu-exporter:9400` to its `scrape_configs` or federate metrics from this stack.
- Panels show one series per GPU (labels such as `GPU-0`, `GPU-1`).

## Shutdown / cleanup

```bash
DOCKER_DEFAULT_PLATFORM=linux/amd64 docker compose -f docker-compose.gpu-monitor.yml down
# Remove volumes if you want a clean reset
DOCKER_DEFAULT_PLATFORM=linux/amd64 docker compose -f docker-compose.gpu-monitor.yml down --volumes
```

Prometheus data lives in the `prom-data` volume; Grafana dashboards/settings reside in `grafana-data`.
