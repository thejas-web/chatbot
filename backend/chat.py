from Retrieval.retrieve import RagRetriever
from Retrieval.generate import RagGenerator
from ingestion.vector_store import VectorDBManager
from ingestion.embedding import EmbeddingManager
from Retrieval.utils import print_results

vector_db_manager = VectorDBManager()
vector_db_manager.load_vector_store()

embedding_manager = EmbeddingManager()




rag_retriever = RagRetriever(vector_db_manager, embedding_manager)
rag_generator = RagGenerator()  # reads GROQ_API_KEY from env, or pass api_key="..."

query = "What are some twitter analytics tool?"

results = rag_retriever.retrieve(query)
print_results(results, query)

# --- non-streaming ---
answer = rag_generator.generate(query, results)
print("\n=== Answer ===")
print(answer)

# --- streaming (uncomment to use instead) ---
# print("\n=== Answer (streaming) ===")
# for token in rag_generator.generate(query, results, stream=True):
#     print(token, end="", flush=True)
# print()