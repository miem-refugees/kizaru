import os
from qdrant_client import QdrantClient
from fastembed import SparseTextEmbedding
import time

from qdrant_client.http.models import models


COLLECTION_NAME = "kizaru_lyrics"
MODEL = "intfloat/multilingual-e5-small"


class VectorSearch:
    def __init__(self):
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY")
        )
        # sanity check
        self.client.info()

        self.embed_model = SparseTextEmbedding(
            model_name="Qdrant/bm42-all-minilm-l6-v2-attentions"
        )

    def search(self, text: str):
        start_time = time.time()

        sparse_vector_fe = list(self.embed_model.query_embed(text))[0]
        sparse_vector = models.SparseVector(
            values=sparse_vector_fe.values.tolist(),
            indices=sparse_vector_fe.indices.tolist(),
        )

        hits = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=sparse_vector,
            using="bm42",
            with_payload=True,
            limit=1,
        ).points

        if len(hits) == 0:
            return None

        hit = hits[0]

        result = f"{hit.payload['text']}\n\nⒸ {hit.payload['title']}"

        elapsed = time.time() - start_time
        result += f" ⏱ {elapsed:.2f}sec"

        return result
