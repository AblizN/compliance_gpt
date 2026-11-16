# Engineering notes

## PDF text extraction: noise observations

pypdf keeps the line breaks from the printed page, so sentences break wherever the column wrapped. Pages also start in the middle of a sentence. Page 20 opens with "protection essentially equivalent…", which is the end of a recital from page 19.
Some layout junk comes through as text too: a stray "I" above "(Legislative acts)" on page 1, and a double space after recital numbers like "(105)  Apart from".

## Chunk quality (800 chars / 100 overlap)

- Mid-word cuts: fixed-size splitting does not care about words or sentences. Page 1 chunk 0 ends with "...Committee of the Region" and page 2 chunk 0 ends with "(5)  T". The overlap saves the text, but every chunk starts and ends with a fragment.
- Article split from its heading: I chunk page by page, so an article that runs over a page break loses its number. Page 44 chunk 0 has Article 17(1)(b)–(f) but the words "Article 17" are not in it, so a search for that article may miss it.
- Footer and footnote noise: the footer "4.5.2016 L 119/N Official Journal of the European Union EN" is in N of 543 chunks. Some chunks are almost nothing but footnotes (page 1 chunk 3, and page 6 chunk 7, which is the shortest at 109 chars). They get embedded like real content.

## Embeddings: first look (text-embedding-3-small)

I embedded three sentences and compared them with my own cosine similarity function (1536 dims each).

- "A DPIA is required for high-risk processing" vs "Impact assessments are mandatory before risky data use": 0.57, with almost no shared words.
- Either one vs "The pizza in Naples is excellent": 0.07 and 0.01.

So it compares meaning, not words. The model has seen "DPIA" and "impact assessment" in the same kind of text, so it puts them close together. A question worded differently from the regulation should still find the right chunk.

## Search: first look (top-5 by cosine, text-embedding-3-small)

I ran five questions through search.py. Two results surprised me.

- The acronym costs a quarter of the score. "What is a DPIA?" finds the right chunk (page 53, Article 35) at 0.476. "What is a data protection impact assessment?" finds the same chunk at 0.735. Same chunk, same rank, very different score. The regulation never uses the word "DPIA", so the question and the chunk share no words. The model knows the acronym, so the ranking is still right, but the score drops. A fixed score threshold would have thrown away a correct hit. My guess: expand short acronyms before embedding, like "DPIA (data protection impact assessment)".

- Recitals rank above the article they explain. For "What are the lawful bases for processing?" all five hits are recitals from pages 8 and 9. Article 6 on page 36, which is the actual list, is not there. Recitals are full sentences that read like an answer to a question. Article 6 is a short list. Cosine similarity likes the sentences more. But for a cited answer the article is the real source, so similarity alone does not pick the right chunk. My guess: put article numbers in the chunk metadata so search can prefer article text, or at least label it.

One more thing from the output: the mid-word cuts from the chunk quality section now show up in the top results ("ice of the data protection officer", "Rectif ication"). I have to fix the chunker.

## Answer prompt: what each rule prevents

prompts/answer.txt has five rules. Each one is there to stop one kind of bad answer.

- Answer only from the context: without it the model fills gaps from memory, and that can be outdated, from another regulation, or made up.
- Cite every claim with [n]: without it I cannot check the answer. With it, every sentence points to a passage with a regulation and page, so I can look it up.
- Reply exactly "Not in my sources." when the context does not cover the question: without it the model guesses when retrieval is weak. The fixed text also makes a refusal easy to detect in code and in evals.
- Be concise: long answers repeat the context and hide the one sentence that matters. Extra text is also where unsupported claims get in.
- Do not give legal advice: the model should say what the regulation says, not tell someone what to do in their own case. That is a job for a lawyer.
