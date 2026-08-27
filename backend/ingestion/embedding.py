import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Tuple


class EmbeddingManager:

    def __init__(self):
        self.model_name = "intfloat/e5-small-v2"
        self.model = SentenceTransformer(self.model_name)

    def generate_embedding(self, documents):

        texts = []

        for doc in documents:

            title = doc.metadata.get("title", "")

            embedding_text = f"""
Title: {title}

Content:
{doc.page_content}
""".strip()

            texts.append("passage: " + embedding_text)

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        print(f"Generated Embeddings: {len(embeddings)}")

        return embeddings

    def embed_query(self, query):

        query = "query: " + query

        return self.model.encode(
            query,
            normalize_embeddings=True
        )

    
'''
class EmbeddingManager:

    def __init__(self):
        self.model_name = "BAAI/bge-small-en-v1.5"
        self.model = SentenceTransformer(self.model_name)

    def generate_embedding(self, documents):

        texts = []

        for doc in documents:

            title = doc.metadata.get("title", "")

            embedding_text = f"""
Title: {title}

Content:
{doc.page_content}
""".strip()

            texts.append(embedding_text)

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        print(f"Generated Embeddings: {len(embeddings)}")

        return embeddings

    def embed_query(self, query):

        query = (
            "Represent this sentence for searching relevant passages: "
            + query
        )

        return self.model.encode(
            query,
            normalize_embeddings=True
        )
'''

'''
class EmbeddingManager():

    def __init__(self, model_name="all-MiniLM-L6-v2"):

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def generate_embedding(self, documents):

        texts = []

        for doc in documents:

            title = doc.metadata.get("title", "")
            source = doc.metadata.get("source", "")

            embedding_text = f"""
Title: {title}
Source: {source}

Content:
{doc.page_content}
""".strip()

            texts.append(embedding_text)

        embeddings = self.model.encode(
            texts,
            show_progress_bar=True
        )

        print(
            f"Generated Embeddings: {len(embeddings)}"
        )

        return embeddings

    def embed_query(self, query):

        return self.model.encode(query)

'''