import os
import pandas as pd
import argparse
import dotenv
from lyricsgenius import Genius


def fetch_artist_songs(artist_name: str, max_songs: int = 200) -> pd.DataFrame:
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
                sort="popularity",
                per_page=50,
                page=page,
            )

            for meta in request["songs"]:
                print(meta["title"])
                song = genius.search_song(song_id=meta["id"], get_full_info=False)
                if song is None or song.lyrics is None or len(song.lyrics) < 30:
                    print(f"Skipping song {meta['title']}")
                    continue

                songs.append(
                    {
                        "id": song.id,
                        "title": song.title,
                        "url": song.url,
                        "thumbnail_url": song.song_art_image_thumbnail_url,
                        "lyrics": song.lyrics,
                        "album_id": song.album.id if song.album else None,
                        "album_name": song.album.name if song.album else None,
                        "album_release_date": song.album.release_date_components
                        if song.album
                        else None,
                        "album_url": song.album.url if song.album else None,
                    }
                )

            page = request["next_page"]

    except Exception as e:
        print(f"got exception: {e}, saving {len(songs)} songs")

    return pd.DataFrame(songs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a dataset from Genius lyrics.")
    parser.add_argument(
        "--artist", type=str, default="kizaru", help="Artist name to fetch"
    )
    parser.add_argument(
        "--max-songs", type=int, default=1000, help="Max number of songs to fetch"
    )
    args = parser.parse_args()

    df = fetch_artist_songs(args.artist, args.max_songs)
    print("sample:\n", df.head())

    out_parquet = os.path.join(
        os.path.dirname(__file__), "..", "data", f"{args.artist}_lyrics.parquet"
    )
    df.to_parquet(out_parquet, index=False)

    print(f"saved {df.shape[0]} {args.artist} songs")


if __name__ == "__main__":
    dotenv.load_dotenv()

    main()
