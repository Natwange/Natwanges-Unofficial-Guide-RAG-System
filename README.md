# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
🌍 ✈️ *International Student Career Survival Guide* 🎓 💼

I chose this domain because international students often struggle to find career advice that addresses their specific experiences. Official resources provide useful information, but it is usually spread across multiple websites and focuses more on policies than real-world guidance. In practice, some of the most helpful advice comes from other international students through Reddit, career webinars, and communities such as CodePath, ColorStack, and Rewriting the Code. This project makes that knowledge easier to search and access by bringing it together in one place.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | How I Survived the Toughest Job Market as an International Student | reddit | https://www.reddit.com/r/internships/comments/1jpcszv/how_i_survived_the_toughest_job_market_as_an/ |
| 2 | Advice for International Students in the US | forum | https://www.wallstreetoasis.com/forum/investment-banking/advice-for-international-students-in-the-us-f-1-visa-opt-cpt-h-1b |
| 3 | I'm an international student at UNC. Here's how I got an AI summer internship. | article | https://www.businessinsider.com/unc-student-landed-internship-after-changing-major-2026-4 |
| 4 | Want to land a tech internship? A Google engineer explains how networking 'intentionally' can help | article | https://www.businessinsider.com/google-engineer-advice-internship-tech-job-offer-2025-6 |
| 5 | No Internship? No Problem | pdf | data/raw/source_05.txt |
| 6 | How to Add Projects to Your Resume (And Actually Get Credit for Them) | article | https://rewritingthecode.org/resources/member-resources/how-to-add-projects-to-your-resume/ |
| 7 | Building Confidence: Empower Yourself as a Woman in Tech | article | https://rewritingthecode.org/resources/member-resources/building-confidence-empower-yourself-as-a-woman-in-tech/ |
| 8 | Google Early Careers Session Notes | txt | data/raw/source_08.txt |
| 9 | Squarespace Acing Technical Recruitment Info Session | txt | data/raw/source_09.txt |
| 10 | How to Ace the First 30 Days of Your New Job | article | https://rewritingthecode.org/resources/member-resources/how-to-ace-the-first-30-days/ |
| 11 | Underclassmen Opportunities | github_repo | https://github.com/Jose-Gael-Cruz-Lopez/underclassmen-opportunities/tree/main?tab=readme-ov-file |
| 12 | Google's AI-Assisted Coding Interview (2026 Guide) | article | https://www.tryexponent.com/blog/google-ai-coding-interview |
| 13 | Using AI in Meta's AI-assisted coding interview (with real prompts and examples) | article | https://interviewing.io/blog/how-to-use-ai-in-meta-s-ai-assisted-coding-interview-with-real-prompts-and-examples |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** Target ~300 words per chunk, hard cap ~380 words (≈490 tokens). The cap is set below the ~400-word equivalent of bge-small-en-v1.5's 512-token limit, and the ~60-word overlap is counted inside the cap, so no chunk is ever silently truncated at embedding time. I split on natural boundaries — paragraph/blank-line breaks for prose, and sentence boundaries where a document has no paragraphs — packing consecutive units until the word budget is reached. Short documents may form a single chunk; long ones are split into several.

**Overlap:** ~60 words (roughly 1–2 sentences) carried from the tail of the previous chunk into the next. I define overlap by word count rather than "one paragraph" because paragraph lengths vary widely across my sources and several sources have no paragraph structure at all.

**Preprocessing before chunking:** My sources are not uniformly clean prose, so I normalize them first. For every document I strip any leftover HTML tags and unescape HTML entities (e.g. "&lt;", "</code>" left over from the code snippets in the AI-interview articles), stripping tags before unescaping so escaped angle brackets inside code survive. Then I clean by type: strip GitHub navigation/file-listing/footer chrome from the scraped repo page (e.g., "Skip to content", "Pull requests", "Insights"); rejoin the clause-per-line info-session transcripts (Google, Squarespace) into running sentences; collapse the slide-deck PDF ("No Internship? No Problem") fragments into coherent text; and normalize whitespace while preserving real paragraph breaks. (The Reddit/forum comment sections were removed manually from the raw files.)

