import re
import json
try:
    import json5
except ImportError:
    json5 = None

def extract_json(text: str):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in response")
    return match.group(0)

def pre_sanitize(text: str):
    return (
        text.replace("\n", "")
            .replace("\r", "")
            .replace("’", "'")
            .replace("“", '"')
            .replace("”", '"')
    )

def safe_json_loads(text: str):
    raw = extract_json(text)
    clean = pre_sanitize(raw)
    # First pass: strict
    try:
        return json.loads(clean)
    except Exception as e_strict:
        # Fallback: tolerant json5 if available
        if json5:
            try:
                return json5.loads(clean)
            except Exception as e_json5:
                print(f"[WARN] json5 tolerant parse failed: {e_json5}")
        print(f"[ERROR] Strict JSON parse failed: {e_strict}")
        print(f"Raw response was:\n{text}")
        return None

# --- LM Studio System Prompt Best Practice ---
LM_STUDIO_PROMPT = '''
You are a strict JSON generator for a clinical simulation system.

Rules:
1. Output ONLY a valid JSON object.
2. It must be a single line (minified, no indentation or markdown).
3. No explanations, comments, or text before or after the JSON.
4. Do NOT include trailing commas, unquoted keys, or line breaks.
5. If uncertain, output an empty JSON object {} — never text.

Schema Example:
{"case_id": "string", "timeline": [{"t":"00:00","speaker":"string","event":"string"}],
 "sbar_goals": {"situation":"string","background":"string","assessment":"string","recommendation":"string"}}

The program will CRASH if you output anything but strict JSON.
'''
# Recommended LM Studio settings:
# Temperature: 0.1–0.2
# Top-p: 0.8–0.9
# Max tokens: just large enough for the schema
