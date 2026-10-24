import yt_dlp
import os
from pathlib import Path
from mutagen.id3 import ID3, TIT2, TPE1, TALB, ID3NoHeaderError

download_folder = os.path.expanduser("~/Downloads")

if "com.termux" in os.environ.get("PREFIX", ""):
    download_folder = os.path.expanduser("~/storage/downloads")
else:
    download_folder = os.path.expanduser("~/Downloads")

def add_metadata(file_path, title, artist, album):
    try:
        tags = ID3(file_path)
    except ID3NoHeaderError:
        tags = ID3()

    tags.add(TIT2(encoding=3, text=title))
    tags.add(TPE1(encoding=3, text=artist))
    tags.add(TALB(encoding=3, text=album))

    tags.save(file_path)

def download_audio(url):
    options = {
    "format": "bestaudio/best",
    "outtmpl": str(download_folder / "%(title)s.%(ext)s"),

    "writethumbnail": True,

    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        },
        {
            "key": "FFmpegMetadata",
        },
        {
            "key": "EmbedThumbnail",
        },
    ],
}

    with yt_dlp.YoutubeDL(options) as downloader:
        info = downloader.extract_info(url, download=True)
        mp3_path = Path(downloader.prepare_filename(info)).with_suffix(".mp3")

    return mp3_path


def main():
    url = input("Enter video URL: ").strip()
    title = input("Enter song title: ").strip()
    artist = input("Enter artist name: ").strip()
    album = input("Enter album name: ").strip()

    try:
        mp3_path = download_audio(url)
        add_metadata(mp3_path, title, artist, album)

        print("Download complete!")
        print("Metadata added successfully!")

    except Exception as error:
        print(f"Something went wrong: {error}")


if __name__ == "__main__":
    main()