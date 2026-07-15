# Paper Research Assistant — Project Guide

**Goal:** Build a system where dropping PDFs into a folder automatically extracts structured notes into your paper tracker, builds a searchable corpus, and lets you ask natural-language questions that get answered from specific papers — grounded, cited, and honest when it doesn't know.

**Rule for the whole project:** No AI-generated code. Use Claude for direction, concept explanations, and debugging discussions only — you write every line yourself. This is what actually builds the skill.

**Total timeline:** 3 sessions across 3-5 days. Don't compress — each milestone has a hard acceptance gate. Do not start the next milestone until the current one's checklist is fully checked.

---

## Milestone 1: Ingestion Pipeline

**Target:** End of Session 1 (~3 hours)
**Builds:** PDF → extracted structured fields → tracker row + corpus entry

### Steps

**1. Environment and data prep (30 min)**
- Install: a PDF text-extraction library (pdfplumber or PyMuPDF — pdfplumber tends to handle academic two-column layouts better), a spreadsheet library (pandas or openpyxl), and your LLM SDK (Anthropic or OpenAI).
- Gather 5-10 PDFs you already understand deeply (papers from your earlier reading list — e.g. GPTQ, AWQ). Using known papers lets you verify correctness later, not just check that code runs without crashing.

> **Hint:** Store your API key as an environment variable, not hardcoded in your script. Test that you can import all three libraries with zero errors before writing any real logic — isolate environment problems from logic problems.

**2. Extract raw text from a PDF (30-40 min)**
- Write the extraction call for a single PDF. Print the first 300-500 characters and visually confirm it's real, readable text.

> **Hint:** Academic PDFs are usually two-column. A naive extractor sometimes reads left-column-then-right-column correctly, but sometimes interleaves lines from both columns into nonsense. If your extracted text reads like garbled fragments jumping between topics mid-sentence, that's the two-column bug — try a different extraction library or a page-region-aware extraction mode before assuming your code is broken.

**3. Trim to what matters (20-30 min)**
- Decide what subset of the paper to actually send to the LLM: abstract + introduction + conclusion, plus maybe first paragraphs of major sections, rather than the entire paper.

> **Hint:** This is a deliberate context-budget decision, not a shortcut — write one sentence in your notes explaining why you chose this subset. You'll want this justification later (interviews ask about this exact tradeoff).

**4. Design the extraction prompt (30-40 min)**
- Write a prompt instructing the model to extract fields matching your tracker columns (Problem, Key Idea, Evaluation, Result, Limitation, Relevance) using ONLY the provided text.
- Explicitly instruct it not to use prior/trained knowledge about the paper, even if it recognizes the title.
- Request strict JSON output matching your column names exactly.

> **Hint:** The "don't use prior knowledge" instruction matters more than it seems. Well-known papers can trigger the model to "recall" details from training that aren't actually in the text you gave it — this is a real, sneaky hallucination source that's easy to miss if you're not specifically testing for it (see Step 8).

**5. Parse, validate, retry (20-30 min)**
- Parse the JSON response. If it fails to parse, or fields are missing, retry once with a stricter reminder in the prompt.
- Do not silently accept a partial or malformed result.

> **Hint:** Log every retry that happens, even if it eventually succeeds. If you're retrying on more than ~1 in 5 papers, your prompt's format instruction needs tightening, not just more retries.

**6. Write to the tracker (20-30 min)**
- Append the validated fields as a new row in your paper tracker spreadsheet, matching your existing columns exactly.
- Set "Pass Completed" to 1 for these rows — this was an automated skim, not your own deep read. Keep this distinction honest in your own data.

**7. Generate the corpus document (10-15 min)**
- Immediately after writing the row, build the combined text string (e.g. `"Title: ... | Topic: ... | Key Idea: ... | Result: ... | Limitation: ..."`) and save it to a growing corpus file/list — one entry per paper.

**8. Validate against papers you know (30-40 min)**
- Run the full pipeline on 2-3 papers you deeply understand.
- Compare the extracted Key Idea and Result against what you actually know is true.

> **Hint:** This is your most important test in this whole milestone. If the model states a result or number that isn't actually in the text you fed it, that's a hallucination — go back to Step 4 and make the "text only" constraint even more explicit (e.g. add "if information is not present in the given text, write 'not stated' rather than inferring it").

**9. Batch it (20-30 min)**
- Loop Steps 2-7 over every PDF in a folder so a stack of papers processes in one run.

### Milestone 1 Acceptance Checklist
- [ ] Extracted text from a sample PDF is readable, not garbled by column-interleaving
- [ ] For at least 2 known papers, extracted Key Idea and Result match your own understanding — no invented claims
- [ ] Malformed model output (bad JSON) is caught and retried, not silently accepted
- [ ] Every processed paper produces both a tracker row AND a corpus entry
- [ ] You can point to one sentence explaining why you chose your specific text-trimming strategy (Step 3)

