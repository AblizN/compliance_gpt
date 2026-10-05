# ComplianceGPT — Architecture

```
┌────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌──────────────────────┐
│  LOAD  │──▶│  CHUNK  │──▶│  EMBED  │──▶│  STORE  │──▶│  RETRIEVE + ANSWER   │ ◀── Evaluation
└────────┘   └─────────┘   └─────────┘   └─────────┘   └──────────────────────┘


## The five boxes

1. **Load** — In: compliance documents PDF. Out: plain text plus metadata (file name, page, section).
2. **Chunk** — In: the full text of each document. Out: small overlapping passages (e.g. ~800 characters, ~100 overlap), each tagged with its source.
3. **Embed** — In: each text chunk. Out: a vector (list of numbers) that captures the chunk's meaning.
4. **Store** — In: vectors plus their chunk text and metadata. Out: a searchable vector index (e.g. data/chroma/) saved to disk.
5. **Retrieve + Answer** — In: the user's question (embedded the same way). Out: the top-k most similar chunks with similarity scores, and an LLM answer grounded in those chunks with citations.

**Evaluation** (arrow back to box 5) — In: a fixed set of test questions with expected answers/sources. Out: scores for retrieval quality (right chunks found?) and answer quality (correct, grounded, cited?), used to tune the retrieve + answer step.

## Why does the similarity score from retrieval matter for a guardrail?

The similarity score tells us how close the best-matching chunks are to the question, so it is the system's evidence that the answer actually exists in the documents. If the top score falls below a threshold, the guardrail should stop the LLM from answering and reply "Not in my sources." instead. Without that check, the LLM would still produce a fluent answer from weakly related chunks or its own general knowledge — a hallucination — which in a compliance tool means confidently wrong guidance with a fake-looking citation.
