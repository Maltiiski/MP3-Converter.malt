import yt_dlp
from pathlib import Path

download_folder = Path.home() / "Downloads"

def download_audio(url):
    options = {
        "format": "bestaudio/best",
        "outtmpl": str(download_folder / "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with yt_dlp.YoutubeDL(options) as downloader:
        downloader.download([url])


def main():
    url = input("Enter video URL: ").strip()

    try:
        download_audio(url)
        print("Download complete!")

    except Exception as error:
        print(f"Something went wrong: {error}")


if __name__ == "__main__":
    main()