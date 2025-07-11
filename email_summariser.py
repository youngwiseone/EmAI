import os, re, tempfile, html
from email import policy, parser

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from bs4 import BeautifulSoup
import extract_msg
import openai

# ─── env & OpenAI key ───────────────────────────────────
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY") or ""
if not openai.api_key:
    raise RuntimeError("OPENAI_API_KEY missing")

# ─── FastAPI + static ───────────────────────────────────
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def index():
    return FileResponse("static/index.html")

# ─── HTML → text helper ─────────────────────────────────
def clean_html_to_text(html_str: str) -> str:
    soup = BeautifulSoup(html_str, "html.parser")
    for t in soup(["style","script","head","meta","noscript"]): t.decompose()
    for br in soup.find_all("br"): br.replace_with("\n")
    for p in soup.find_all("p"):   p.insert_before("\n"); p.insert_after("\n")
    text = html.unescape(soup.get_text())
    text = re.sub(r"\r?\n\s*\n+", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

# ─── banner/footer scrubber ─────────────────────────────
def strip_banners_and_footer(text: str) -> str:
    lines = text.splitlines()

    # top banner
    if lines and "cyber" in lines[0].lower() and "safety" in lines[0].lower():
        idx = 1
        while idx < len(lines) and lines[idx].strip(): idx += 1
        while idx < len(lines) and not lines[idx].strip(): idx += 1
        lines = lines[idx:]

    # bottom Smartsheet footer
    keys = ("unsubscribe","©","privacy","report spam","provide feedback")
    for i,l in enumerate(lines):
        if any(k in l.lower() for k in keys):
            lines = lines[:i]
            break

    return "\n".join(l.rstrip() for l in lines).strip()

# ─── .eml / .msg parsers ───────────────────────────────
def parse_eml(raw: bytes):
    msg = parser.BytesParser(policy=policy.default).parsebytes(raw)
    part = msg.get_body(preferencelist=("plain","html"))
    body = part.get_content() if part and part.get_content_type()=="text/plain" \
           else clean_html_to_text(part.get_content() if part else "")
    body = strip_banners_and_footer(body or "")
    return msg["from"], msg["subject"] or "(no subject)", body or "(empty)"

def parse_msg(upload: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(upload.file.read()); tmp.flush()
        msg = extract_msg.Message(tmp.name)
    body = msg.body if msg.body else clean_html_to_text(msg.htmlBody or "")
    body = strip_banners_and_footer(body or "")
    return msg.sender or msg.sender_email, msg.subject or "(no subject)", body

# ─── GPT helper ─────────────────────────────────────────
def gpt_summary(text: str, prompt_header: str) -> str:
    prompt = f"{prompt_header}\n\n{text[:6000]}"
    resp   = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.3,max_tokens=120,
    )
    return resp.choices[0].message.content.strip()

# ─── API routes ─────────────────────────────────────────
@app.post("/parse")
async def parse_route(file: UploadFile):
    try:
        if file.filename.lower().endswith(".msg"):
            sender, subject, body = parse_msg(file)
        else:
            sender, subject, body = parse_eml(await file.read())
        return JSONResponse({"sender": sender, "subject": subject, "body": body})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/summarise")
async def summarise_route(text: str = Form(...), prompt: str = Form(...)):
    try:
        return JSONResponse({"summary": gpt_summary(text, prompt)})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)