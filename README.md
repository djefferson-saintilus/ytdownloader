# YouTube to MP3 Converter

A simple desktop application to download and convert YouTube videos (under 9 minutes) to MP3 audio files.  
Built with Python, Tkinter, [yt-dlp](https://github.com/yt-dlp/yt-dlp), and [moviepy](https://zulko.github.io/moviepy/).

*Author: Djefferson saintilus*

## Features

- Paste or drag-and-drop a YouTube link
- Downloads best available audio (videos under 9 minutes)
- Converts downloaded audio to MP3
- Progress bar and status updates
- Choose output folder for MP3 files
- Modern, dark-themed GUI

## Requirements

- Python 3.7+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [moviepy](https://zulko.github.io/moviepy/) (version 1.0.3 recommended)
- [tkinterdnd2](https://github.com/pmgagne/tkinterdnd2)

Install dependencies with:

```sh
pip install yt-dlp tkinterdnd2
pip install moviepy==1.0.3
```

## Usage

1. Run the application:

    ```sh
    python ytdownloader.py
    ```

2. Paste or drag a YouTube video link (must be less than 9 minutes).
3. Choose the output folder (default is `converted/`).
4. Click "Download & Convert".
5. The MP3 file will be saved in the selected folder.

## Files

- [`ytdownloader.py`](ytdownloader.py) — Main application script
- `icon.ico` — Application icon
- `converted/` — Default output folder for MP3 files

## Notes

- Only supports YouTube videos shorter than 9 minutes.
- Requires a working internet connection.
- Make sure all dependencies are installed.


## License

MIT LICENSE