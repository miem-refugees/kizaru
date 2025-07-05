import dotenv
import torch
import pandas as pd
from sentence_transformers import SentenceTransformer

MODEL = "intfloat/multilingual-e5-small"


def main():
    dotenv.load_dotenv()

    df = pd.read_parquet("data/02_kizaru_lyrics_chunked.parquet")
    assert df.shape[0] > 20

    if torch.cuda.is_available():
        device = "cuda"
    elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"

    print(f"Using device: {device}")
    model = SentenceTransformer(MODEL, device=device)
    print(f"Embedding with {MODEL}")

    embeddings = model.encode(df["text"].tolist(), show_progress_bar=True)
    df["embedding"] = embeddings.tolist()
    df.to_parquet("data/03_kizaru_lyrics_embedded.parquet", index=False)


if __name__ == "__main__":
    main()
