# Tension Pneumothorax OR Crisis Scene

This scenario simulates a laparoscopic case that evolves into a tension pneumothorax. Use the assets in this folder to replay the timeline into the SBAR builder or LLM orchestrator for end-to-end validation.

## Files
- `scene_metadata.yaml` – high level description, duration, phases, and participants.
- `dialogue.jsonl` – utterance-level timeline ordered by `t_start` in seconds.

Optional future additions:
- `audio_mix.wav` – synthetic operating room mix if you need to exercise ASR.
- `sbar_log.jsonl` – incremental SBAR snapshots captured during playback.

## Phases
1. **Onset (0–90 s)** – Subtle ventilator and oxygenation changes.
2. **Decompensation (90–210 s)** – Rapid decline with alarms and hemodynamic compromise.
3. **Diagnosis (210–240 s)** – Tension pneumothorax confirmed, decompression prepared.
4. **Treatment (240–274 s)** – Needle decompression and stabilization.

## Usage
Feed `dialogue.jsonl` through the scene player utility (see `src/utils/scene_player.py`) or your orchestrator to stream events in real time. Each line is valid JSON with:

```json
{
  "t_start": 142.3,
  "t_end": 145.7,
  "text": "Pressure’s up to forty-five, sats dropping—seventy-two percent",
  "context_tag": "vitals",
  "noise_level": 0.2
}
```

`context_tag` and `noise_level` are optional; add them as your upstream generator supports richer metadata.
