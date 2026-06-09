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

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `bge-small-en-v1.5` via sentence-transformers. I chose it over `all-MiniLM-L6-v2` because MiniLM truncates inputs at 256 tokens, which would silently cut off my ~300-word chunks, whereas bge-small-en-v1.5 supports up to 512 tokens — matching my chunk size — while remaining small, fast, and free to run locally. Both are English-only, which fits my corpus since all 13 sources are in English. Retrieval uses top-k = 4 by cosine similarity, and queries are prefixed with BGE's recommended "Represent this sentence for searching relevant passages:" instruction.

**Production tradeoff reflection:** If I were deploying this for real users and cost were not a constraint, I would evaluate stronger models such as `bge-large-en-v1.5` for better English retrieval accuracy, or API-hosted models like OpenAI `text-embedding-3-large` and Cohere `embed-v3` for higher accuracy and longer context. Because my users are international students who may search in their first language, I would also consider a multilingual model such as `paraphrase-multilingual-MiniLM-L12-v2`, even though my current sources are all English. For nuanced career advice where the same idea is phrased many different ways, I would likely add a cross-encoder re-ranker (e.g., Cohere Rerank) on top of the initial retrieval. The tradeoffs are increased latency, infrastructure complexity, per-call cost, and sending data off-device, in exchange for more accurate retrieval.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What advice did a Squarespace recruiter give students without prior SWE internships who are applying for new grad roles? | Tech-adjacent experience can still be valuable. Projects, hackathons, leadership positions, clubs, and other relevant experiences can help demonstrate skills and initiative. | | | |
| 2 | What building blocks were recommended for overcoming self-doubt? | Self-awareness, self-trust, resilience, growth mindset, self-compassion, and commitment. | | | |
| 3 | What resume formula was recommended for writing project bullet points? | [Action Verb] + [What You Did] + [Technology Used] + [Measurable Result] | | | |
| 4 | What strategies did new graduate software engineers recommend for improving at LeetCode? | Paying attention in data structures and algorithms courses, explaining solutions out loud, doing mock interviews, and comparing brute-force solutions to optimized approaches. | | | |
| 5 | What are common reasons international students are rejected from internships? | Sponsorship requirements and not meeting job qualifications are frequently cited reasons. | | | |

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

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
