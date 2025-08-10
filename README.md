[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/vgbm4cZ0)


## 🧠 Approach

1. **UI & File Upload**  
   - Used **Streamlit** to allow users to upload `.docx` legal documents.
   - System identifies document type using keyword matching + embeddings.

2. **Process Detection & Checklist Matching**  
   - Used predefined ADGM checklists for different processes (e.g., incorporation, licensing).
   - Automatically detects the process type from uploaded docs.
   - Compares uploaded docs to required list → flags missing documents.

3. **RAG Integration for Legal Accuracy**  
   - Loaded official ADGM reference documents into a **vector database** (Chroma).
   - Used **LangChain** to retrieve relevant legal rules when checking each clause.

4. **Red Flag Detection**  
   - Pattern-based + semantic search for:
     - Wrong jurisdiction mentions
     - Missing clauses
     - Ambiguous wording
     - Missing signatories

5. **Outputs**  
   - Reviewed `.docx` with highlights/comments.
   - Structured **JSON** report summarizing:
     - Process type
     - Docs uploaded/missing
     - Issues found + severity + suggestions.

6. **Example Workflow**
   - User uploads docs → System classifies & checks → Retrieves ADGM rules → Flags issues → Outputs reviewed doc + JSON.

