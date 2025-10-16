
# Architecture Overview (2025-10-17)

## System Architecture (Current)

```
                           ┌──────────────────────────┐
                           │  Admin Dashboard (Web)   │
                           │  /dashboard.html + WS    │
                           └────────────┬─────────────┘
                                        │ wss:// + token
                 ┌──────────────────────┼──────────────────────┐
                 │                      │                      │
        ┌────────▼───────┐      ┌───────▼────────┐      ┌──────▼────────┐
        │ Android Client │      │ Windows Client │      │ Future Clients │
        │ (SOS button,   │      │ (Kivy UI)      │      │  (CLI/Browser) │
        │  WebRTC/HTTP)  │      │                │      │                │
        └────────┬───────┘      └────────┬───────┘      └──────┬────────┘
                 │ HTTPS + JWT / token    │ HTTPS + JWT / token │
                 └────────────┬───────────┴────────────┬────────┘
                              │                        │
                    ┌─────────▼────────────────────────▼─────────┐
                    │      SOS Orchestrator (FastAPI)             │
                    │  - mTLS / token auth / JWT roles            │
                    │  - SBAR + LLM routing + ASR/TTS proxy       │
                    │  - OTA update manifest + pairing tokens     │
                    │  - Audit log + PHI de-identification        │
                    │  - OpenTelemetry metrics (/metrics)         │
                    └─────────┬───────────┬───────────┬──────────┘
                              │           │           │
      ┌───────────────────────┤           │           ├───────────────────────┐
      │                       │           │           │                       │
┌─────▼─────┐        ┌───────▼──────┐  ┌──▼──────────┐  ┌───────────▼─────────┐
│  Postgres │        │    Redis     │  │   Object    │  │  External LLM/ASR/TTS│
│ (metrics, │        │ (sessions,   │  │   Storage   │  │ (OpenRouter, LM      │
│  audit)   │        │  pairing)    │  │  (S3/GCS)   │  │  Studio, FasterWhisper│
└───────────┘        └──────────────┘  └────────────┘  └──────────────────────┘
      ▲                     ▲                ▲                       ▲
      │                     │                │                       │
      │        ┌────────────┴──────────────┐ │   ┌───────────────────┴──────────┐
      │        │ Prometheus + Grafana      │ │   │ Chaos Harness / Validation    │
      │        │ (Traefik exposes /metrics │ │   │ Pipelines (local or cloud)    │
      └────────┴───────────────────────────┴─┴───┴──────────────────────────────┘
```

### Key Changes (Steps 10–14)

- **Secure Edge**: Traefik terminates HTTPS (Let’s Encrypt). FastAPI enforces bearer/JWT tokens; QR pairing issues time-limited clinician tokens.  
- **Discovery & Pairing**: Zeroconf advertises `_sos._tcp.local`, and pairing endpoint returns signed tokens and QR data. Android discovers the cloud or LAN host automatically.  
- **Persistence**: Metrics stream into PostgreSQL, validation WAV/JSONL artifacts push to S3/GCS, Redis caches session/OTAs.  
- **Observability**: OpenTelemetry instruments `/turn` pathways. Prometheus scrapes `/metrics`; Grafana visualizes latency/turn counts, connected clients, storage uploads.  
- **Compliance**: `deid.scrub_record()` removes PHI before persistence, `_validation/audit_log.jsonl` is hash-chained, and every pairing/update/turn records audit events.  
- **Cross-Platform Updates**: OTA manifest served from orchestrator; Windows UI and Android client check SHA-256 signed packages over TLS.  
- **Cloud Deployment**: Docker image runs in Cloud Run or ECS Fargate. Compose file mirrors cloud stack for local parity.

## Data Flow (Voice → Protocol Guidance → Storage)

