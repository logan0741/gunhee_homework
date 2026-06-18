"""
Convert the final project report Markdown → styled HTML → PDF (via Edge headless).
"""
import base64
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent
MD_FILE = BASE / "기말프로젝트_보고서_214466_김건희.md"
HTML_FILE = BASE / "기말프로젝트_보고서_214466_김건희.html"
PDF_FILE = BASE / "기말프로젝트_보고서_214466_김건희.pdf"
SCREENSHOTS = BASE / "screenshots"

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def b64_img(path: Path) -> str:
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/png;base64,{data}"


def md_to_html(md: str) -> str:
    """Simple markdown → HTML converter (tables, headers, code, bold, images)."""
    lines = md.split("\n")
    html = []
    in_code = False
    in_table = False
    in_ul = False

    for line in lines:
        # Code block
        if line.startswith("```"):
            if in_code:
                html.append("</code></pre>")
                in_code = False
            else:
                lang = line[3:].strip()
                html.append(f'<pre><code class="lang-{lang}">')
                in_code = True
            continue
        if in_code:
            html.append(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            continue

        # Table
        if "|" in line and line.strip().startswith("|"):
            if not in_table:
                html.append('<table border="1">')
                in_table = True
            if re.match(r"^\|[-| :]+\|$", line.strip()):
                continue
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            tag = "th" if not any("<td>" in h for h in html[-3:]) else "td"
            row = "".join(f"<{tag}>{c}</{tag}>" for c in cols)
            html.append(f"<tr>{row}</tr>")
            continue
        elif in_table:
            html.append("</table>")
            in_table = False

        # Headings
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            lvl = len(m.group(1))
            text = inline(m.group(2))
            html.append(f"<h{lvl}>{text}</h{lvl}>")
            continue

        # HR
        if re.match(r"^---+$", line.strip()):
            html.append("<hr>")
            continue

        # Images  ![alt](path)
        if re.match(r"^\s*!\[", line):
            im = re.sub(r"!\[([^\]]*)\]\(([^\)]+)\)", img_tag, line)
            html.append(f"<p>{im}</p>")
            continue

        # Empty line
        if not line.strip():
            if in_ul:
                html.append("</ul>")
                in_ul = False
            html.append("<br>")
            continue

        # Bullet
        if line.strip().startswith("- "):
            if not in_ul:
                html.append("<ul>")
                in_ul = True
            html.append(f"<li>{inline(line.strip()[2:])}</li>")
            continue
        elif in_ul:
            html.append("</ul>")
            in_ul = False

        html.append(f"<p>{inline(line)}</p>")

    if in_table:
        html.append("</table>")
    if in_ul:
        html.append("</ul>")
    return "\n".join(html)


def img_tag(m):
    alt = m.group(1)
    src = m.group(2)
    path = SCREENSHOTS / Path(src).name if not Path(src).is_absolute() else Path(src)
    if path.exists():
        return f'<img src="{b64_img(path)}" alt="{alt}" style="max-width:100%;border:1px solid #ddd;border-radius:4px;margin:8px 0;">'
    return f'<em>[이미지 없음: {src}]</em>'


def inline(text: str) -> str:
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Inline code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # Links
    text = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", r'<a href="\2">\1</a>', text)
    # Inline images
    text = re.sub(r"!\[([^\]]*)\]\(([^\)]+)\)", img_tag, text)
    return text


CSS = """
* { box-sizing: border-box; }
body { font-family: 'Malgun Gothic', 'NanumGothic', Arial, sans-serif;
       font-size: 12pt; line-height: 1.7; color: #222;
       max-width: 900px; margin: 0 auto; padding: 40px 48px; }
h1 { font-size: 22pt; border-bottom: 3px solid #1565c0; padding-bottom: 10px; color: #1565c0; }
h2 { font-size: 16pt; border-left: 5px solid #1565c0; padding-left: 12px; color: #1a237e; margin-top: 32px; }
h3 { font-size: 13pt; color: #333; margin-top: 20px; }
h4 { font-size: 12pt; color: #555; }
table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 11pt; }
th { background: #1565c0; color: white; padding: 8px 10px; text-align: left; }
td { padding: 7px 10px; border: 1px solid #ccc; }
tr:nth-child(even) td { background: #f5f8ff; }
pre { background: #1e1e1e; color: #d4d4d4; padding: 16px; border-radius: 6px;
      font-size: 10pt; overflow-x: auto; white-space: pre-wrap; word-break: break-all; }
code { background: #f0f4ff; color: #c62828; padding: 2px 5px; border-radius: 3px; font-size: 10pt; }
pre code { background: transparent; color: #d4d4d4; padding: 0; }
img { max-width: 100%; }
hr { border: none; border-top: 1px solid #ddd; margin: 24px 0; }
a { color: #1565c0; }
ul { padding-left: 24px; }
li { margin: 4px 0; }
"""


def main():
    md = MD_FILE.read_text(encoding="utf-8")

    # Replace placeholder image tags in markdown
    replacements = {
        # 섹션 1 개요: 실험 목록 + 등록 모델 목록 (서로 다른 이미지)
        "`[MLflow UI 실험 목록 화면 캡처 첨부]`": "![MLflow 실험 목록](screenshots/04_mlflow_experiments.png)",
        "`[MLflow SpamClassifier 모델 레지스트리 화면 캡처 첨부]`": "![MLflow 등록 모델 목록](screenshots/05_mlflow_models.png)",
        # 섹션 6 CI/CD: CI 성공 화면 + MLflow 학습 결과 Run 상세 (서로 다른 이미지)
        "`[GitHub Actions CI 성공 화면 캡처 첨부]`": "![GitHub Actions CI](screenshots/06_github_actions.png)",
        "`[GitHub Actions MLflow Auto Train 성공 화면 캡처 첨부]`": "![MLflow Auto Train 실행 결과](screenshots/07_mlflow_run_detail.png)",
        # 섹션 8 MLflow: 실험 목록 + Run 상세 + 버전 상세 (모두 다른 이미지)
        "`[MLflow Experiments 탭 - 3개 실험 목록 캡처 첨부]`": "![MLflow 실험 목록](screenshots/04_mlflow_experiments.png)",
        "`[MLflow Run 상세 - 파라미터/메트릭 화면 캡처 첨부]`": "![MLflow Run 상세](screenshots/07_mlflow_run_detail.png)",
        "`[MLflow Models 탭 - SpamClassifier 버전 목록 캡처 첨부]`": "![SpamClassifier 버전 상세](screenshots/05_mlflow_model_detail.png)",
        # 섹션 12 롤백: 등록 모델 목록 + git 이력 (서로 다른 이미지)
        "`[MLflow Models - SpamClassifier 버전 목록 캡처 첨부]`": "![MLflow 등록 모델 목록](screenshots/05_mlflow_models.png)",
        "`[rollback.py --list 실행 결과 캡처 첨부]`": "![Git 커밋 이력](screenshots/09_git_log.png)",
        # 섹션 11: 분류 결과 화면 (GitHub Issue 캡처 대용)
        "`[GitHub Issues - 자동 생성된 에러 이슈 캡처 첨부]`": "![에러 분류 결과](screenshots/08_classify_result.png)",
        "`[Render.com 배포 화면 캡처 첨부]`": "",
        "`[배포된 서비스 접속 화면 캡처 첨부]`": "",
    }
    for old, new in replacements.items():
        md = md.replace(old, new)

    # Remove remaining empty placeholder lines
    md = re.sub(r"`\[.*?캡처.*?\]`", "", md)

    body = md_to_html(md)
    html = f"""<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width">
<title>기말프로젝트 보고서 - 214466 김건희</title>
<style>{CSS}</style>
</head><body>
{body}
</body></html>"""

    HTML_FILE.write_text(html, encoding="utf-8")
    print(f"HTML saved: {HTML_FILE}")

    # Convert to PDF via Edge headless
    result = subprocess.run([
        EDGE,
        "--headless",
        f"--print-to-pdf={PDF_FILE}",
        "--no-pdf-header-footer",
        "--no-sandbox",
        "--disable-gpu",
        str(HTML_FILE),
    ], capture_output=True, text=True, timeout=60)

    if PDF_FILE.exists():
        print(f"PDF saved: {PDF_FILE} ({PDF_FILE.stat().st_size:,} bytes)")
    else:
        print(f"PDF failed: {result.stderr[:500]}")


if __name__ == "__main__":
    main()
