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
