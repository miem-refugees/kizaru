import os
import pandas as pd
import argparse
from datetime import datetime
import dotenv
from lyricsgenius import Genius

artist_name = "kizaru"


def fetch_artist_songs(max_songs: int) -> pd.DataFrame:
    genius = Genius(os.getenv("GENIUS_ACCESS_TOKEN"))
    artist = genius.search_artist(artist_name, max_songs=1)
    if not artist:
        raise ValueError(f"Artist '{artist_name}' not found.")

    page = 1
    songs = []

    try:
        while page and len(songs) < max_songs:
            print(f"==PAGE {page}==")

            request: dict = genius.artist_songs(
                artist.id,
                per_page=50,
                page=page,
            )

            for meta in request["songs"]:
                print(meta["title"])
                song = genius.search_song(song_id=meta["id"], get_full_info=False)
                if song is None or song.lyrics is None or len(song.lyrics) < 30:
                    print(f"Skipping song {meta['title']}")
                    continue

                release_date = None
                if meta.get("release_date_components"):
                    release_date = datetime(
                        meta["release_date_components"].get("year", 0) or 1,
                        meta["release_date_components"].get("month", 0) or 1,
                        meta["release_date_components"].get("day", 0) or 1,
                    )

                songs.append(
                    {
                        "id": song.id,
                        "title": song.title,
                        "url": song.url,
                        "thumbnail_url": song.song_art_image_thumbnail_url,
                        "lyrics": song.lyrics,
                        "album_id": song.album.id if song.album else None,
                        "album_name": song.album.name if song.album else None,
                        "album_url": song.album.url if song.album else None,
                        "release_date": release_date,
                    }
                )

            if not request.get("next_page"):
                break

            page = request["next_page"]

    except Exception as e:
        print(f"got exception: {e}, saving {len(songs)} songs")

    return pd.DataFrame(songs)


def main():
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser(description="Create a dataset from Genius lyrics.")
    parser.add_argument(
        "--max-songs", type=int, default=500, help="Max number of songs to fetch"
    )
    args = parser.parse_args()

    df = fetch_artist_songs(args.max_songs)
    print("sample:\n", df.head())

    df.to_parquet("data/00_kizaru_lyrics.parquet", index=False)

    print(f"saved {df.shape[0]} songs")


if __name__ == "__main__":
    main()
