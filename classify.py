from docx import Document

KEYWORDS = {
    "Articles of Association":  ["articles of association", "articles of association (aoa)"],
    "Memorandum of Association": ["memorandum of association", "memorandum of association (moa)"],
    "Board Resolution":         ["board resolution"],
    "Shareholder Resolution":   ["shareholder resolution"],
    "Incorporation Application Form": ["incorporation application", "application for incorporation"],
    "UBO Declaration Form":     ["ubo declaration", "ultimate beneficial owner"],
    "Register of Members and Directors": ["register of members", "register of directors"],
    "Change of Registered Address Notice": ["change of registered address", "registered address change"],
}

PROCESS_MAP = {
    "incorporation": {
        "keywords": ["incorporation", "articles of association", "ubo declaration"],
        "required": [
            "Articles of Association",
            "Memorandum of Association",
            "Incorporation Application Form",
            "UBO Declaration Form",
            "Register of Members and Directors",
        ],
    },
    # Extend with licensing / HR / compliance etc.
}

def _read_text(path):
    doc = Document(path)
    return " ".join(p.text.lower() for p in doc.paragraphs)

def detect_type(path: str) -> str:
    """
    Return a best-guess document type based on keywords.
    """
    text = _read_text(path)
    for doc_type, kws in KEYWORDS.items():
        for k in kws:
            if k in text:
                return doc_type
    # fallback: look at filename (if available)
    try:
        from os.path import basename
        name = basename(path).lower()
        for doc_type, kws in KEYWORDS.items():
            for k in kws:
                if k.replace(" ", "_") in name or k.split()[0] in name:
                    return doc_type
    except Exception:
        pass
    return "Unknown"

def detect_process(uploaded_types) -> str:
    """
    Infer the legal process from detected doc types.
    Returns a string (e.g., 'incorporation') or 'unknown'.
    Heuristic: if any of the required docs for a process appear in uploaded_types, infer that process.
    """
    uploaded = set(uploaded_types)
    for name, cfg in PROCESS_MAP.items():
        req = set(cfg.get("required", []))
        # if at least two required documents found, assume this process
        found = req.intersection(uploaded)
        if len(found) >= 2:
            return name
    # fallback: check keywords
    for name, cfg in PROCESS_MAP.items():
        kws = cfg.get("keywords", [])
        if any(k in " ".join(uploaded_types).lower() for k in kws):
            return name
    return "unknown"
