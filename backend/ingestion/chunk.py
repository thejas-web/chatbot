from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_docs(documents, chunk_size=1200, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    ) 

    chunked_docs = splitter.split_documents(documents)
    print(f"Chunked Documennts: {len(chunked_docs)}")
    print(chunked_docs)
    return chunked_docs
