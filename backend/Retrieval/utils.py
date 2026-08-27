def print_results(results: list[dict], query: str = None):
    if query:
        print(f"\nQuery: {query}")
    print(f"Found {len(results)} result(s)\n" + "=" * 80)

    for rank, r in enumerate(results, start=1):
        title = r["metadata"].get("title", "Untitled")
        source = r["metadata"].get("source", "N/A")
        score = r["similarity_score"]
        preview = r["document"].strip().replace("\n", " ")
        if len(preview) > 200:
            preview = preview[:200] + "..."

        print(f"[{rank}] {title}")
        print(f"    Score : {score:.3f}")
        print(f"    Source: {source}")
        print(f"    Text  : {preview}")
        print("-" * 80)