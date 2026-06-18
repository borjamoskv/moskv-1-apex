#!/usr/bin/env python3
import re
from typing import Dict, Any
class RealityAuditor:
    @staticmethod
    def audit_osint_payload(output: str) -> Dict[str, Any]:
        has_http = bool(re.search(r'(HTTP/[123](?:\.\d)?\s+[2-5]\d\d|Status:\s*[2-5]\d\d)', output))
        has_hash = bool(re.search(r'[a-fA-F0-9]{32,64}', output))
        has_time = bool(re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', output))
        proofs = []
        if has_http: proofs.append("HTTP_STATUS")
        if has_hash: proofs.append("TX_HASH")
        if has_time: proofs.append("TIMESTAMP")
        score = len(proofs)
        if score == 3: return {"reality": "REAL", "confidence": "HIGH", "proofs": proofs}
        elif score > 0: return {"reality": "DEGRADED", "confidence": "MEDIUM", "proofs": proofs}
        return {"reality": "EMULATED", "confidence": "LOW", "proofs": proofs}
    @staticmethod
    def audit_filesystem_payload(output: str) -> Dict[str, Any]:
        has_sha = bool(re.search(r'(?:SHA256|MD5|Hash):\s*[a-fA-F0-9]{32,64}', output, re.IGNORECASE))
        has_inode = bool(re.search(r'inode:\s*\d+', output, re.IGNORECASE))
        has_path = bool(re.search(r'/\w+(?:/\w+)+', output))
        proofs = []
        if has_sha: proofs.append("FILE_HASH")
        if has_inode: proofs.append("FS_INODE")
        if has_path: proofs.append("ABSOLUTE_PATH")
        score = len(proofs)
        if score >= 2: return {"reality": "REAL", "confidence": "HIGH", "proofs": proofs}
        elif score == 1: return {"reality": "DEGRADED", "confidence": "MEDIUM", "proofs": proofs}
        return {"reality": "EMULATED", "confidence": "LOW", "proofs": proofs}
    @classmethod
    def evaluate(cls, domain: str, output: str) -> Dict[str, Any]:
        domain = domain.upper()
        if domain in ("OSINT", "WEB"): return cls.audit_osint_payload(output)
        elif domain in ("FILESYSTEM", "LOCAL"): return cls.audit_filesystem_payload(output)
        if len(output.strip()) > 0 and not re.search(r'(dummy|mock|test)', output, re.IGNORECASE):
            return {"reality": "DEGRADED", "confidence": "UNKNOWN", "proofs": ["NON_EMPTY"]}
        return {"reality": "EMULATED", "confidence": "ZERO", "proofs": []}
