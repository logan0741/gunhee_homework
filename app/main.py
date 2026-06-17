import logging
import traceback
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.issue import create_github_issue
from app.spam import check_spam, get_model_version, reload_model


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(filename)s:%(lineno)d (%(funcName)s) | "
        "%(message)s"
    ),
)
logger = logging.getLogger("spamcheck")


class ClassifyRequest(BaseModel):
    text: str


class ClassifyResponse(BaseModel):
    label: str
    score: float


BASE_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="SpamCheck Web")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
def home():
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.post("/classify", response_model=ClassifyResponse)
async def classify(payload: ClassifyRequest):
    text = payload.text
    logger.info("CALL /classify | text='%s' | len=%s", text, len(text))

    try:
        if text == "crash":
            raise RuntimeError("의도적 장애 추가")

        label, score = check_spam(text)
        logger.info("OK /classify | model=%s | label=%s score=%s",
                    get_model_version(), label, score)
        return {"label": label, "score": score}

    except Exception as exc:
        logger.exception(
            "FAIL /classify | text='%s' | error=%s: %s",
            text,
            type(exc).__name__,
            exc,
        )
        tb = traceback.format_exc()
        title = f"[Prod Error] /classify failed: {type(exc).__name__}"
        body = (
            "## Summary\n"
            f"- endpoint: /classify\n"
            f"- input(text, short): `{text}`\n"
            f"- input length: {len(text)}\n\n"
            "## Exception\n"
            f"- type: {type(exc).__name__}\n"
            f"- message: {exc}\n\n"
            "## Traceback (line info)\n"
            f"```text\n{tb}\n```"
        )
        create_github_issue(title, body, logger)
        return {"label": "error", "score": -1.0}


@app.get("/model/info")
def model_info():
    version = get_model_version()
    logger.info("CALL /model/info | version=%s", version)
    return JSONResponse({"model_version": version})


@app.post("/model/reload")
def model_reload():
    version = reload_model()
    logger.info("CALL /model/reload | new_version=%s", version)
    return JSONResponse({"model_version": version, "status": "reloaded"})