**Why these choices fit your documents:** My corpus mixes genuine prose (Reddit posts, forum threads, career articles, ~600–1,300 words each) with two large transcripts (~6,000+ words), a scraped repo page, and slide-deck text. Each prose document covers several subtopics (networking, internships, sponsorship, resumes, interviews), so chunking by topic-coherent groups keeps related ideas together instead of blending them. Because my two largest sources have no paragraph breaks, a word budget is the primary splitter with paragraph/sentence boundaries as preferred cut points — this works across all document types while keeping every chunk under the embedding model's token limit.

**Final chunk count:** 111 chunks across all 13 documents (min 84 / avg 313 / max 380 words per chunk; 0 chunks over the cap, no empty chunks, no HTML/boilerplate artifacts).

---

## Sample Chunks

<!-- At least 5 labeled sample chunks, each with its source document name. -->

Five representative chunks from `data/processed/chunks.jsonl` (snippets shown; each is a full ~300-word chunk):

**1. `source_06_chunk_001` — source: How to Add Projects to Your Resume (And Actually Get Credit for Them)**
> "...You want the projects you list on your resume, whether they're an app, scripts that automate something, analyses, or dashboards (Tableau, Power BI, Jupyter notebooks), or machine learning models, to have shareable output..."

**2. `source_09_chunk_006` — source: Squarespace Acing Technical Recruitment Info Session**
> "...Everyone talks about LeetCode and how to use it for prepping. But beyond practicing problems, what were your most effective strategies for preparing for technical interviews?..." (continues with advice on data-structures coursework, thinking out loud, mock interviews, and comparing brute-force to optimized solutions)

**3. `source_07_chunk_002` — source: Building Confidence: Empower Yourself as a Woman in Tech**
> "...make and keep promises to yourself - tell yourself, 'I am becoming someone who trusts myself.' Develop this skill by setting and maintaining relevant boundaries... Resilience: be willing to bounce back from whatever challenges and setbacks you have..."

**4. `source_01_chunk_000` — source: How I Survived the Toughest Job Market as an International Student**
> "I landed a full-time job and got 2 internships before graduating in May. That's the result of 2,300+ applications for both internship and full-time positions. As an international student I can't tell how many rejections were because of sponsorship or my qualifications..."

**5. `source_05_chunk_002` — source: No Internship? No Problem**
> "HOW TO START: Look for 'good first issue' tags on GitHub; start with documentation improvements; fix small bugs to build confidence. CV LINE EXAMPLE: 'Contributed 12 pull requests to XYZ open-source library, improving performance by 15%.' THE FORMULA: Contributions + Library + Measurable Impact..."

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `bge-small-en-v1.5` via sentence-transformers. I chose it over `all-MiniLM-L6-v2` because MiniLM truncates inputs at 256 tokens, which would silently cut off my ~300-word chunks, whereas bge-small-en-v1.5 supports up to 512 tokens — matching my chunk size — while remaining small, fast, and free to run locally. Both are English-only, which fits my corpus since all 13 sources are in English. Retrieval uses top-k = 4 by cosine similarity, and queries are prefixed with BGE's recommended "Represent this sentence for searching relevant passages:" instruction.

**Production tradeoff reflection:** If I were deploying this for real users and cost were not a constraint, I would evaluate stronger models such as `bge-large-en-v1.5` for better English retrieval accuracy, or API-hosted models like OpenAI `text-embedding-3-large` and Cohere `embed-v3` for higher accuracy and longer context. Because my users are international students who may search in their first language, I would also consider a multilingual model such as `paraphrase-multilingual-MiniLM-L12-v2`, even though my current sources are all English. For nuanced career advice where the same idea is phrased many different ways, I would likely add a cross-encoder re-ranker (e.g., Cohere Rerank) on top of the initial retrieval. The tradeoffs are increased latency, infrastructure complexity, per-call cost, and sending data off-device, in exchange for more accurate retrieval.

---

## Retrieval Test Results

<!-- At least 3 queries, each showing the query and top returned chunks; for >=2, explain relevance. -->

Run `python -m src.retrieve` to reproduce. Distances are cosine distance (lower = more similar).

**Query 1: "What advice did a Squarespace recruiter give students without prior SWE internships applying for new grad roles?"**

