# Listen-to-Son: TikTok Freeze + Subtitle Tool

A desktop application for creating TikTok-style videos with custom freeze effects and karaoke/line-by-line subtitles, powered by AI transcription and flexible video editing features.

## Features

- **TikTok Freeze Effect:** Automatically freeze the last two seconds of your MP4 video and overlay audio from a TikTok URL.
- **AI-Powered Transcription:** Uses [faster-whisper](https://github.com/guillaumekln/faster-whisper) to transcribe both the main video and TikTok audio, generating word-level timestamps.
- **Subtitle Modes:** 
  - *Line-by-Line*: Adds subtitles grouped by lines.
  - *Karaoke*: Animates subtitles word-by-word with customizable highlight and background colors.
- **Customizable Output:** 
  - Choose subtitle font size and word count per line.
  - Select colors for word, highlight, and outline via a GUI.
- **Preview and Export:** Preview your video before exporting. Exported videos are saved in the `output/` folder with dynamic filenames.
- **Logging & Progress:** Real-time progress bar and log output for transparency and troubleshooting.

## How It Works

1. **Select an MP4 File:** Pick a video to edit.
2. **Enter TikTok URL:** Paste the TikTok audio source.
3. **Choose Subtitle Mode & Style:** Set subtitle mode, font size, max words per line, and colors.
4. **Run or Preview:** Process the video, preview the result, and export when satisfied.

## Installation

### Requirements

- Python 3.8+
- FFmpeg
- The following Python packages:
  - PyQt6
  - moviepy
  - faster-whisper
  - yt-dlp

Install dependencies with:

```bash
pip install PyQt6 moviepy faster-whisper yt-dlp
```

Make sure `ffmpeg` is installed and available in your PATH.

### Running

```bash
python app.py
```

The application will launch a GUI.

## Usage

1. **Select MP4:** Click "Select MP4" to pick your video.
2. **Enter TikTok URL:** Paste a TikTok link for the audio overlay.
3. **Adjust Settings:** Modify subtitle mode, font size, words per line, and colors.
4. **Run:** Click "Run" to process and export the video.
5. **Preview Output:** Use "Preview Output" to view the result.

## Output

- Processed videos are saved as `output/{FIRST-THREE-WORDS}.mp4` based on the TikTok audio.
- Temporary files are cleaned up after export.

## Advanced Options

- **Color Selection:** Use the built-in color pickers for word, highlight, and outline colors.
- **Logging:** All actions and warnings appear in the log box for debugging and tracking process steps.

## License

MIT License

---

*Made with ❤️ by [leksautomate](https://github.com/leksautomate).*
