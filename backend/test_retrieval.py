from ingestion.vector_store import VectorDBManager
from Retrieval.retrieve import RagRetriever
from ingestion.embedding import EmbeddingManager


vector_store = VectorDBManager()
vector_store.load_vector_store()

embedding_manager = EmbeddingManager()

retriever = RagRetriever(
    vector_store=vector_store,
    embedding_manager=embedding_manager
)

query = "Who is the owner of Webenza?"

results = retriever.retrieve(
    query=query,
    top_k=20,
    score_threshold=0.0
)

print("\nQUERY:", query)
print("RESULT COUNT:", len(results))

for index, result in enumerate(results, start=1):
    print("\n==============================")
    print("RESULT:", index)
    print("SCORE:", result["similarity_score"])
    print("TITLE:", result["metadata"].get("title"))
    print("SOURCE:", result["metadata"].get("source"))
    print("DOCUMENT:")
    print(result["document"])