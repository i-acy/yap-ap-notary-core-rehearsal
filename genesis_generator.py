import json
import hashlib
import jcs
import unicodedata
import sys
import ssl
import platform

def normalize_strings(obj):
    if isinstance(obj, str):
        return unicodedata.normalize("NFC", obj)
    if isinstance(obj, dict):
        return {normalize_strings(k): normalize_strings(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize_strings(i) for i in obj]
    return obj

def check_no_floats(d):
    items = d.values() if isinstance(d, dict) else d
    for v in items:
        if isinstance(v, (float, complex)):
            raise TypeError(f"DETERMINISM_ERROR: Float found: {v}")
        if isinstance(v, (dict, list)):
            check_no_floats(v)

def generate():
    # 1. Shadow Genesis Payload
    payload = {
        "protocol": {
            "version": "1.1",
            "chain_id": "YAPIAP-NOTARY-SHADOW-TR-001",
            "jcs_spec": "RFC8785"
        },
        "governance": {
            "matrix_v": "4.2.0-STABLE",
            "threshold_basis_points": 8500
        },
        "cryptography": {
            "suite": "SUITE_B_P256",
            "hash_algo": "SHA256"
        }
    }

    # 2. Hardening & Normalization
    check_no_floats(payload)
    normalized_payload = normalize_strings(payload)
    
    # 3. RFC 8785 Canonicalization
    canonical_bytes = jcs.canonicalize(normalized_payload)
    
    # 4. Final Hashing
    genesis_hash = hashlib.sha256(canonical_bytes).hexdigest()

    # 5. Forensic DNA Capture
    dna = {
        "genesis_payload_hash": genesis_hash,
        "env": {
            "python_vv": sys.version,
            "openssl": ssl.OPENSSL_VERSION,
            "platform": platform.platform()
        }
    }

    # WINDOWS FIX: Dizin yolu kaldırıldı, doğrudan aynı klasöre yazar.
    with open("shadow_genesis_report.json", "w") as f:
        json.dump(dna, f, indent=4)
    
    print(f"\n[SUCCESS] Shadow Genesis Hash:\n{genesis_hash}\n")

if __name__ == "__main__":
    generate()