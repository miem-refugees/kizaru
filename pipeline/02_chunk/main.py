import pandas as pd

def chunk_lyrics(lyrics, min_window=2, max_window=4):
    lines = [line.strip() for line in lyrics.split('\n') if line.strip()]

    chunks = []
    for window_size in range(min_window, max_window + 1):
        for i in range(len(lines) - window_size + 1):
            chunk = '\n'.join(lines[i:i+window_size])
            chunks.append(chunk)

    return chunks

def main():
    df = pd.read_parquet('data/01_kizaru_lyrics_preprocessed.parquet')
    assert df.shape[0] > 20

    result = []
    meta_cols = [col for col in df.columns if col != 'lyrics']

    for _, row in df.iterrows():
        chunks = chunk_lyrics(row['lyrics'])
        meta = {col: row[col] for col in meta_cols}
        for chunk in chunks:
            row = meta.copy()
            row['chunk'] = chunk
            result.append(row)


    chunked_df = pd.DataFrame(result)
    chunked_df.to_parquet('data/02_kizaru_lyrics_chunked.parquet', index=False)
    print(f"saved {chunked_df.shape[0]} rows")

if __name__ == '__main__':
    main()
