import json
import hashlib
import jcs
import unicodedata
import sys
import platform

# --- PROTOCOL CONSTANTS ---
INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1

def check_strict_determinism(obj):
    if obj is None:
        raise TypeError("DETERMINISM_ERROR: Null values are forbidden.")
    if isinstance(obj, bool):
        return  
    if isinstance(obj, (float, complex)):
        raise TypeError(f"DETERMINISM_ERROR: Forbidden type {type(obj)}")
    if isinstance(obj, int):
        if obj < INT64_MIN or obj > INT64_MAX:
            raise ValueError(f"INT64_RANGE_VIOLATION: {obj}")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if not isinstance(k, str):
                raise TypeError("KEY_ERROR: Keys must be strings.")
            check_strict_determinism(v)
    elif isinstance(obj, list):
        for i in obj:
            check_strict_determinism(i)

def normalize_strings(obj):
    if isinstance(obj, str):
        return unicodedata.normalize("NFC", obj)
    if isinstance(obj, dict):
        return {normalize_strings(k): normalize_strings(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize_strings(i) for i in obj]
    return obj

def run_notary():
    deterministic_core = {
        "parent_genesis_hash": "6cf0559f5b878038b3bd2c52c5afc37de7971c3a357bfc4f89d71499c84d18b8",
        "receipt_id": "REC-2026-001",
        "decision": {
            "action": "INITIATE_WAR_ROOM",
            "level": "ALPHA",
            "participants": ["Gemini", "Node_Owner"]
        }
    }

    check_strict_determinism(deterministic_core)
    normalized_core = normalize_strings(deterministic_core)
    canonical_bytes = jcs.canonicalize(normalized_core)
    
    if canonical_bytes != canonical_bytes.decode("utf-8").encode("utf-8"):
        raise ValueError("INTEGRITY_ERROR: UTF8_ROUNDTRIP_FAILURE")
    
    decision_hash = hashlib.sha256(canonical_bytes).hexdigest()

    envelope = {
        "decision_hash": decision_hash,
        "forensics": {
            "os": platform.system(),
            "python_vv": sys.version,
            "architecture": platform.machine()
        }
    }

    with open("decision_receipt_v1.json", "w") as f:
        json.dump(envelope, f, indent=4)
        
    print(f"\n[AUDIT SUCCESS] Decision Core Hash:\n{decision_hash}\n")

if __name__ == "__main__":
    run_notary()