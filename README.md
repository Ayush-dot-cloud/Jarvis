# Jarvis

A personal, voice-activated AI assistant written in Python — your own little Iron Man-style sidekick. Talk to it, and it talks back: opens apps and websites, plays music on YouTube, tells you the time, weather, news, looks things up on Wikipedia, controls volume, and answers freeform questions through OpenAI.

> Built for Windows (uses SAPI5 TTS and Windows-specific shortcuts), but degrades gracefully on macOS/Linux for most non-system features.

---

## Features

| Category | Example phrases |
| --- | --- |
| **Time / date** | "what is the time", "what's today's date" |
| **Open apps** | "open notepad", "open chrome", "open calculator" |
| **Open websites** | "open youtube", "open github", "open gmail" |
| **Search** | "search best python tutorials", "google weather in mumbai" |
| **Play media** | "play despacito", "play music lofi", "play marvel trailer" |
| **Wikipedia** | "wikipedia alan turing", "tell me about black holes", "who is elon musk" |
| **Weather** | "what's the weather", "weather in delhi" *(needs OpenWeather key)* |
| **News** | "tell me the news", "headlines" *(needs NewsAPI key)* |
| **System** | "volume up", "mute", "lock screen", "shutdown computer", "cancel shutdown" |
| **Fun** | "tell me a joke" |
| **Ask anything** | Any other question — routed to OpenAI |
| **Exit** | "goodbye", "stop jarvis", "go to sleep" |

---

## Quick start (Windows)

1. **Install Python 3.10+** from <https://www.python.org/downloads/windows/>. Tick **"Add Python to PATH"** during install.
2. Download / clone this repo into `C:\Users\gopal\OneDrive\Desktop\Jarvis` (or wherever you like).
3. Double-click **`run.bat`** — it will:
   - create a virtual environment (`.venv`),
   - install dependencies from `requirements.txt`,
   - copy `.env.example` to `.env` and open it in Notepad on first run.
4. Paste your **OpenAI API key** into `.env`:
   ```
   OPENAI_API_KEY=sk-...your-real-key...
   ```
   Get one at <https://platform.openai.com/api-keys>.
5. Re-run **`run.bat`**. Jarvis will greet you. Say:

   > **"Jarvis, what is the time?"**

That's it.

### If PyAudio fails to install

`PyAudio` ships pre-built wheels for most modern Python versions, but if the install fails:

```cmd
pip install pipwin
pipwin install pyaudio
```

---

## Manual setup (any OS)

```bash
git clone https://github.com/Ayush-dot-cloud/Jarvis.git
cd Jarvis
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # then edit .env and paste your OpenAI key
python -m jarvis
```

---

## Configuration (`.env`)

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | **yes** | — | Powers the "ask anything" brain |
| `OPENAI_MODEL` | no | `gpt-4o-mini` | Cheap + fast; try `gpt-4o` for higher quality |
| `OPENWEATHER_API_KEY` | optional | — | Enables weather skill |
| `DEFAULT_CITY` | no | `Pune` | Used when no city is named |
| `NEWS_API_KEY` | optional | — | Enables news skill |
| `WAKE_WORD` | no | `jarvis` | Set blank to react to every utterance |
| `VOICE_INDEX` | no | `0` | `0`/`1` to switch between male/female SAPI voices |
| `VOICE_RATE` | no | `185` | Words per minute; lower = slower |
| `MIC_CALIBRATION_SECONDS` | no | `1.0` | Ambient-noise calibration at startup |
| `USER_NAME` | no | `Sir` | How Jarvis addresses you |

---

## Project layout

```
Jarvis/
├── run.bat                # Windows quick-start launcher
├── requirements.txt
├── .env.example
├── jarvis/
│   ├── __main__.py        # `python -m jarvis`
│   ├── main.py            # main listen → route → speak loop
│   ├── config.py          # .env loading
│   ├── voice.py           # mic input + TTS output
│   ├── brain.py           # OpenAI client wrapper
│   ├── router.py          # intent matching
│   └── skills/
│       ├── info.py        # time, date, Wikipedia
│       ├── web.py         # open sites, Google, YouTube
│       ├── system.py      # apps, volume, lock, shutdown (Windows)
│       ├── media.py       # music shortcuts
│       └── utility.py     # jokes, weather, news
└── tests/
    └── test_router.py     # unit tests (run with `pytest`)
```

---

## How it works

1. **`voice.Listener`** records from the default microphone and uses Google's free web speech API for transcription.
2. **`main`** strips the wake word (default: `jarvis`) and hands the rest to **`router.Router`**.
3. The router matches keyword patterns against built-in skills (`time`, `weather`, `open …`, etc.). Anything that doesn't match falls through to…
4. **`brain.Brain`**, which sends the utterance to OpenAI with a "concise voice assistant" system prompt and the last few turns of conversation history.
5. The reply text is spoken via **`voice.Speaker`** (offline `pyttsx3` → Windows SAPI5).

To add a new skill, drop a function in `jarvis/skills/<your_skill>.py` and add a matcher in `jarvis/router.py::Router.handle`.

---

## Tests

```bash
pip install pytest
pytest -q
```

The router tests stub OpenAI and side-effecting OS calls, so they run without a network or microphone.

---

## Troubleshooting

- **"Failed to initialise microphone"** — make sure your mic is not muted in Windows Sound Settings, and that the Microphone privacy setting allows desktop apps.
- **No audio output** — open Windows Settings → System → Sound, set the default output device, then re-run.
- **Recognition is slow / hallucinates** — try a quieter room, or increase `MIC_CALIBRATION_SECONDS` to `2.0`.
- **OpenAI rate-limit / quota errors** — switch `OPENAI_MODEL` to `gpt-4o-mini` (already the default) and check your billing at <https://platform.openai.com/account/billing>.

---

## License

MIT — see [`LICENSE`](LICENSE).
