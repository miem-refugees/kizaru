import dotenv
import os
import pandas as pd

from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import PointStruct, PayloadSchemaType

collection_name = "kizaru_lyrics"


def ensure_collection_created(client: QdrantClient, vector_size: int):
    try:
        client.get_collection(collection_name)

        collection_info = client.get_collection(collection_name)
        existing_size = collection_info.config.params.vectors.size
        if existing_size != vector_size:
            raise RuntimeError(
                f"Mismatch collection vector size: existing: {existing_size}, input: {vector_size}"
            )

    except UnexpectedResponse:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE,
            ),
            # setting the HNSW m parameter to 0 disable index building entirely until enable it later
            hnsw_config=models.HnswConfigDiff(
                m=0,
            ),
            optimizers_config=models.OptimizersConfigDiff(
                indexing_threshold=0,
            ),
        )


def upload_vectors(client: QdrantClient, df: pd.DataFrame, batch_size: int = 512):
    payload_columns = [col for col in df.columns if col != "embedding"]

    num_rows = df.shape[0]
    for start in range(0, num_rows, batch_size):
        end = min(start + batch_size, num_rows)
        batch = df.iloc[start:end]
        points = []
        for idx, row in batch.iterrows():
            payload = {col: row[col] for col in payload_columns if pd.notna(row[col])}
            points.append(
                PointStruct(id=int(idx), vector=row["embedding"], payload=payload)
            )

        client.upsert(collection_name=collection_name, points=points, wait=True)
        print(f"Uploaded {end} / {num_rows} vectors")


def setup_indices(client: QdrantClient):
    print("getting back optimizer and hnsw build")
    client.update_collection(
        collection_name=collection_name,
        hnsw_config=models.HnswConfigDiff(
            m=16,
        ),
        optimizer_config=models.OptimizersConfigDiff(indexing_threshold=20000),
    )

    print("creating indices")
    client.create_payload_index(
        collection_name=collection_name,
        field_name="text",
        field_schema=PayloadSchemaType.TEXT,
    )


def main():
    dotenv.load_dotenv()

    df = pd.read_parquet("data/03_kizaru_lyrics_embedded.parquet")
    assert df.shape[0] > 20

    client = QdrantClient(
        url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY")
    )
    print(client.info())

    ensure_collection_created(client, df.embedding.iloc[0].shape[0])

    upload_vectors(client, df)

    setup_indices(client)


if __name__ == "__main__":
    main()
