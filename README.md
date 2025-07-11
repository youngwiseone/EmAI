# EmAI – Email Helper ✉️🤖

Drag-and-drop an `.eml` or `.msg` file, tweak the body, choose your prompt,
and EmAI will send the text to OpenAI and return a clean summary.

<p align="center">
  <img src="docs/demo.gif" width="650" alt="Demo GIF"/>
</p>

---

## Features

* **Drag & drop** Outlook/Gmail exports (`.eml`, `.msg`)
* Strips marketing footers & cyber-banner headers
* Edit before you send to the model
* Three prompt presets & custom prompt
* Progress bar while GPT is thinking
* Runs on **FastAPI + Uvicorn**, no DB required

---

## Quick-start (local)

### 1  Clone

```bash
git clone https://github.com/youngwiseone/emai.git
cd emai
```

### 2  Python 3.9+ & virtual-env

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install --upgrade pip
```

### 3  Install dependencies

```bash
pip install -r requirements.txt
```

<details>
<summary>Or install manually</summary>

```bash
pip install fastapi uvicorn[standard] python-dotenv \
            extract_msg beautifulsoup4 openai
```
</details>

### 4  Add your `.env`

Create a file named **`.env`** in the project root:

```dotenv
# .env
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

> *You need an OpenAI API key with GPT-4o access.  
> Sign in → https://platform.openai.com/account/api-keys → create key.*

### 5  Run the server

```bash
uvicorn email_summariser:app --reload --port 8000
```

Open <http://localhost:8000> and start dragging emails.

*Swagger docs*: <http://localhost:8000/docs>

---

## Production deploy

* **Single VM**: see `docs/lightsail.md` for an AWS Lightsail walk-through  
  (Gunicorn + Caddy with auto-HTTPS).  
* **Docker**: coming soon in `docker-compose.yml`.

---

## Roadmap

- [ ] Direct Outlook Graph API fetch (no file needed)  
- [ ] OAuth login & per-user key quota  
- [ ] Multiple language models (Gemini 1.5, Claude 3)

PRs welcome! ✨
