# Video Analyzer with Google Cloud & Gemini

This is a Python project for automatic video analysis, generating a `.txt` file with timestamps, audio transcription (via Faster Whisper), and detailed visual descriptions (via Gemini 2.0 Flash or compatible models).  
It is recommended for multimodal summarization of videos such as meetings, lectures, interviews, and more.

## Prerequisites

- Google Cloud account with access to the Gemini 2.0 Flash model (or similar)
- Service Account key (JSON format)
- Python 3.8 or higher
- ffmpeg installed on the system  
  - Linux: `sudo apt install ffmpeg`  
  - macOS: `brew install ffmpeg`
- Python dependencies listed in `requirements.txt`

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

### Service Key

Place your Service Account JSON key file in:

```
credentials/key.json
```

### Videos

Add your video files to the directory:

```
videos/
```

Example: `videos/video1.mp4`

### Main Script

Edit `main.py` to set the video path and output filename as needed.

## Usage

```bash
python main.py
```

The result will be saved as `video1_resultado.txt` (or equivalent filename) in the project root.

## Folder Structure

```
ANALYZER/
├── credentials/
│   └── key.json
├── venv/
├── videos/
│   └── video1.mp4
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
└── video1_resultado.txt
```

## Notes

- Execution time may vary depending on your Gemini API quota.
- The `interval` parameter in `main.py` defines the frequency of visual analysis (in seconds).
- Audio transcription is performed locally with Faster Whisper, without file size limitations.
- Credential files and `.txt` output files are included in `.gitignore` for security.
- To process another video, simply change the configured path in the script.

## Technologies

- Python
- Google Cloud (Gemini 2.0 Flash)
- Faster Whisper
- ffmpeg
