from pypdf import PdfReader

FILE_PATH = "data/raw/gdpr.pdf"


def load_pdf(file_path: str) -> list[str]:
    page_list = []
    reader = PdfReader(file_path)
    for page in reader.pages:
        txt = page.extract_text() or ""
        page_list.append(txt)
    return page_list


if __name__ == "__main__":
    pages = load_pdf(FILE_PATH)
    page_count = len(pages)

    print("total page count", page_count)

    print("First 500 character for page 1\n")
    p1_500 = pages[0][0:500]
    print(p1_500)

    print("-" * 40)
    print("First 500 character for page 20\n")
    p20_500 = pages[19][0:500]
    print(p20_500)
