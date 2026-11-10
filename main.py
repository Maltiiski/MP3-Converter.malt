import os
import shutil
import subprocess
from pathlib import Path

import yt_dlp
from yt_dlp.utils import DownloadError
from mutagen.id3 import ID3, TIT2, TPE1, TALB, ID3NoHeaderError

IS_TERMUX = "com.termux" in os.environ.get("PREFIX", "")

COOKIES_FILE = Path(__file__).resolve().parent / "cookies.txt"

if IS_TERMUX:
    download_folder = Path("/storage/emulated/0/Download")
    if not download_folder.exists():
        raise SystemExit("Storage not accessible. Run: termux-setup-storage")
else:
    download_folder = Path.home() / "Downloads"
    download_folder.mkdir(parents=True, exist_ok=True)

if not shutil.which("ffmpeg"):
    hint = "pkg install ffmpeg" if IS_TERMUX else "sudo apt install ffmpeg"
    raise SystemExit(f"ffmpeg not found. Install it with: {hint}")


def add_metadata(file_path, title, artist, album):
    try:
        tags = ID3(file_path)
    except ID3NoHeaderError:
        tags = ID3()

    tags.add(TIT2(encoding=3, text=title))
    tags.add(TPE1(encoding=3, text=artist))
    tags.add(TALB(encoding=3, text=album))

    tags.save(file_path, v2_version=3)


def scan_media(file_path):
    """Tell Android's media library about the new file (Termux only)."""
    if not IS_TERMUX:
        return
    try:
        subprocess.run(["termux-media-scan", str(file_path)], check=False)
    except FileNotFoundError:
        print("Tip: run 'pkg install termux-api' so files show up in your music app.")


def download_audio(url):
    options = {
        "format": "bestaudio/best",
        "outtmpl": str(download_folder / "%(title)s.%(ext)s"),
        "writethumbnail": True,
        "noplaylist": True,
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"},
            {"key": "FFmpegThumbnailsConvertor", "format": "jpg", "when": "before_dl"},
            {"key": "FFmpegMetadata"},
            {"key": "EmbedThumbnail"},
        ],
    }

    if not shutil.which("deno") and shutil.which("node"):
        options["js_runtimes"] = {"node": {}}

    if COOKIES_FILE.exists():
        options["cookiefile"] = str(COOKIES_FILE)

    with yt_dlp.YoutubeDL(options) as downloader:
        info = downloader.extract_info(url, download=True)
        try:
            mp3_path = Path(info["requested_downloads"][0]["filepath"])
        except (KeyError, IndexError):
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
        scan_media(mp3_path)

        print("Download complete!")
        print("Saved to:", mp3_path)

    except DownloadError as error:
        message = str(error)
        print(f"Download failed: {message}")
        if "not a bot" in message or "429" in message:
            print("\nYouTube is blocking the request. Try:")
            print("  1. pip install -U --pre 'yt-dlp[default]'")
            print("  2. Install a JS runtime (Termux: pkg install nodejs)")
            print(f"  3. Export your YouTube cookies to: {COOKIES_FILE}")
            print("  4. Switch networks (Wi-Fi <-> mobile data) or wait a bit")
    except Exception as error:
        print(f"Something went wrong: {error}")


if __name__ == "__main__":
    main()