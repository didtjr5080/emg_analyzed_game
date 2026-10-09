# EMG Arm Wrestle

EMG Arm Wrestle is a Flask-based mock exercise game for experimenting with two-channel muscle activation. Biceps activation pushes the grip toward the opponent, while triceps activation reduces wobble. Push into the target zone and hold it there to earn points. A local photorealistic arena plate is combined with real-time Canvas-rendered arms and joints. It is a software prototype and does not produce medical measurements.

## Architecture

Input is isolated behind `EMGProvider`; `EMGProcessor` clamps and derives normalized values; `GameController` owns server-side state; Flask exposes that state; vanilla JavaScript renders the game and graphs. A future sensor provider can replace the mock provider without changing game rendering.

```text
Keyboard / Slider / MockEMGProvider
              -> EMGProcessor
              -> GameController
                -> Flask JSON API
              -> Canvas game and dashboard
```

## Directory structure

```text
emg_mock_game/
├── app.py                  Flask routes
├── config.py               thresholds and tuning
├── emg/                    provider abstraction and processor
├── game/                   state and controller
├── templates/index.html    game page
├── static/css/style.css    responsive dashboard
├── static/js/game.js       input, physics, rendering, graphs
└── tests/                  processor, controller, and API tests
```

## Installation and execution

Python 3.10 or later is required.

```bash
cd emg_mock_game
python -m pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>. The UI is designed for desktop at 1280×720 or larger and adapts to narrower screens.

## Controls and input modes

- **Keyboard:** `W`/`S` increase/decrease biceps and `D`/`A` increase/decrease triceps by 0.05.
- **Slider:** directly sets each channel from 0–100%.
- **Auto Mock:** generates alternating contraction cycles with small independent noise.
- **START / PAUSE / RESET:** controls elapsed time and play state. Reset clears score, fatigue, time, and the arm-wrestling round position.

All activation values are clamped to `0.0–1.0`. Biceps values below 40% are LOW, 40–70% are GOOD, and values above 70% are OVER.

## API

- `GET /` — game page
- `POST /api/emg` — update normalized activation, e.g. `{"biceps": 0.62, "triceps": 0.21, "input_mode": "slider"}`
- `GET /api/mock` — generate and process an automatic mock sample
- `GET /api/state` — current calculated and game state
- `POST /api/control` — `{"action": "start"}` or `{"action": "pause"}`
- `POST /api/score` — award 100 points while playing (called after browser collision detection)
- `POST /api/reset` — reset the session

## Mock fatigue disclaimer

The fatigue number is a game-only proxy. Sustained overall activation above 0.6 adds 0.005 per sample, while lower activation subtracts 0.003. It is not physiological fatigue analysis, a health assessment, or a medical-device output.

## Future EMG integration

Create an `ESP32EMGProvider`, `SerialEMGProvider`, or `FileEMGProvider` implementing `EMGProvider.get_sample()`. Sensor communication belongs only in that provider. A production pipeline can then add band-pass filtering, rectification, envelope/window extraction, RMS/MAV features, MVC normalization, and validated fatigue estimation before passing normalized activation into `EMGProcessor` and `GameController`.

Run tests with:

```bash
python -m pytest -q
```
