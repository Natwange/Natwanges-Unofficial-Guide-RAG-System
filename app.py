"""
Gradio web interface for The Unofficial Guide RAG system (Milestone 5).

Wires the full pipeline together: a question is embedded, the top-k chunks are
retrieved from ChromaDB, and Groq's llama-3.3-70b-versatile answers using only
that context. The answer and the documents it drew from are shown separately.

Prerequisites:
    1. Build the index once:   python -m src.ingest && python -m src.embed
    2. Set GROQ_API_KEY in .env (copy from .env.example).

Run:
    python app.py
Then open http://localhost:7860
"""

import gradio as gr

from src.generate import ask


def handle_query(question: str):
    """Answer a question and format the retrieved sources for display."""
    question = (question or "").strip()
    if not question:
        return "Please enter a question.", ""

    result = ask(question)

    if result["sources"]:
        sources = "\n".join(
            f"• {s['source_id']} — {s['title']}\n  {s['url']}"
            for s in result["sources"]
        )
    else:
        sources = "(no sources — the answer was not found in the documents)"

    return result["answer"], sources


EXAMPLES = [
    "What resume formula was recommended for writing project bullet points?",
    "What are common reasons international students are rejected from internships?",
    "How can I build experience over the summer without an internship?",
    "What building blocks help with overcoming self-doubt?",
]

with gr.Blocks(title="The Unofficial Guide") as demo:
    gr.Markdown(
        "# 🌍 The Unofficial Guide\n"
        "Career advice for international students, answered **only** from a "
        "curated set of documents. If the documents don't cover your question, "
        "the system will say so rather than guess."
    )
    inp = gr.Textbox(label="Your question",
                     placeholder="e.g. How do I add projects to my resume?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=5)
    gr.Examples(examples=EXAMPLES, inputs=inp)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    demo.launch()