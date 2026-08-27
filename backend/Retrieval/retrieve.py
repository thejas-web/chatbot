


class RagRetriever():

    def __init__(self,vector_store, embedding_manager):
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager

    def retrieve(self, query:str,top_k:int = 20,score_threshold:float = 0.0):

        query_embedding = self.embedding_manager.embed_query(query)


        try:

            results = self.vector_store.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
                )

            #print(f"number of results retrieved: {len(results['documents'][0])}")
            #print(f"results: {results}")

            final_results = []
            if results["documents"] and results["documents"][0]:
                documents = results["documents"][0]
                metadatas = results["metadatas"][0]
                distances = results["distances"][0]
                ids = results["ids"][0]

                for i,(document,metadata,distance,id) in enumerate(zip(documents,metadatas,distances,ids)):

                    similarity_score = 1 - distance
                    if similarity_score >= score_threshold:
                        final_results.append({
                            "document": document,
                            "metadata": metadata,
                            "similarity_score": similarity_score,
                            "id": id
                        })
                return final_results
            else:
                print("No results found.")
                return []
        
        except Exception as e:
            print(f"Error during retrieval: {e}")
            return []
        
                

