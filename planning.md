# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
I chose the International Student Career Survival Guide as my domain because international students often struggle to find career advice that addresses their specific experiences. Although official resources provide useful information, it is usually spread across multiple websites and focuses more on policies than real-world guidance. In my experience, some of the most helpful advice came from other international students through Reddit, career webinars, and communities such as CodePath, ColorStack, and Rewriting the Code. This project will make that knowledge easier to search and access by bringing it together in one place.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | How I Survived the Toughest Job Market as an International Student | International student internship search experience, application volume, recruiting challenges, sponsorship concerns | https://www.reddit.com/r/internships/comments/1jpcszv/how_i_survived_the_toughest_job_market_as_an/ |
| 2 | Advice for International Students in the US | Career advice, networking, recruiting mistakes, internship strategy, long-term planning | https://www.wallstreetoasis.com/forum/investment-banking/advice-for-international-students-in-the-us-f-1-visa-opt-cpt-h-1b |
| 3 | I'm an international student at UNC. Here's how I got an AI summer internship. | Personal success story, networking, projects, internship search strategy | https://www.businessinsider.com/unc-student-landed-internship-after-changing-major-2026-4 |
| 4 | Want to land a tech internship? A Google engineer explains how networking 'intentionally' can help | Projects, networking, interview preparation, internship recruiting | https://www.businessinsider.com/google-engineer-advice-internship-tech-job-offer-2025-6 |
| 5 | No Internship? No Problem | Advice for leveling-up your resume if you didn't land a summer internship | data/raw/source_05.txt |
| 6 | How to Add Projects to Your Resume (And Actually Get Credit for Them) | How to add projects to your resume | https://rewritingthecode.org/resources/member-resources/how-to-add-projects-to-your-resume/ |
| 7 | Building Confidence: Empower Yourself as a Woman in Tech | Building confidence in your career | https://rewritingthecode.org/resources/member-resources/building-confidence-empower-yourself-as-a-woman-in-tech/ |
| 8 | Google Early Careers Session Notes | Tips from a Google recruiter and Nooglers | data/raw/source_08.txt |
| 9 | Squarespace Acing Technical Recruitment Info Session | Tips from a Squarespace recruiter and two SWE recent grads | data/raw/source_09.txt |
| 10 | How to Ace the First 30 Days of Your New Job | Thriving in your new job during the first 30 days | https://rewritingthecode.org/resources/member-resources/how-to-ace-the-first-30-days/ |
| 11 | Underclassmen Opportunities | A resource for finding underclassmen career opportunities | https://github.com/Jose-Gael-Cruz-Lopez/underclassmen-opportunities/tree/main?tab=readme-ov-file |
| 12 | Google's AI-Assisted Coding Interview (2026 Guide) | A guide on Google's AI-assisted coding interview | https://www.tryexponent.com/blog/google-ai-coding-interview |
| 13 | Using AI in Meta's AI-assisted coding interview (with real prompts and examples) | A guide on Meta's AI-assisted coding interview | https://interviewing.io/blog/how-to-use-ai-in-meta-s-ai-assisted-coding-interview-with-real-prompts-and-examples |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