| Rank | Distance | Source | Chunk |
|---|---|---|---|
| 1 | 0.277 | source_09 | chunk 20 — "...what helps new grad candidates stand out..." |
| 2 | 0.279 | source_09 | chunk 21 — "...our interview process looks like here at Squarespace..." |
| 3 | 0.294 | source_09 | chunk 13 — "...working with someone not knowing everything, but asking the right questions..." |
| 4 | 0.300 | source_09 | chunk 4 — "...how did you first start preparing..." |

*Why these are relevant:* All four top hits come from **source_09 — the Squarespace info session itself**, which is exactly the document the question targets, and all distances are low (≈0.28–0.30). The chunks cover what makes new-grad candidates stand out and how the Squarespace process works — directly on-topic for advice to students without internships.

**Query 2: "What resume formula was recommended for writing project bullet points?"**

| Rank | Distance | Source | Chunk |
|---|---|---|---|
| 1 | 0.287 | source_06 | chunk 1 — "...projects you list on your resume...shareable output..." |
| 2 | 0.320 | source_06 | chunk 2 — "...for Y. I used X tech, and this was my result..." |
| 3 | 0.325 | source_06 | chunk 0 — "How to Add Projects to Your Resume..." |
| 4 | 0.329 | source_05 | chunk 2 — "...THE FORMULA: Contributions + Library + Measurable Impact..." |

*Why these are relevant:* The top three hits are from **source_06**, the article specifically about adding projects to a resume, which contains the "[Action verb] + [What you did] + [Tech used] + [Measurable result]" formula. The fourth hit (source_05) independently states a closely related bullet-point formula, so even the lowest-ranked chunk is on-topic.

**Query 3: "What are common reasons international students are rejected from internships?"**

| Rank | Distance | Source | Chunk |
|---|---|---|---|
| 1 | 0.258 | source_01 | chunk 0 — "...can't tell how many rejections were because of sponsorship or my qualifications..." |
| 2 | 0.305 | source_01 | chunk 1 — resume/application volume details |
| 3 | 0.308 | source_02 | chunk 1 — "...best way to get accurate info is to ask the recruiter..." |
| 4 | 0.318 | source_02 | chunk 0 — F-1/OPT/CPT/H-1B advice intro |

Top hits come from the two international-student experience posts (source_01, source_02), with the best match explicitly naming sponsorship and qualifications as rejection factors.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The model receives a strict system prompt: *"You are a careers assistant for international students. Answer the user's question using ONLY the information in the provided context documents. Do not use any outside or prior knowledge, and do not guess. If the context does not contain enough information to answer, reply with exactly this sentence and nothing else: 'I don't have enough information on that.' When you use a fact, cite its source id in square brackets, e.g. [source_09]. Be concise and specific."* The retrieved chunks are formatted into a numbered, source-labelled context block (each prefixed with `[source_id] Title`) and passed in the user message, with `temperature=0` for deterministic, context-faithful answers.

Beyond the prompt, grounding is enforced *structurally* by a **relevance gate**: before calling the LLM, the system drops any retrieved chunk whose cosine distance exceeds 0.65, and if no chunk qualifies it returns the decline message **without calling the model at all**. This means an out-of-domain question (e.g. "What is the best recipe for chocolate chip cookies?") cannot be answered from the model's training knowledge — it is declined before generation.

**How source attribution is surfaced in the response:** Attribution is guaranteed **programmatically**, not left to the model. After generation, the system collects the source metadata (`source_id`, title, URL) of the chunks that were actually passed as context, de-duplicates them per document, and returns them as a separate `sources` list that the interface displays under "Retrieved from." The model is *also* asked to cite `[source_id]` inline, but the authoritative source list comes from the retrieval metadata, so attribution holds even if the model omits a citation. When the system declines (no relevant context), the source list is empty.

---

## Example Responses

<!-- >=2 responses with source attribution visible in the output, plus 1 out-of-scope refusal. -->

**Example 1 (in-scope, attribution visible):**
> **Q:** What resume formula was recommended for writing project bullet points?
> **A:** The recommended resume formula for writing project bullet points is: [Action verb] + [What you did] + [Tech used] + [Measurable result] **[source_06]**.
> **Retrieved from:** source_06 — How to Add Projects to Your Resume; source_05 — No Internship? No Problem

