# GyanSetu Architecture Flowchart

This diagram shows the two parallel ingestion pipelines (static and dynamic) converging into a single ChromaDB collection, then flowing through retrieval and answer generation — which now serves both source types equally.

```mermaid
flowchart TD
    %% ── Style classes ─────────────────────────────────────────────
    classDef static     fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
    classDef dynamic    fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    classDef shared     fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef metadata   fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,stroke-dasharray:4 3,color:#000
    classDef error      fill:#ffebee,stroke:#c62828,stroke-width:1px,color:#000
    classDef decision   fill:#fff8e1,stroke:#f57f17,stroke-width:1px,color:#000

    %% ═══════════════════════════════════════════════════════════════
    %% PATH A — STATIC PIPELINE (unchanged)
    %% ═══════════════════════════════════════════════════════════════
    subgraph PathA["PATH A — Static Pipeline (unchanged)"]
        A_SRC["14 Wikipedia URLs"]:::static
        A_LOADER["ingestion/loader.py<br/><b>load_webpage()</b><br/>requests + BeautifulSoup"]:::static
        A_ORCH["ingestion/ingest_pipeline.py<br/><b>ingest_urls()</b><br/>(runs once at cold-start)"]:::static

        A_SRC --> A_LOADER --> A_ORCH
    end

    %% ═══════════════════════════════════════════════════════════════
    %% PATH B — DYNAMIC PIPELINE (new)
    %% ═══════════════════════════════════════════════════════════════
    subgraph PathB["PATH B — Dynamic Pipeline (new)"]
        B_SRC["User pastes any URL in<br/>Streamlit sidebar"]:::dynamic
        B_FRONT["frontend/app.py<br/>sidebar text input + button<br/>→ requests.post()"]:::dynamic
        B_API["api/main.py<br/><b>POST /ingest-url</b>"]:::dynamic

        B_DUPE{"Duplicate?<br/>collection.get(where={'source': url})"}:::decision
        B_DONE["Return: already in KB"]:::dynamic

        B_SCRAPE["ingestion/loader.py<br/><b>load_webpage_dynamic()</b><br/>trafilatura.extract()"]:::dynamic
        B_FALLBACK["Fallback:<br/>load_webpage()<br/>(BeautifulSoup)"]:::dynamic
        B_LEN{"Text ≥ 200 chars?"}:::decision
        B_ERR["400 error: too short"]:::error

        B_SRC --> B_FRONT --> B_API --> B_DUPE
        B_DUPE -- "exists" --> B_DONE
        B_DUPE -- "new URL" --> B_SCRAPE
        B_SCRAPE -- "None / error" --> B_FALLBACK
        B_SCRAPE -- "success" --> B_LEN
        B_FALLBACK --> B_LEN
        B_LEN -- "no" --> B_ERR
        B_LEN -- "yes" --> B_CHUNKER
    end

    %% ═══════════════════════════════════════════════════════════════
    %% CONVERGED PATH — same functions, same collection
    %% ═══════════════════════════════════════════════════════════════
    subgraph Converged["Converged Ingestion (shared)"]
        CHUNKER["ingestion/chunker.py<br/><b>chunk_document()</b><br/>500 chars, 50 overlap"]:::shared
        EMBEDDER["ingestion/embedder.py<br/><b>embed_chunks()</b><br/>all-MiniLM-L6-v2 → 384d"]:::shared
        STORE["vectorstore/store.py<br/><b>add_chunks(source_type)</b><br/>MD5(id) → upsert"]:::shared
        DB[("💾 ChromaDB<br/>collection: <b>gyanshetu_docs</b><br/>cosine similarity")]:::shared

        META["Metadata per chunk:<br/>
        • source / source_url<br/>
        • type (webpage / pdf)<br/>
        • chunk_index<br/>
        • <b>source_type</b> ← 'static' | 'dynamic'<br/>
        • <b>ingested_at</b> ← ISO timestamp"]:::metadata
    end

    A_ORCH --> CHUNKER
    CHUNKER --> EMBEDDER --> STORE --> DB
    META -.-> STORE

    %% ═══════════════════════════════════════════════════════════════
    %% QUERY PATH — retrieval + generation (serves both source types)
    %% ═══════════════════════════════════════════════════════════════
    subgraph QueryPath["Query Path (shared — both static and dynamic content searchable together)"]
        Q_USER["User question in English or Bangla"]:::shared
        Q_LANG["retrieval/language_detector.py<br/><b>is_bangla()</b>"]:::shared

        Q_TRANS1["llm/generator.py<br/><b>translate_to_english()</b><br/>Attempt 1: simple prompt"]:::shared
        Q_V1{"contains Bangla?<br/>Unicode U+0980–U+09FF"}:::decision
        Q_TRANS2["Attempt 2: few-shot retry<br/>(+ worked example)"]:::shared
        Q_V2{"Still Bangla?"}:::decision
        Q_FAIL[("Return honest error message<br/>(no silent garbage into embedder)")]:::error

        Q_RET["retrieval/retriever.py<br/><b>retrieve()</b><br/>candidate_pool = top_k × 5<br/>sim floor = 0.15 → top_k"]:::shared
        Q_CTX["format_context()<br/>→ [Source N] labeled"]:::shared
        Q_PROMPT["llm/prompt_template.py<br/><b>build_prompt()</b><br/>topic-neutral: reads all sources"]:::shared
        Q_GROQ["Groq API<br/>Llama 3.1 8B instant<br/>temperature=0.2"]:::shared
        Q_ANS["Answer with cited sources"]:::shared
    end

    Q_USER --> Q_LANG
    Q_LANG -- "English" --> Q_RET
    Q_LANG -- "Bangla" --> Q_TRANS1 --> Q_V1
    Q_V1 -- "clean English" --> Q_RET
    Q_V1 -- "has Bangla" --> Q_TRANS2 --> Q_V2
    Q_V2 -- "clean English" --> Q_RET
    Q_V2 -- "still Bangla" --> Q_FAIL

    DB -.-> Q_RET
    Q_RET --> Q_CTX --> Q_PROMPT --> Q_GROQ --> Q_ANS
```

## Legend

| Colour | Meaning |
|---|---|
| 🔵 Blue (`static`) | **Path A** — Static pipeline (unchanged, cold-start only) |
| 🟠 Orange (`dynamic`) | **Path B** — Dynamic URL ingestion (this feature) |
| 🟣 Purple (`shared`) | Shared code — identical for both source types |
| 🟢 Green (dashed) | New metadata fields added for provenance tracking |
| 🔴 Red (`error`) | Error / failure exit |
| 🟡 Yellow (`decision`) | Conditional validation gate |
