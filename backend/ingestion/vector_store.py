import chromadb
from chromadb.config import Settings
import uuid
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import VECTOR_STORE_DIR

class VectorDBManager():

    def __init__(self,persist_directory:str = VECTOR_STORE_DIR,collection_name:str = "documents"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory

        self.client = None
        self.collection = None

    def load_vector_store(self):
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            

            self.collection = self.client.get_or_create_collection(name=self.collection_name,
                                                                   metadata={"description": "RAG Documents for chatbot",
                                                                             "hnsw:space": "cosine"
                                                                            }
                                                                  )
        except Exception as e:
            print(f"error occured: {e}")


    def add_documents(self,docs:list[dict], embeddings):

        if len(docs) != len(embeddings):
            raise ValueError("The number of documents and embeddings must be the same.")

        ids = []
        metadatas = []
        documents = []
        ebeddings = []


        for i,(doc,embedding) in enumerate(zip(docs,embeddings)):
            doc_id = f"doc_{uuid.uuid4().hex[:8]}_{i}"
            ids.append(doc_id)

            meta_data = dict(doc.metadata)
            meta_data["doc_index"] = i
            meta_data["content_length"] = len(doc.page_content)
            metadatas.append(meta_data)

            documents.append(doc.page_content)
            ebeddings.append(embedding.tolist())
        try:
            self.collection.add(
                ids=ids,
                metadatas=metadatas,
                documents=documents,
                embeddings=ebeddings
            )
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
        