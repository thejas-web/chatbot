import json
from pathlib import Path
from langchain_core.documents import Document

def load_pages_as_documents(combined_json_path: str) -> list[Document]:
    data = json.loads(Path(combined_json_path).read_text(encoding="utf-8"))
    documents = []
    for page in data:
        if page["char_count"] < 100:
            continue  # skip thin/empty pages
        doc = Document(
            page_content=page["text"],
            metadata={
                "source": page["url"],
                "title": page["title"],
            },
        )
        documents.append(doc)
    print(f"Loaded Documents: {len(documents)} \n {documents}")
    return documents