**Example 2 (in-scope, attribution visible):**
> **Q:** What are common reasons international students are rejected from internships?
> **A:** According to **[source_01]**, students who require sponsorship are always considered last. Additionally, **[source_02]** notes that hiring outside immigration lawyers to sponsor an H-1B costs money, making employers more likely to favor a U.S. citizen.
> **Retrieved from:** source_01 — How I Survived the Toughest Job Market...; source_02 — Advice for International Students in the US

**Example 3 (out-of-scope refusal):**
> **Q:** What is the best recipe for chocolate chip cookies?
> **A:** I don't have enough information on that.
> **Retrieved from:** (none)

This question is declined by the relevance gate before the LLM is even called, because no chunk is within the cosine-distance threshold — the system refuses rather than answering from general knowledge.

---

## Query Interface

<!-- Description of input/output fields + a sample interaction transcript. -->

The interface is a **Gradio web app** (`app.py`), launched with `python app.py` and opened at `http://localhost:7860`.

**Input field:**
- **"Your question"** — a single-line textbox. Submit by clicking the **Ask** button or pressing Enter. Clickable example questions are provided below the box.

**Output fields:**
- **"Answer"** — the grounded answer text, with inline `[source_id]` citations.
- **"Retrieved from"** — the list of source documents (id, title, URL) the answer drew from; shows "(no sources...)" when the system declines.

