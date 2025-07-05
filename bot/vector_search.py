import os
import logging
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import torch
import time


COLLECTION_NAME = "kizaru_lyrics"
MODEL = "intfloat/multilingual-e5-small"


class VectorSearch:
    def __init__(self):
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY")
        )
        # sanity check
        self.client.info()

        if torch.cuda.is_available():
            device = "cuda"
        elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"

        logging.debug("using device: {} and model", device, MODEL)
        self.embed_model = SentenceTransformer(MODEL, device=device)

    def search(self, text: str):
        start_time = time.time()

        embedding = self.embed_model.encode(
            text,
            prompt="query: ",
            show_progress_bar=False,
        )

        hit = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=embedding,
            limit=1,
        ).points[0]

        result = f"{hit.payload['text']}\n\nⒸ {hit.payload['title']}"

        elapsed = time.time() - start_time
        result += f" ⏱ {elapsed:.2f}sec"

        return result
