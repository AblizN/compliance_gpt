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
- Reply exactly "Not in my sources." when no passage is relevant: without it the model guesses when retrieval is weak. The fixed text also makes a refusal easy to detect in code and in evals. If the passages cover only part of the question, the model should answer that part. My first version of this rule was stricter and the model refused questions it could mostly answer.
- Be concise: long answers repeat the context and hide the one sentence that matters. Extra text is also where unsupported claims get in.
- Do not give legal advice: the model should say what the regulation says, not tell someone what to do in their own case. That is a job for a lawyer.

## First grounded answers (gpt-4o-mini, k=5, temperature 0)

answer.py retrieves five chunks, numbers them, fills prompts/answer.txt and makes one chat call. These are the answers from the demo run.

What is a DPIA?

> A Data Protection Impact Assessment (DPIA) is a process required to evaluate the origin, nature, particularity, and severity of risks associated with the processing of personal data. It is particularly necessary in cases such as systematic and extensive evaluations based on automated processing, large-scale processing of special categories of data, or systematic monitoring of publicly accessible areas [1][2]. The outcome of the DPIA should inform the appropriate measures to ensure compliance with data protection regulations, and if a DPIA indicates a high risk that cannot be mitigated, a consultation with the supervisory authority is required prior to processing [2][3].

What is the right to erasure?

> The right to erasure, also known as the 'right to be forgotten,' allows a data subject to obtain the erasure of personal data concerning them without undue delay. This right applies when the personal data is no longer necessary for the purposes for which it was collected, when the data subject has withdrawn consent, or when the processing does not comply with the GDPR [1][3]. Additionally, if the controller has made the personal data public, they are obliged to inform other controllers processing that data to erase any links or copies [2][4].

What are the lawful bases for processing?

> The lawful bases for processing include:
>
> 1. Compliance with a legal obligation to which the controller is subject.
> 2. Processing necessary for the performance of a task carried out in the public interest or in the exercise of official authority.
> 3. Further processing for archiving purposes in the public interest, scientific or historical research purposes, or statistical purposes, which should be considered compatible lawful processing operations [1][2].
> 4. Processing based on the vital interest of another natural person, which should occur only when no other legal basis is manifestly applicable [3].
> 5. Legitimate interests of the controller, provided that these do not override the fundamental rights and freedoms of the data subject [3][5].

What does Chinese law say about DPIAs? (out of scope)

> Not in my sources.

What I learned from these runs:

- A worked example in the prompt can block its own topic. My first prompt had an example about a DPIA. With it, the model answered "Not in my sources." to every DPIA question, at k = 5, 6, 8 and 10, even when the right passage was in the context. Making the refusal rule softer was not enough. It only worked after I also replaced the example with one about the data protection officer. Questions about the data protection officer still get answered, so the new example does not block its own topic. I do not know why the two examples behave differently.
- The answer is only as good as the retrieval. The lawful bases answer is wrong in a quiet way: consent and contract are missing, point 3 is not a lawful basis, and points 1 and 2 have no citation. This is the recital problem from the search notes. Article 6 is not in the top five, so the model builds a list from recitals. The answer still reads well, which is the dangerous part.
- For "What is a DPIA?" the chunk with Article 35(1) is ranked 6th, just outside k=5. The answer comes from the chunks next to it.
- I checked about ten questions by hand. That is not an eval. The prompt is tuned on a few examples and needs a proper question set before I trust it.