**Sample interaction transcript:**
```
Your question:  How can I build experience over the summer without an internship?

Answer:         You can build experience over the summer without an internship by
                following 9 practical ways: 1. building a project, 2. contributing to
                open source, 3. freelance/micro work, 4. skill sprint, 5. hackathons,
                6. research/teaching, 7. practicing technical skills, 8. building your
                network, and 9. gaining career clarity [source_05]. You can also create
                a personalized 8-week action plan and turn summer activities into strong
                CV bullets [source_05].

Retrieved from: • source_05 — No Internship? No Problem
                • source_03 — I'm an international student at UNC. Here's how I got an
                  AI summer internship.
```

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What advice did a Squarespace recruiter give students without prior SWE internships who are applying for new grad roles? | Tech-adjacent experience can still be valuable. Projects, hackathons, leadership positions, clubs, and other relevant experiences can help demonstrate skills and initiative. | Stand out through projects, clubs, leadership roles, and hackathon experience; include projects on your resume and be able to speak to them. Cites [source_09]. | Relevant (top distance 0.27, correct source) | Accurate |
| 2 | What building blocks were recommended for overcoming self-doubt? | Self-awareness, self-trust, resilience, growth mindset, self-compassion, and commitment. | Lists all six: self-awareness, self-trust, resilience, growth mindset, self-compassion, commitment. Cites [source_07]. | Relevant (top distance 0.24, correct source) | Accurate |
| 3 | What resume formula was recommended for writing project bullet points? | [Action Verb] + [What You Did] + [Technology Used] + [Measurable Result] | "[Action verb] + [What you did] + [Tech used] + [Measurable result]." Cites [source_06]. | Relevant (top distance 0.29, correct source) | Accurate |
| 4 | What strategies did new graduate software engineers recommend for improving at LeetCode? | Paying attention in data structures and algorithms courses, explaining solutions out loud, doing mock interviews, and comparing brute-force solutions to optimized approaches. | Find your best way to learn/retain (reading, writing, implementing, notes); do problems out loud; do mock interviews. Cites [source_09]. Captured "out loud" + "mock interviews" but omitted the DSA-courses and brute-force-vs-optimized points. | Relevant (correct chunk retrieved at rank #2, distance 0.27) | Partially accurate |
| 5 | What are common reasons international students are rejected from internships? | Sponsorship requirements and not meeting job qualifications are frequently cited reasons. | Sponsorship: students needing sponsorship are considered last, and H-1B sponsorship cost makes employers favor U.S. citizens. Cites [source_01, source_02]. Captured sponsorship strongly but did not mention "not meeting qualifications." | Relevant (top distance 0.26, correct sources) | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** *"What strategies did new graduate software engineers recommend for improving at LeetCode?"* (Q4 — partially accurate.)

**What the system returned:** The system answered that you should find your own best way to learn and retain information (one speaker described "reading, writing, implementing" and taking notes), practice problems out loud, and do mock interviews with friends. It captured two of the four expected strategies ("out loud" and "mock interviews") but **omitted** "paying attention in data structures and algorithms courses" and "comparing brute-force solutions to optimized approaches."

**Root cause (tied to a specific pipeline stage):** This is a **generation-stage (synthesis) failure, not a retrieval failure.** I verified that the chunk containing *all four* expected strategies — `source_09_chunk_006`, which explicitly mentions brute-force vs. optimized, thinking out loud, mock interviews, and DSA coursework — was retrieved at **rank #2 with a low distance of 0.271**, so the correct information was present in the LLM's context. The model nonetheless produced a selective summary: it latched onto one speaker's personal learning anecdote ("reading, writing, implementing") and under-extracted the other concrete tips that were in the same chunk. In other words, retrieval did its job; the LLM's summarization dropped relevant points rather than enumerating them.

**What you would change to fix it:** (1) Tighten the system prompt to instruct the model to **enumerate all distinct strategies/items found in the context** rather than summarizing, e.g. "List every distinct recommendation present in the context as bullet points." (2) Optionally lower `temperature` is already 0, so instead add a light post-generation completeness check, or (3) for list-style questions, increase `top-k` slightly and ask the model to deduplicate — though since the key chunk was already retrieved, the highest-leverage fix here is the prompt change, not retrieval tuning.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Writing the Chunking Strategy and Retrieval Approach sections in detail *before* coding caught a real bug before it happened. The spec's reasoning about embedding token limits made me realize that the commonly recommended `all-MiniLM-L6-v2` truncates at 256 tokens, which would have silently cut off my ~300-word chunks. Because that reasoning was already written down, the choice to use `bge-small-en-v1.5` (512 tokens) and to cap chunks at ~380 words "with the overlap counted inside the cap" flowed directly into the implementation, and the embedding step worked on the first build with zero chunks over the limit. The spec turned an easy-to-miss silent failure into a deliberate, documented decision.

**One way your implementation diverged from the spec, and why:** My planning.md AI Tool Plan named Claude as the generation LLM, but the implementation uses **Groq's `llama-3.3-70b-versatile`**. I switched because the starter repository was already configured for Groq — `requirements.txt` includes the `groq` client and `.env.example` ships a `GROQ_API_KEY` — and Groq's free tier needs no credit card or rate-limit management, which suited a student project. The grounding logic and prompt are model-agnostic, so the swap required no architectural change. (A smaller divergence: the chunk hard cap moved from the originally written ~400 words to ~380 to leave headroom for overlap under the 512-token limit; I updated planning.md to reflect this.)

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1 — Ingestion and chunking**

- *What I gave the AI:* My planning.md Documents section (the 13 sources and their file types), my full Chunking Strategy section (~300-word target, ~60-word overlap, preprocessing rules), and my pipeline diagram. I asked it to implement a script that loads the documents, cleans them, and chunks them to spec.
- *What it produced:* `src/ingest.py` with `load_documents()`, a type-aware `preprocess()` (GitHub chrome stripping, transcript/slide line-rejoin, whitespace normalization), and a paragraph-first `chunk_text()` with sentence fallback and word-level overlap.
- *What I changed or overrode:* I overrode the hard cap from ~400 to ~380 words so that adding the overlap never pushes a chunk past the embedding model's 512-token limit. After reviewing a printed sample I caught two issues the first version missed: leftover Reddit/forum **comment sections** (I removed these from the raw files) and **HTML artifacts** (`</code>`, `&lt;`) in the interview articles, so I had it add a general HTML-tag/entity stripping step (tags removed before unescaping, to protect angle brackets inside code).

**Instance 2 — Embedding, retrieval, and grounded generation**

- *What I gave the AI:* My planning.md Retrieval Approach section (`bge-small-en-v1.5`, top-k=4, BGE query prefix) and pipeline diagram, plus my grounding requirement (answer from retrieved context only, with programmatic source attribution).
- *What it produced:* `src/embed.py` (embed chunks into ChromaDB with source metadata), `src/retrieve.py` (top-k retrieval with distances), `src/generate.py` (Groq-backed grounded answering), and a Gradio `app.py`.
- *What I changed or overrode:* I directed it to make source attribution **programmatic** (built from retrieval metadata) rather than trusting the LLM to cite correctly, and to add a **relevance gate** that declines out-of-domain questions before the LLM is ever called — strengthening grounding beyond the prompt instruction alone.

---
[App Demo Link](https://www.loom.com/share/28ee95ed4e6949088f48fd92fa819d1d)