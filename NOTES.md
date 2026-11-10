# Engineering notes

## PDF text extraction: noise observations

pypdf keeps the PDF's visual line breaks, so sentences are split mid-line wherever the printed column wrapped, and pages start mid-sentence (page 20 opens with "protection essentially equivalent…", the tail of a recital from page 19).
Layout artifacts also come through as text: a stray "I" (the Official Journal series marker) above "(Legislative acts)" on page 1, and a double space after recital numbers like "(105)  Apart from".

## Chunk quality (800 chars / 100 overlap)

- **Mid-word cuts:** fixed-size splitting ignores word and sentence boundaries; page 1 chunk 0 ends "...Committee of the Region" and page 2 chunk 0 ends "(5)  T". Overlap keeps the text, but every chunk starts and ends with fragments.
- **Article split from its heading:** chunking is per page, so an article that crosses a page break loses its number; page 44 chunk 0 holds Article 17(1)(b)–(f) with no "Article 17" in its text, so a query for that article may miss it.
- **Footer/footnote noise:** the page footer "4.5.2016 L 119/N Official Journal of the European Union EN" appears in N of 543 chunks, and some chunks are almost only footnote citations (page 1 chunk 3; page 6 chunk 7, the 109-char minimum). They get embedded as if they were content.

## Embeddings: first look (text-embedding-3-small)

Embedded three sentences and compared them with hand-written cosine similarity (1536 dims each).

- "A DPIA is required for high-risk processing" vs "Impact assessments are mandatory before risky data use": **0.57**, with almost no shared words.
- Either one vs "The pizza in Naples is excellent": **0.07** and **0.01**.

Meaning gets compared, not vocabulary: the model learned from huge amounts of text that "DPIA" and "impact assessment" appear in the same contexts, so it places them close together. A question worded differently from the regulation should still find the right chunk.

## Search: first look (top-5 by cosine, text-embedding-3-small)

Ran five questions through search.py. Two results I did not expect.

- **The acronym costs a quarter of the score.** "What is a DPIA?" returns the right chunk (page 53, Article 35) at **0.476**. The spelled-out "What is a data protection impact assessment?" returns the same chunk at **0.735**. Same chunk, same rank, very different confidence. The regulation never writes "DPIA", so the question and the chunk share no surface vocabulary; the model still knows the acronym from training data, which is why the ranking survives, but the chunk's own words pull the match down. A fixed similarity threshold would have rejected a correct hit here. Guess: short acronym questions need query expansion ("DPIA (data protection impact assessment)") before embedding.

- **Recitals outrank the article they explain.** For "What are the lawful bases for processing?" all five hits are recitals from pages 8 and 9. Article 6, the actual list of lawful bases on page 36, does not appear. Recitals are written as explanatory prose, which reads like a question; Article 6 is a terse enumerated list. Cosine similarity rewards the prose. For a cited answer the article is the authoritative source, so similarity alone cannot pick the right chunk. Guess: this needs article numbers in chunk metadata so retrieval can prefer or at least label article text over recital text.

Also visible in the output: the mid-word cuts from the chunk-quality section now show up as rank-1 snippets ("ice of the data protection officer", "Rectif ication"). The chunker fixes are no longer optional.
