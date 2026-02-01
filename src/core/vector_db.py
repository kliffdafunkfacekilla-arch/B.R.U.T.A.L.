import os
import json
from typing import List, Any, Optional, Dict
import chromadb
from chromadb.utils import embedding_functions

class LoreVectorDB:
    """
    Manages the vector database for lore fragments using ChromaDB and Sentence Transformers.
    """
    def __init__(self, persistence_path: Optional[str] = "./data/vector_store", collection_name: str = "lore"):
        """
        Initialize the ChromaDB client and collection.
        If persistence_path is None, use in-memory client.
        """
        if persistence_path:
            # Ensure the directory exists
            os.makedirs(persistence_path, exist_ok=True)
            self.client = chromadb.PersistentClient(path=persistence_path)
        else:
            self.client = chromadb.Client()

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
        Stores the full object as JSON in metadata.
        """
        ids = []
        documents = []
        metadatas = []

        for fragment in fragments:
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

            # Serialize the full fragment
            if hasattr(fragment, "model_dump_json"):
                json_str = fragment.model_dump_json()
            else:
                # Fallback if it's a dict or other object
                try:
                    # If it's a dict, use it directly
                    if isinstance(fragment, dict):
                         json_str = json.dumps(fragment)
                    else:
                        # Best effort: dump what we know
                        json_str = json.dumps({
                            "id": f_id, "content": f_content,
                            "category": f_category, "tags": f_tags
                        })
                except:
                     json_str = "{}"

            metadatas.append({
                "category": f_category,
                "tags": ",".join(f_tags),
                "json_data": json_str
            })

        if ids:
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )

    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Search for relevant lore fragments by semantic similarity.
        Returns a list of dicts (parsed from stored JSON).
        """
        count = self.collection.count()
        if count == 0:
            return []

        n_results = min(n_results, count)

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        found_fragments = []
        # results['metadatas'] is a list of lists (one per query)
        if results and results['metadatas']:
            metas_list = results['metadatas'][0]
            for meta in metas_list:
                json_data = meta.get("json_data")
                if json_data:
                    try:
                        obj = json.loads(json_data)
                        found_fragments.append(obj)
                    except:
                        pass

        return found_fragments

    def reset(self):
        """
        Clears the collection. Useful for testing or re-indexing.
        """
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            embedding_function=self.embedding_fn
        )
