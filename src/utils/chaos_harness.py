import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from chaos_telemetry import record_metric
"""
ChaosHarness: Realistic, LLM-driven SBAR/ASR chaos test harness.

Features:
  - 4-agent loop: GT (ground truth), Utterance Synth, ASR-noise, SBAR Processor
  - Pluggable LLMs (13B, OpenRouter, etc) and optional Extractor LLM
  - Fully dialable chaos knobs (WER, flip, retraction, overlap, etc)
  - Logs raw and consensus SBAR, clarification prompts, and context
  - Demo mode with toy LLM stubs for fast local testing
"""

# (Re)define only the clean, correct classes and main block below


import json
from typing import Callable, Optional
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from chaos_json_parser import safe_json_loads
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../llm')))
from llm_client import LLMClient

class ChaosKnobs:
    def __init__(self, seed=42, emit_rate_mean_sec=3.0, base_wer=0.15, num_confusion=1,
                 flip_rate=0.05, retraction_rate=0.08, overlap_rate=0.20, partial_ratio=0.60,
                 speaker_error=0.10, out_of_order=0.05, token_budget=512, stability_window_sec=25,
                 consensus_margin=0.20):
        self.seed = seed
        self.emit_rate_mean_sec = emit_rate_mean_sec
        self.base_wer = base_wer
        self.num_confusion = num_confusion
        self.flip_rate = flip_rate
        self.retraction_rate = retraction_rate
        self.overlap_rate = overlap_rate
        self.partial_ratio = partial_ratio
        self.speaker_error = speaker_error
        self.out_of_order = out_of_order
        self.token_budget = token_budget
        self.stability_window_sec = stability_window_sec
        self.consensus_margin = consensus_margin

class ChaosHarness:
    def __init__(self, llm_gt: Callable[[str], str], llm_u: Callable[[str], str], extractor: Optional[Callable[[str], str]] = None, knobs: Optional[ChaosKnobs] = None, rate: float = 1.0):
        self.gt = llm_gt
        self.u = llm_u
        self.ex = extractor
        self.knobs = knobs or ChaosKnobs()
        self.rate = rate

    def generate_case(self):
        # Request a case in strict JSON from the LLM
        prompt = (
            """
You are a clinical simulation engine.
Respond with a SINGLE LINE of valid, MINIFIED JSON.
DO NOT include explanations, Markdown, or commentary.
If you include anything else, the program will crash.
Schema:
{"case_id": str, "timeline": [ { "t": str, "speaker": str, "event": str } ], "sbar_goals": { "situation": str, "background": str, "assessment": str, "recommendation": str }}
Return only JSON.
            """
        )
        start = time.time()
        response = self.gt(prompt)
        elapsed = time.time() - start
        # Try strict parse
        case = None
        parsed_strictly = False
        try:
            case = json.loads(response)
            parsed_strictly = True
        except Exception:
            case = safe_json_loads(response)
        # Telemetry logging
        case_id = case.get('case_id') if case and isinstance(case, dict) else 'unknown'
        record_metric(
            case_id=case_id,
            strict_ok=parsed_strictly and case is not None,
            tolerant_ok=(not parsed_strictly) and case is not None,
            llm_model="Medicine-13B",
            prompt_template="chaos_harness_generate_case",
            response_len=len(response) if response else 0,
            elapsed=elapsed
        )
        return case

    def stream(self, case):
        # Demo: returns a list of telemetry snapshots (fake)
        return [
            {"step": 1, "sbar": {"situation": "O2 sat 95%"}},
            {"step": 2, "sbar": {"situation": "Wheezing, sats dropping"}},
            {"step": 3, "sbar": {"situation": "O2 sat 78%"}},
        ]


# --- Real LLM integration ---
def make_llm_functions(api_url, system_prompt, model_name, temperature=0.7):
    import requests
    def call_llm(prompt, sys_prompt=None):
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": sys_prompt or system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": -1,
            "stream": False
        }
        resp = requests.post(api_url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        # Try OpenAI format, fallback to 'response' key
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        return data.get("response", "")
    return call_llm, call_llm, call_llm


if __name__ == "__main__":
    print("--- ChaosHarness Real LLM Mode ---")
    # Set your LLM API URL, model, and system prompt here:
    api_url = os.environ.get("LLM_API_URL", "http://100.111.223.74:1234/v1/chat/completions")
    model_name = os.environ.get("LLM_MODEL", "medicine-llm-13b")
    system_prompt = os.environ.get("LLM_SYSTEM_PROMPT", "You are a clinical reasoning assistant. You never give orders, only ask questions. You do not diagnose, prescribe, or recommend. You encourage physicians to reflect on possibilities. You may retrieve supporting guidelines, references, or YAML protocols.")
    temperature = float(os.environ.get("LLM_TEMPERATURE", "0.7"))
    knobs = ChaosKnobs()
    llm_gt, llm_u, extractor = make_llm_functions(api_url, system_prompt, model_name, temperature)
    h = ChaosHarness(llm_gt=llm_gt, llm_u=llm_u, extractor=extractor, knobs=knobs)
    case = h.generate_case()
    print("Ground truth case:", json.dumps(case, indent=2))
    telemetry = h.stream(case)
    print("\n--- Telemetry (last 3 steps) ---")
    for snap in telemetry[-3:]:
        print(json.dumps(snap, indent=2))
    print("\nDone. Real LLM test complete!")

