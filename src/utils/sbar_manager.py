"""
SBARManager and ContextManager for Chaotic Input

- Maintains a live SBAR object with confidence/conflict tracking
- Prunes, filters, and summarizes input before sending to the LLM
- Handles token budgeting and context window management
- Includes a test harness to simulate chaotic, noisy input
"""
from typing import Optional, Dict, Any, List, Tuple
import time

from collections import deque, Counter

class SBARManager:
    def __init__(self, max_tokens_per_field: int = 12):
        self.fields = ["situation", "background", "assessment", "recommendation"]
        self.sbar = {field: {"value": None, "confidence": 0.0, "conflict": False} for field in self.fields}
        # history: (field, value, confidence, t, source, value_norm, conflict)
        self.history: List[Tuple[str, str, float, float, str, str, bool]] = []
        self._recent = {f: deque(maxlen=6) for f in self.fields}  # (t, value_norm, conf, source)
        self.half_life_sec = 120
        self.max_tokens_per_field = max_tokens_per_field
        self.conflict_threshold = 0.2
        self.synonyms = {
            "spo2": "sats",
            "oxygen": "sats",
            "o2": "sats",
            "bp": "blood pressure",
        }

    def _norm(self, field, value):
        v = (value or "").strip().lower()
        for k, rep in self.synonyms.items():
            v = v.replace(k, rep)
        v = v.replace("%", "").replace("/", " ").replace(",", " ")
        return v

    def _decay(self, conf, t_then):
        dt = max(0.0, time.time() - t_then)
        return conf * (0.5 ** (dt / self.half_life_sec))

    def update_field(self, field: str, value: str, confidence: float = 0.8, source: str = "asr"):
        if field not in self.sbar:
            return
        t = time.time()
        value_norm = self._norm(field, value)
        prev = self.sbar[field]["value"]
        prev_norm = self._norm(field, prev) if prev else None
        conflict = bool(prev_norm and prev_norm != value_norm)
        tokens = value.split()
        if len(tokens) > self.max_tokens_per_field:
            value = " ".join(tokens[:self.max_tokens_per_field]) + " ..."
        if conflict:
            confidence = min(confidence, 0.5)
        self.sbar[field].update({"value": value, "confidence": confidence, "conflict": conflict})
        self.history.append((field, value, confidence, t, source, value_norm, conflict))
        self._recent[field].append((t, value_norm, confidence, source))

    def best_current(self, field: str):
        items = list(self._recent[field])
        if not items:
            return None, 0.0, False
        votes = {}
        for t, v, c, source in items:
            w = self._decay(c, t)
            votes[v] = votes.get(v, 0.0) + w
        if not votes:
            return None, 0.0, True
        top = sorted(votes.items(), key=lambda x: x[1], reverse=True)
        (v1, s1) = top[0]
        s2 = top[1][1] if len(top) > 1 else 0.0
        contested = (s1 - s2) < self.conflict_threshold
        return v1, s1, contested

    def consensus_sbar(self):
        out = {}
        for f in self.fields:
            v, score, contested = self.best_current(f)
            out[f] = {"consensus": v, "score": round(score, 3), "contested": contested}
        return out

    def needs_clarification(self, field: str) -> bool:
        v, score, contested = self.best_current(field)
        return (v is None) or contested or score < 0.5

    def clarification_prompts(self):
        prompts = []
        for f in self.fields:
            v, score, contested = self.best_current(f)
            if (v is None) or contested or score < 0.5:
                if f == "situation":
                    prompts.append("Current oxygen saturation (number + %)?")
                elif f == "background":
                    prompts.append("Current blood pressure (systolic/diastolic)?")
                elif f == "assessment":
                    prompts.append("Patient appearance (cyanotic/pink/alert)?")
                elif f == "recommendation":
                    prompts.append("Action to take now (e.g., epi dose/CPR)?")
        return prompts

    def serialize_for_llm(self) -> str:
        lines = []
        for f in self.fields:
            v, score, contested = self.best_current(f)
            if v and not contested and score >= 0.5:
                t = None
                for t0, v0, _, _ in reversed(self._recent[f]):
                    if v0 == v:
                        t = t0
                        break
                t_str = time.strftime("%H:%M:%S", time.localtime(t)) if t else ""
                lines.append(f"{f[:1].upper()}={v}@{t_str}")
        return " ".join(lines)

    def export_history_jsonl(self, path):
        import json
        with open(path, "w") as f:
            for h in self.history:
                field, value, conf, t, source, value_norm, conflict = h
                f.write(json.dumps({
                    "t": t,
                    "field": field,
                    "value": value,
                    "value_norm": value_norm,
                    "confidence": conf,
                    "conflict": conflict,
                    "source": source
                }) + "\n")

