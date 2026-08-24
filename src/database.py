import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class TravelVectorDB:
    def __init__(self, collection_name = "travel_guides"):
        self.collection_name = collection_name
        self.client = QdrantClient(":memory:")
        self._init_collection()

    def _init_collection(self):
        """Creates the database collection if it doesn't already exist."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if not exists:
            self.client.create_collection(
                collection_name = self.collection_name,
                vectors_config = VectorParams(size = 1536, distance = Distance.COSINE),
            )
            print(f"Created collection: '{self.collection_name}' successfully")

    def add_travel_guide(self, doc_id: int, text_content: str, city: str, vector: list):
        """Inserts a chunk of travel guide text into the database with its embedding vector"""
        self.client.upsert(
            collection_name = self.collection_name,
            points = [
                PointStruct(
                    id = doc_id,
                    vector = vector,
                    payload = {
                        "text": text_content,
                        "city": city.lower()
                    }
                )
            ]
        )

    def search_guides(self, query_vector: list, city: str, limit=3) -> list:
        """Searches the database for the most contextually relevant travel snippets matching the destination."""
        import qdrant_client.models as models  # Import standard Qdrant models wrapper

        # This filter ensures we only scan documents matching the target city
        city_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="city",
                    match=models.MatchValue(value=city.lower())
                )
            ]
        )
        
        # Swapped old '.search()' method with the modern multi-dimensional '.query_points()' structure
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=city_filter,
            limit=limit
        )
        
        # Extract and return the raw text blocks to be injected into DSPy
        return [hit.payload["text"] for hit in results.points if hit.payload]



if __name__ == "__main__":
    db = TravelVectorDB()
    print("Qdrant database initialized and ready for embedding vectors")

    db.client.close()