1. **SOS Trigger**: Android/Windows UI signals orchestrator via HTTPS (token enforced). LAN discovery supplies host info; out-of-band QR tokens unlock cloud access.  
2. **Audio Path**: Client streams voice (WebRTC or HTTP WAV). Orchestrator proxies ASR, de-identifies transcripts, stores summary metrics.  
3. **LLM/Protocol**: Orchestrator retrieves YAML protocols, constructs SBAR context, routes to configured LLM (local LM Studio / Ollama / cloud OpenRouter).  
4. **Response**: Questions/recommendations return to clients; TTS audio stored locally + uploaded to S3 for later review.  
5. **Telemetry & Audit**: `log_turn_metric` writes JSONL + Postgres row (`metrics` table), increments OpenTelemetry counters, appends tamper-evident audit entry. Dashboard streams live metrics over WebSocket + Prometheus.  
6. **Compliance Processing**: All audit + telemetry payloads scrubbed for PHI before persistence. AWS/GCP credentials restrict bucket access; logs mirror to long-term storage.  
7. **Updates & Pairing**: OTA checker polls manifest, verifies SHA-256, and installs signed packages. Admin pairing endpoint issues short-lived tokens and records chain of custody.

## Component Responsibilities (2025-10-17)

- **Client Apps (Android/Windows)**: SOS UI, mic streaming, HTTPS/JWT auth, OTA update polling.  
- **Traefik / Proxy**: TLS termination, cert management, routing to FastAPI.  
- **FastAPI Orchestrator (`src/orchestrator`)**:  
  - Discovery (mDNS), pairing tokens, OTA manifest.  
  - SBAR/LLM orchestration (`/turn`, `/turn_text`).  
  - Dashboard + metrics summary (`/dashboard.html`, `/ws/metrics`, `/metrics/summary`).  
  - Compliance filters + audit logging.  
- **Telemetry**: `log_turn_metric` (JSONL + Postgres + OTel). Prometheus exporter at `/metrics` (port 9464).  
- **Persistence**:  
  - `src/schema/db_models.Metric` + `src/utils/db` for Postgres.  
  - `src/utils/storage` uploads `_validation/` artifacts to S3/GCS.  
  - `_validation/audit_log.jsonl` for tamper-proof audit chain.  
- **Security Modules**:  
  - `src/security/auth` (JWT issue/verify).  
  - `src/security/deid` (PHI scrubbing).  
- **Infrastructure**: Dockerfile, `docker-compose.yml`, `prometheus.yml`, `grafana-provisioning/`, GitHub Actions (optional) to build/push images.  
- **External Services**: ASR/TTS microservices, LM Studio or configurable LLM endpoints.

## Compliance & Observability Pipeline

- **PHI De-identification**: `scrub_record()` sanitizes all metric/audit payloads (SSN, phone, dates, names).  
- **Audit Chain**: Each admin/clinician action hashed and linked; logs stored in `_validation/audit_log.jsonl` and mirrored via S3.  
- **OpenTelemetry**: `turns_counter`, `latency_hist` expose metrics for `/turn`/`/turn_text`. Prometheus scrapes orchestrator; Grafana displays latency, success ratios, connected clients, storage uploads.  
- **Alerting (next step)**: Grafana dashboards ready for threshold/SLI alerts (latency > 5s, storage failure, etc.).  
- **Access Control**: Scoped JWT roles (`admin`, `clinician`) guard dashboard, metrics summary, pairing; bootstrap token remains for emergency admin access until rotated.

---

**Operational Notes**

- Use `docker compose up --build` for local parity (Traefik TLS, Prometheus, Grafana, Postgres, Redis).  
- Cloud deployments mirror compose stack on Cloud Run/ECS. Configure secrets (`TOKEN_SECRET`, `DATABASE_URL`, S3 creds) via environment variables/Secret Manager.  
- Android dashboard access: `https://<domain>/dashboard.html?token=<admin-jwt>`  
- Keep `prometheus.yml`, Grafana provisioning, and OTA manifest under version control and update hashes via `python tools/publish_update.py`.

For detailed swim-lane or sequence diagrams, export from draw.io and store alongside this document.