**Do not proceed to Milestone 2 until every box above is checked.**

---

## Milestone 2: Query Pipeline

**Target:** End of Session 2 (~2.5 hours)
**Builds:** Question → embedding retrieval → matched paper → grounded answer
**Dependency:** Requires Milestone 1 fully complete — bad corpus data makes this milestone undebuggable.

### Steps

**10. Build the embedding index (30-40 min)**
- Load your corpus (from Step 7). For each document, generate an embedding vector using a local model (`sentence-transformers` is free, runs fine on CPU at this scale).
- Store each as a `(title, text, vector)` unit — a plain in-memory list is enough for a few dozen papers; you don't need a real vector database yet.

> **Hint:** Print the vector for one paper and confirm it's a list of numbers with consistent length across papers — a quick sanity check before building retrieval logic on top of it.

**11. Embed and compare the user's question (30-40 min)**
- Embed the user's question the same way as your documents.
- Compute cosine similarity between the question vector and every stored document vector, then sort to find the top matches.

> **Hint:** Print just titles and similarity scores first, without generation attached. If the top result doesn't intuitively make sense for the question, debug retrieval in isolation before connecting it to the LLM call — don't try to diagnose two layers of the system at once.

**12. Set a relevance threshold (15-20 min)**
- Decide a similarity score cutoff below which the system responds "I don't have a paper on that" instead of forcing a weak match.

> **Hint:** Without this threshold, your system will always return "the closest paper," even when nothing in your corpus is actually relevant — this is one of the most common real RAG failure modes, and you will hit it if you skip this step.

**13. Generate the grounded answer (25-30 min)**
- Take the top-matched paper's corpus text and the user's question. Prompt the model to answer using only that retrieved text, and to explicitly state which paper the answer comes from.

**14. Test deliberately (25-30 min)**
Run and actually read the output for:
- A question clearly covered by one paper — check accuracy.
- A question with no relevant paper in your corpus — confirm the threshold correctly triggers "I don't know."
- A borderline/ambiguous topic — observe the behavior, don't just assume it's fine.
- A topic covered by two different papers — check whether it returns one or both, and decide if that matches what you want.

**15. Wrap in a loop (15 min)**
- A simple loop so you can ask multiple questions without restarting the program.

### Milestone 2 Acceptance Checklist
- [ ] A question clearly covered by a paper returns the correct paper and an accurate answer
- [ ] A question with no relevant paper triggers an explicit "I don't have that," not a forced weak match
- [ ] The answer explicitly names which paper it came from
- [ ] You've manually reviewed at least 5 different test questions, not just the first one that worked
- [ ] You know your chosen similarity threshold value and can explain why you picked it

**Do not proceed to Milestone 3 until every box above is checked.**

---

## Milestone 3: End-to-End System, Stress-Tested

**Target:** Session 3 (~1.5-2 hours)
**Builds:** Full pipeline connection + documented failure modes

### Steps

**16. Run it end to end for real (30-40 min)**
- Drop 3-5 NEW PDFs (not used in Milestones 1-2) into your ingestion pipeline.
- Once processed, immediately query your chatbot about a topic from one of those new papers.

> **Hint:** This is the real integration test. If Milestones 1 and 2 passed individually but this step fails, the bug is almost always in the handoff between them — e.g. a formatting mismatch between what Step 7 writes and what Step 10 expects to read.

**17. Break it on purpose (20-30 min)**
- Feed it one deliberately hard input: a poorly formatted or scanned PDF, or an oddly phrased/trick question.
- Note exactly where it fails: extraction, JSON parsing, or retrieval/generation.

> **Hint:** Knowing precisely where your system breaks is more valuable, and more interview-relevant, than a demo that only ever works on clean inputs.

**18. Log the whole build (15-20 min)**
- Write down: what worked on the first try, what needed a fix and why, and one thing you'd redesign if starting over.

### Milestone 3 Acceptance Checklist
- [ ] New PDFs go in one end, and you can query them from the other end with no manual steps in between
- [ ] You've deliberately tested one hard input and documented what happened
- [ ] You have a written 3-5 sentence retrospective note

**Definition of done:** All checklists above fully checked, plus the retrospective note exists. A system that "mostly works" without documented failure cases isn't finished — you won't be able to speak to it credibly later.

---

## How to use this file day to day

- Work through one numbered step at a time. Check off the milestone boxes only when you've actually verified the criterion yourself, not when the code merely runs without an error.
- When something breaks: bring the exact error message and what you were trying to do to Claude. Ask for the concept behind the failure, not the fix — write the fix yourself.
- Keep a running note under each milestone (in this file or your paper tracker) of anything that surprised you. This becomes real material for interviews and for describing this project later.

## Total time estimate: ~6-7 hours across Milestones 1-2, plus ~1.5-2 hours for Milestone 3 — realistically 3 sessions over 3-5 days, not one sitting.