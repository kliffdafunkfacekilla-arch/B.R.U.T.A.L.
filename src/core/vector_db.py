import os
from typing import List, Any, Dict
import chromadb
from chromadb.utils import embedding_functions

class LoreVectorDB:
    """
    Manages the vector database for lore fragments using ChromaDB and Sentence Transformers.
    """
    def __init__(self, persistence_path: str = "./data/vector_store", collection_name: str = "lore"):
        """
        Initialize the ChromaDB client and collection.
        """
        # Ensure the directory exists
        os.makedirs(persistence_path, exist_ok=True)

        self.client = chromadb.PersistentClient(path=persistence_path)

        # Use a lightweight, effective model for embeddings
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )

    def index_lore(self, fragments: List[Any]):
        """
        Upsert lore fragments into the vector database.
        Expects objects with 'id', 'content', 'category', and 'tags' attributes.
        """
        ids = []
        documents = []
        metadatas = []

        for fragment in fragments:
            # Handle both Pydantic models and dicts if necessary,
            # but assuming Pydantic models based on usage.
            f_id = getattr(fragment, "id", None)
            f_content = getattr(fragment, "content", "")
            f_category = getattr(fragment, "category", "general")
            f_tags = getattr(fragment, "tags", [])

            if f_id is None:
                continue

            ids.append(f_id)

            # Enrich the document text with tags for better semantic matching
            text_content = f"{f_content} | Tags: {', '.join(f_tags)}"
            documents.append(text_content)

            metadatas.append({
                "category": f_category,
                "tags": ",".join(f_tags)
            })

        if ids:
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )

    def search(self, query: str, n_results: int = 5) -> List[str]:
        """
        Search for relevant lore fragments by semantic similarity.
        Returns a list of fragment IDs.
        """
        # Handle case where collection is empty or small
        count = self.collection.count()
        if count == 0:
            return []

        n_results = min(n_results, count)

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        # results['ids'] is a list of lists (one per query)
        if results and results['ids']:
            return results['ids'][0]

        return []

    def reset(self):
        """
        Clears the collection. Useful for testing or re-indexing.
        """
        # ChromaDB doesn't have a direct clear, so we delete and recreate or delete items.
        # But for this scope, let's just delete all items if we can list them,
        # or easier: delete the collection and recreate.
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            embedding_function=self.embedding_fn
        )
