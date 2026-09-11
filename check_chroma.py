import chromadb

client = chromadb.PersistentClient(
    path="data/vector_store"
)

collection = client.get_collection(
    name="documents"
)

print("Total documents:", collection.count())

data = collection.get(
    include=["documents", "metadatas"]
)

search_terms = [
    "puneet pahuja",
    "founder",
    "founder & ceo"
]

found = False

for index, document in enumerate(data["documents"]):
    text = document or ""

    if any(term in text.lower() for term in search_terms):
        found = True

        print("\n--- MATCH FOUND ---")
        print("Metadata:")
        print(data["metadatas"][index])

        print("\nDocument:")
        print(text[:4000])

if not found:
    print("\nNo founder/Webenza document was found in ChromaDB.")