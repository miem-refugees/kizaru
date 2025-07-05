import re
import pandas as pd


def cut_tagged(text: str, idx: int) -> str:
    end_idx = text.find("]", idx)
    if end_idx == -1:
        print("not found end_idx")
        return text[idx:]

    return text[end_idx + 1 :].lstrip("\n ")


def cutter(text: str) -> str:
    marker = "[Текст песни"
    idx = text.find(marker)
    if idx != -1:
        return cut_tagged(text, idx)

    marker = "Lyrics"
    idx = text.find(marker)
    if idx == -1:
        print(f"not found Lyrics: {text[:50].replace('\n', ' ')}")
        return text

    return text[idx + len(marker) + 1 :]


def remove_brackets(text: str) -> str:
    # Remove well-formed [ ... ] blocks
    text = re.sub(r"\[.*?\]", "", text, flags=re.DOTALL)

    # Remove dangling open brackets and everything after
    text = re.split(r"\[", text)[0]

    # Remove dangling close brackets and everything before
    text = re.split(r"\]", text)[-1]

    # Strip leading/trailing newlines
    return text.strip("\n")


def remove_contrib(text: str) -> str:
    for i, word in enumerate(text):
        if "Contributors" in word:
            return " ".join(text[i + 1 :])

    return text


def main():
    df = pd.read_parquet("data/00_kizaru_lyrics.parquet")

    df["lyrics"] = df["lyrics"].apply(cutter)
    df["lyrics"] = df["lyrics"].apply(remove_brackets)
    df["lyrics"] = df["lyrics"].apply(remove_contrib)

    df.to_parquet("data/01_kizaru_lyrics_preprocessed.parquet", index=False)


if __name__ == "__main__":
    main()
