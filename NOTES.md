# Engineering notes

## PDF text extraction: noise observations

pypdf keeps the PDF's visual line breaks, so sentences are split mid-line wherever the printed column wrapped, and pages start mid-sentence (page 20 opens with "protection essentially equivalent…", the tail of a recital from page 19).
Layout artifacts also come through as text: a stray "I" (the Official Journal series marker) above "(Legislative acts)" on page 1, and a double space after recital numbers like "(105)  Apart from".