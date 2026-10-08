import json
import os

from pypdf import PdfReader

import config

PDF_PATH = os.path.join(config.RAW_DIR, "gdpr.pdf")
OUTPUT_PATH = os.path.join(config.PROCESSED_DIR, "gdpr.json")


def load_pdf(file_path: str) -> list[str]:
    page_list = []
    reader = PdfReader(file_path)
    for page in reader.pages:
        txt = page.extract_text() or ""
        page_list.append(txt)
    return page_list


def extract_to_json(pdf_path: str, output_path: str, regulation: str) -> None:
    pages = load_pdf(pdf_path)
    records = []
    skipped = 0
    total_char = 0

    # loop over and build dict for each page
    for index, page_content in enumerate(pages):
        page_num = index + 1
        if not page_content.strip():
            skipped += 1
        else:
            records.append({
                "regulation": regulation,
                "page": page_num,
                "text": page_content
            })
            total_char += len(page_content)

    # Write records in the json
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=1)

    print("--- summary ---")
    print("Pages kept:", len(records))
    print("Pages skipped:", skipped)
    print("Total characters:", total_char)


if __name__ == "__main__":
    extract_to_json(PDF_PATH, OUTPUT_PATH, "gdpr")