class ContextManager:
    def __init__(self, sbar_manager: SBARManager, max_total_tokens: int = 256):
        self.sbar_manager = sbar_manager
        self.max_total_tokens = max_total_tokens
        self.recent_inputs: List[str] = []

    def add_input(self, text: str):
        # Only keep the most recent, relevant inputs
        self.recent_inputs.append(text)
        # Prune if over token budget
        while self.token_count() > self.max_total_tokens:
            self.recent_inputs.pop(0)

    def token_count(self) -> int:
        return sum(len(t.split()) for t in self.recent_inputs) + sum(len((self.sbar_manager.sbar[f]["value"] or "").split()) for f in self.sbar_manager.fields)

    def get_context_for_llm(self) -> str:
        # Combine recent inputs and SBAR summary
        return "\n".join(self.recent_inputs[-3:]) + "\n" + self.sbar_manager.serialize_for_llm()

# --- Test Harness ---
import random


def simulate_chaotic_input():
    mgr = SBARManager()
    ctx = ContextManager(mgr)
    import time as _t
    # Rapid flip-flop vitals
    mgr.update_field("situation", "O2 sats 72%", 0.8, source="asr")
    _t.sleep(1)
    mgr.update_field("situation", "oxygen 95%", 0.8, source="asr")
    _t.sleep(1)
    mgr.update_field("situation", "SpO2 72%", 0.8, source="asr")
    # Synonym test
    mgr.update_field("situation", "sats 92%", 0.8, source="asr")
    mgr.update_field("situation", "SpO2 92%", 0.8, source="asr")
    # Conflicting commands
    mgr.update_field("recommendation", "start compressions", 0.8, source="asr")
    _t.sleep(1)
    mgr.update_field("recommendation", "pulse is back", 0.8, source="asr")
    # Long monologue
    long_bg = "Patient is a 65 year old male with a history of hypertension, diabetes, and recent surgery, presenting with low blood pressure and tachycardia. BP 80/40."
    mgr.update_field("background", long_bg, 0.9, source="asr")
    mgr.update_field("background", "BP 120/80", 0.8, source="asr")
    mgr.update_field("assessment", "cyanotic", 0.7, source="asr")
    mgr.update_field("assessment", "pink", 0.8, source="asr")
    # Add to context
    ctx.add_input("O2 sats 72%")
    ctx.add_input("oxygen 95%")
    ctx.add_input("SpO2 72%")
    ctx.add_input("sats 92%")
    ctx.add_input("SpO2 92%")
    ctx.add_input("start compressions")
    ctx.add_input("pulse is back")
    ctx.add_input(long_bg)
    ctx.add_input("BP 120/80")
    ctx.add_input("cyanotic")
    ctx.add_input("pink")
    # Print outputs
    print("SBAR for LLM:", mgr.serialize_for_llm())
    print("Clarification prompts:", mgr.clarification_prompts())
    print("Consensus snapshot:", mgr.consensus_sbar())
    mgr.export_history_jsonl("sbar_history.jsonl")

if __name__ == "__main__":
    simulate_chaotic_input()
