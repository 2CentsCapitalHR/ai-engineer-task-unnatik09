import os
import tempfile
import json
import streamlit as st

from classify import detect_type, detect_process, PROCESS_MAP
from checker import scan_document
from annotate import mark_file
from qa import rag_ask

st.set_page_config(page_title="ADGM Corporate Agent", page_icon="📑")
st.title("ADGM Corporate Agent")

uploaded = st.file_uploader(
    "Upload one or more .docx files", type=["docx"], accept_multiple_files=True
)

if uploaded:
    with st.spinner("Analysing…"):
        tmp_dir = tempfile.mkdtemp()
        summary = {
            "process": "unknown",
            "documents_uploaded": len(uploaded),
            "required_documents": 0,
            "missing_document": None,
            "uploaded_types": [],
            "issues_found": [],
        }

        reviewed_files = []

        for uf in uploaded:
            # Save to disk
            file_path = os.path.join(tmp_dir, uf.name)
            with open(file_path, "wb") as out:
                out.write(uf.getbuffer())

            doc_type = detect_type(file_path)
            summary["uploaded_types"].append(doc_type)

            findings = scan_document(file_path)
            if findings:
                marked = os.path.join(tmp_dir, f"reviewed_{uf.name}")
                try:
                    mark_file(file_path, marked, findings)
                    reviewed_files.append({"original": uf.name, "reviewed_path": marked})
                except Exception:
                    # If marking fails, still provide the original file as fallback
                    reviewed_files.append({"original": uf.name, "reviewed_path": file_path})

            # normalize findings for JSON
            summary["issues_found"].extend([
                {
                    "document": doc_type,
                    "issue": f["issue"],
                    "severity": f.get("severity", "Medium"),
                    "suggestion": f.get("suggest"),
                    "pattern": f.get("pattern"),
                    "cite": f.get("cite"),
                } for f in findings
            ])

        # ---------- Checklist Verification ----------
        summary["process"] = detect_process(summary["uploaded_types"])
        required_list = PROCESS_MAP.get(summary["process"], {}).get("required", [])
        summary["required_documents"] = len(required_list)
        missing = [d for d in required_list if d not in summary["uploaded_types"]]
        summary["missing_document"] = missing[0] if missing else None
        summary["missing_documents"] = missing

        # ---------- Natural-language explanation ----------
        user_friendly = (
            f"It appears you're attempting **{summary['process'].title()}** in ADGM. "
            f"You provided {summary['documents_uploaded']} of "
            f"{summary['required_documents']} required docs. "
            + (f"The missing document appears to be: "
               f"'{summary['missing_document']}'.\n\n" if missing else "")
            + "Key issues:\n"
            + ("\n".join(f"- {i['document']}: {i['issue']}" for i in summary["issues_found"])
               if summary["issues_found"] else "None found.")
        )

        # RAG explanation (best-effort)
        legal_basis = rag_ask(
            "Explain why each flagged issue matters under ADGM law and propose compliant wording."
        )
        final_msg = user_friendly + "\n\n" + legal_basis

        st.subheader("Results")
        st.markdown(final_msg)

        st.subheader("Structured JSON")
        st.json(summary)

        # Provide reviewed files for download
        if reviewed_files:
            st.subheader("Reviewed documents")
            for r in reviewed_files:
                try:
                    with open(r["reviewed_path"], "rb") as fh:
                        st.download_button(
                            label=f"Download reviewed: {r['original']}",
                            data=fh.read(),
                            file_name=os.path.basename(r["reviewed_path"]),
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        )
                except Exception:
                    st.text(f"Could not load reviewed file for {r['original']}")

        # Provide the structured JSON as a downloadable file
        json_path = os.path.join(tmp_dir, "analysis_summary.json")
        with open(json_path, "w") as jf:
            json.dump(summary, jf, indent=2)
        with open(json_path, "rb") as jf:
            st.download_button(
                label="Download analysis JSON",
                data=jf.read(),
                file_name="analysis_summary.json",
                mime="application/json",
            )
 