import re
from docx import Document

# --- Expanded rule set (can be extended) -----------------
RULES = [
    {
        "issue":  "Jurisdiction clause does not specify ADGM",
        "pattern": "courts of",
        "severity":"High",
        "suggest": "Replace with 'the courts of the Abu Dhabi Global Market (ADGM)'.",
        "cite":    "Companies Regulations 2020 s.6"
    },
    {
        "issue":  "Missing signatory block / no signatures found",
        "pattern": "signed by",
        "severity":"Medium",
        "suggest": "Insert a signatory block with name, position, signature line and date.",
        "cite":    "Companies Regulations 2020 s.47"
    },
    {
        "issue": "UBO declaration missing or not referenced",
        "pattern": "ubo",
        "severity": "High",
        "suggest": "Include a completed UBO declaration form as required for incorporation.",
        "cite": "ADGM Registry guidance on beneficial ownership"
    },
    {
        "issue": "Ambiguous / permissive language (uses 'may' extensively in critical clauses)",
        "pattern": " may ",
        "severity": "Medium",
        "suggest": "Use clearer mandatory language where required (e.g., 'shall' or 'must').",
        "cite": "Companies Regulations 2020 - general drafting standards"
    }
]

SIGNATURE_PATTERNS = [
    r"\bsigned\b",
    r"\bsignature\b",
    r"\bdate:\b",
    r"\bname:\b",
]

def _doc_text_lower(path):
    doc = Document(path)
    return "\n".join(p.text.lower() for p in doc.paragraphs), doc

def scan_document(path):
    """
    Scan a .docx doc and return findings list.
    Each finding is a dict with keys: issue, pattern, severity, suggest, cite
    """
    text, doc = _doc_text_lower(path)
    findings = []

    # Quick ADGM presence check: if doc references other jurisdictions, flag
    if ("federal courts" in text or "u.a.e. federal" in text) and ("adgm" not in text):
        findings.append({
            "issue": "Document references UAE Federal Courts rather than ADGM jurisdiction",
            "pattern": "federal courts",
            "severity": "High",
            "suggest": "Replace jurisdiction references with ADGM courts / exclusive ADGM jurisdiction language.",
            "cite": "ADGM Companies Regulations 2020 s.6"
        })

    for rule in RULES:
        # we will only flag rule if pattern present; for some rules (like 'may') add thresholds
        pat = rule["pattern"]
        if pat.strip():
            if pat in text:
                # For 'may' we try to ensure it's used in critical clauses; simple heuristic:
                if pat.strip() == " may ":
                    # count occurrences
                    cnt = text.count(" may ")
                    if cnt >= 3:
                        findings.append({**rule, "pattern": pat})
                else:
                    # only append if ADGM not referenced (so suggestions reference ADGM)
                    # but we will include cite regardless
                    findings.append({**rule, "pattern": pat})
    # Check for signature presence - if none, add missing signatory warning
    if not any(re.search(pat, text) for pat in SIGNATURE_PATTERNS):
        findings.append({
            "issue": "Missing signatory block or signature lines",
            "pattern": "signatory",
            "severity": "Medium",
            "suggest": "Add a signatory section with name, designation, signature and date.",
            "cite": "Companies Regulations 2020 s.47"
        })

    # Remove duplicates (by issue)
    unique = []
    seen = set()
    for f in findings:
        key = (f["issue"], f.get("pattern", ""))
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique
