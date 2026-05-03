import logging
import traceback
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.issue import create_github_issue
from app.spam import check_spam


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
	score: int


BASE_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = BASE_DIR / "static"


# FastAPI 기반 웹 앱 생성
# /docs (Swagger UI)에 표기되는 이름
app = FastAPI(title="SpamCheck Web")
# 정적 HTML 서빙: static 안에 파일들을 URL로 접근가능하게 해라
# {URL}/static/…… 으로 접근 가능하게
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# 메인 페이지 (/) 처리 : “/”로 접속 시 처리할 작업
@app.get("/", response_class=HTMLResponse)
def home():
	return (STATIC_DIR / "index.html").read_text(encoding="utf-8")
# classify 요청이 올 때 할 일
# async: 비동기 처리 (서버가 요청 기다리는 동안 다른 요청도 처리 가능
@app.post("/classify", response_model=ClassifyResponse)
async def classify(payload: ClassifyRequest):
	text = payload.text
	logger.info("CALL /classify | text='%s' | len=%s", text, len(text))

	try:
		if text == "crash":
			raise RuntimeError("의도적 장애 추가")

		label, score = check_spam(text)
		logger.info("OK /classify | label=%s score=%s", label, score)
		return {
			"label": label,
			"score": score
		}
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
		return {"label": "Internal Server Error", "score": -1}
# 실행은 운영 환경의 책임으로 남기기 위해 만들지 X
# http://127.0.0.1:8000 접속
# if __name__ == "__main__":
# uvicorn.run(app, host="127.0.0.1", port=8000)
