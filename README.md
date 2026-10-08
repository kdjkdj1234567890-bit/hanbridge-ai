# 🌉 HanBridge AI

**Korean ↔ English business communication agent** — built for the
[Nebius × NVIDIA Global AI Hackathon](https://nebiusglobalaihackathon.devpost.com/)
(Best Apps and Agents track).

HanBridge doesn't just translate — it **adapts tone across business cultures**.
Korean business writing is indirect, humble, and relationship-first; Western
business writing is direct, ownership-driven, and action-oriented. HanBridge
bridges that gap and *teaches* the user why, so every translation is also a
cross-cultural coaching moment.

Powered by **NVIDIA Nemotron** open models served on **Nebius Token Factory**.

## ✨ Features

| Mode | What it does |
|---|---|
| 🇰🇷 → 🇺🇸 Korean → English | Translates + adapts to Western business tone (1–5 strength slider), with tone adjustments & cultural notes |
| 🇺🇸 → 🇰🇷 English → Korean | Translates + applies Korean business etiquette (합니다체/해요체, honorifics), with etiquette notes |
| 💬 Live Chat | Slack/Teams-style real-time bilingual chat translation |

Every translation returns **coaching notes**: *what* changed in tone and *why*
it matters culturally — the feature that makes this an agent, not a dictionary.

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────────────┐      ┌─────────────────────────────┐
│  Streamlit  │─────▶│  hanbridge/llm.py    │─────▶│ Nebius Token Factory        │
│  app.py     │      │  (OpenAI-compatible) │      │ api.tokenfactory.nebius.com │
│  (UI x3)    │◀─────│  structured JSON out │◀─────│ NVIDIA Nemotron models      │
└─────────────┘      └──────────────────────┘      └─────────────────────────────┘
```

- **Frontend:** Streamlit (single container, Hugging Face Spaces-ready)
- **Inference:** NVIDIA Nemotron family via Nebius Token Factory
  (`https://api.tokenfactory.nebius.com/v1/`, OpenAI-compatible)
- **Output contract:** `response_format={"type": "json_object"}` with
  fence-tolerant fallback parsing (`hanbridge/llm.py::extract_json`)
- **Model selection:** the app queries the live `/v1/models` endpoint and
  prefers NVIDIA/Nemotron models — no hardcoded IDs to go stale

## 🚀 Quickstart

### 1. Get a Nebius Token Factory API key (free)

1. Sign up at https://tokenfactory.nebius.com/ — new accounts include
   promotional credits.
2. Hackathon builders: claim **$25 in credits** from the Devpost Resources
   page (code `NEBIUS-DEVPOST-GLOBAL26`).

### 2. Run locally

```bash
git clone https://github.com/kdjkdj1234567890-bit/hanbridge-ai.git
cd hanbridge-ai
pip install -r requirements.txt
cp .env.example .env   # then put your key in .env
export NEBIUS_API_KEY="v1...."   # or set it in .env
streamlit run app.py
```

Open http://localhost:8501 → paste your key in the sidebar → **Load available
models** → pick a Nemotron model → translate.

### 3. Run with Docker

```bash
docker build -t hanbridge-ai .
docker run -p 8501:8501 -e NEBIUS_API_KEY="v1...." hanbridge-ai
```

### 4. Deploy

- **Hugging Face Spaces:** create a Streamlit Space, push this repo, add
  `NEBIUS_API_KEY` as a Space secret.
- **Nebius AI Cloud:** the included `Dockerfile` deploys as-is to Nebius
  Serverless Endpoints / App hosting.

## 🧪 Tests (offline, no key needed)

```bash
python tests/test_smoke.py   # 10/10 passing
```

Tests cover JSON extraction robustness, prompt contracts, model auto-selection,
and the missing-key error path using a fake client — no network calls.

## 🎥 Demo

See [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for the 3-minute English demo video script.

## 📄 License

MIT — see [LICENSE](LICENSE).
