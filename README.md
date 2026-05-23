# Jarvis

A personal, voice-activated AI assistant written in Python.

## Features

- **Voice Recognition** – Listens to your microphone and converts speech to text via Google Speech API.
- **Text-to-Speech** – Responds with a natural-sounding voice using `pyttsx3`.
- **Wake Word** – Activates only when you say *"Jarvis"*.
- **Time & Date** – Tells the current time and date.
- **Weather** – Fetches live weather using OpenWeatherMap API.
- **Wikipedia Search** – Quick summaries from Wikipedia.
- **Web Browsing** – Opens Google, YouTube, GitHub, Gmail, WhatsApp, etc.
- **Google Search** – Searches Google from your voice.
- **YouTube Playback** – Searches and plays videos on YouTube.
- **App Launcher** – Opens Notepad, Calculator, Paint, CMD, Explorer, Task Manager.
- **System Info** – Reports OS, machine, and Python version.
- **Jokes** – Tells programming jokes.

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Ayush-dot-cloud/Jarvis.git
cd Jarvis

# 2. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run Jarvis
python main.py
```

## Configuration

Set optional environment variables before running:

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key (for future LLM integration) |
| `WEATHER_API_KEY` | [OpenWeatherMap](https://openweathermap.org/api) API key |

All settings can be tuned in `jarvis/config.py`.

## Project Structure

```
Jarvis/
├── main.py               # Entry point
├── requirements.txt      # Python dependencies
├── .gitignore
├── README.md
└── jarvis/
    ├── __init__.py
    ├── config.py          # Settings & constants
    ├── speech.py          # TTS & speech recognition
    ├── commands.py        # Command handlers & router
    ├── assistant.py       # Core listen-respond loop
    └── utils.py           # Logging setup
```

## Voice Commands

| Say | Action |
|---|---|
| *"Jarvis, what time is it?"* | Tells the current time |
| *"Jarvis, what's the date?"* | Tells today's date |
| *"Jarvis, weather in Mumbai"* | Current weather for Mumbai |
| *"Jarvis, search Wikipedia Python"* | Wikipedia summary |
| *"Jarvis, open YouTube"* | Opens YouTube in browser |
| *"Jarvis, play lo-fi music"* | Searches YouTube |
| *"Jarvis, google machine learning"* | Google search |
| *"Jarvis, open notepad"* | Launches Notepad |
| *"Jarvis, tell me a joke"* | Programming joke |
| *"Jarvis, system info"* | Shows system details |
| *"Jarvis, goodbye"* | Exits the assistant |

## License

MIT
