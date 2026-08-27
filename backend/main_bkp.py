from backend.ingestion.scrape import main
from backend.ingestion.load import load_pages_as_documents
from backend.ingestion.chunk import split_docs
from backend.ingestion.embedding import EmbeddingManager
from backend.ingestion.vector_store import VectorDBManager
from backend.config import ALL_PAGES_JSON
from backend.Retrieval.retrieve import RagRetriever
from backend.Retrieval.utils import print_results


scraped_pages = main()


docs = load_pages_as_documents(ALL_PAGES_JSON)


chunked_docs = split_docs(docs)

embedding_manager = EmbeddingManager()

embedded_docs = embedding_manager.generate_embedding(chunked_docs)

vector_db_manager = VectorDBManager()
vector_db_manager.load_vector_store()


vector_db_manager.add_documents(chunked_docs, embedded_docs)
print("Ingestion completed successfully.")

'''
retriever = RagRetriever(vector_db_manager, embedding_manager)

retrieved_docs = retriever.retrieve("Where is Webenza headquartered?", top_k=5, score_threshold=0.5)



response = print_results(retrieved_docs, "Where is Webenza headquartered?")

print(response)
'''