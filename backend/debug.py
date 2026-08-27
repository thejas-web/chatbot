from ingestion.vector_store import VectorDBManager

vdb = VectorDBManager()
vdb.load_vector_store()

# 1. How many chunks total, and what distance space is the collection using?
print(f"Total chunks in collection: {vdb.collection.count()}")
print(f"Collection metadata: {vdb.collection.metadata}")

# 2. Pull EVERYTHING and check how many chunks come from /work/ pages
all_data = vdb.collection.get(include=["metadatas", "documents"])
work_chunks = [
    (meta.get("source"), meta.get("title"), doc[:80])
    for meta, doc in zip(all_data["metadatas"], all_data["documents"])
    if "/work/" in (meta.get("source") or "")
]

print(f"\nChunks from /work/ pages: {len(work_chunks)}")
for source, title, preview in work_chunks:
    print(f"  - {title} | {source}")
    print(f"    {preview}...")

# 3. Direct raw-text sanity check: does ANY chunk literally contain a known
#    client name? Replace 'Zolostays' with a client you know is in your data.
target = "Zolostays"
matches = [
    (meta.get("source"), doc[:120])
    for meta, doc in zip(all_data["metadatas"], all_data["documents"])
    if target.lower() in doc.lower()
]
print(f"\nChunks containing '{target}': {len(matches)}")
for source, preview in matches:
    print(f"  - {source}\n    {preview}...")

# 4. Where does that chunk rank for an explicit query, regardless of threshold?
if matches:
    from ingestion.embedding import EmbeddingManager
    embedding_manager = EmbeddingManager()
    query = f"Tell me about Webenza's work with {target}"
    query_embedding = embedding_manager.embed_query(query)

    results = vdb.collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=vdb.collection.count(),  # rank against EVERYTHING
        include=["metadatas", "distances"],
    )
    for rank, (meta, dist) in enumerate(zip(results["metadatas"][0], results["distances"][0]), start=1):
        if target.lower() in (meta.get("source") or "").lower():
            print(f"\n'{target}' chunk found at rank {rank}/{vdb.collection.count()} (distance={dist:.4f})")
            break
    else:
        print(f"\n'{target}' chunk never surfaced in the full ranked list — something's off in embedding, not just threshold.")