import os
import pandas as pd

def cut_tagged(text: str, idx: int) -> str:
    end_idx = text.find("]", idx)
    if end_idx == -1:
        print("not found end_idx")
        return text[idx:]

    return text[end_idx+1:].lstrip("\n ")


def cutter(text: str) -> str:
    marker = "[Текст песни"
    idx = text.find(marker)
    if idx != -1:
        return cut_tagged(text, idx)

    marker = "Lyrics"
    idx = text.find(marker)
    if idx == -1:
        print(f'not found Lyrics: {text[:50].replace('\n', ' ')}')
        return text

    return text[idx+len(marker)+1:]

def main():
    df = pd.read_parquet("data/kizaru_lyrics.parquet")

    df['lyrics'] = df['lyrics'].apply(cutter)

    out_parquet = os.path.join(
        os.path.dirname(__file__), "..", "data", "kizaru_lyrics_prepared.parquet"
    )
    df.to_parquet(out_parquet, index=False)


if __name__ == '__main__':
    main()
