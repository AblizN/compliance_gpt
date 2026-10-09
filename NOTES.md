# Engineering notes

## PDF text extraction: noise observations

pypdf keeps the PDF's visual line breaks, so sentences are split mid-line wherever the printed column wrapped, and pages start mid-sentence (page 20 opens with "protection essentially equivalent…", the tail of a recital from page 19).
Layout artifacts also come through as text: a stray "I" (the Official Journal series marker) above "(Legislative acts)" on page 1, and a double space after recital numbers like "(105)  Apart from".

## Chunk quality (800 chars / 100 overlap)

- **Mid-word cuts:** fixed-size splitting ignores word and sentence boundaries; page 1 chunk 0 ends "...Committee of the Region" and page 2 chunk 0 ends "(5)  T". Overlap keeps the text, but every chunk starts and ends with fragments.
- **Article split from its heading:** chunking is per page, so an article that crosses a page break loses its number; page 44 chunk 0 holds Article 17(1)(b)–(f) with no "Article 17" in its text, so a query for that article may miss it.
- **Footer/footnote noise:** the page footer "4.5.2016 L 119/N Official Journal of the European Union EN" appears in N of 543 chunks, and some chunks are almost only footnote citations (page 1 chunk 3; page 6 chunk 7, the 109-char minimum). They get embedded as if they were content.