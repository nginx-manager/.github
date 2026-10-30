"""조직 소개(profile/README.md와 언어별 README.<언어>.md)의 릴리스 표와 배지를 app 저장소 릴리스 노트에 맞춘다.

원천은 nginx-manager/app main의 docs/releases/README.md 표다. 날짜가 적힌(출시한) 줄만 가져오고,
맨 위 줄을 최신 버전으로 보고 release 배지와 그 노트의 nginx 버전으로 nginx 배지를 바꾼다.
표는 README의 <!-- releases:start --> 와 <!-- releases:end --> 사이를 통째로 다시 쓴다.
노트 목록의 "주요 내용"은 한국어라 한국어 README에만 넣고, 다른 언어 README에는 버전·날짜·노트 링크만 넣는다.
사용: python3 scripts/sync_releases.py profile/README.md profile/README.en.md ...
"""
import re
import sys
import urllib.request

RAW = "https://raw.githubusercontent.com/nginx-manager/app/main/docs/releases/"
BLOB = "https://github.com/nginx-manager/app/blob/main/docs/releases/"
HEADER = "| 버전 | 날짜 | 주요 내용 | 릴리스 노트 |\n| --- | --- | --- | --- |"
# 한국어 밖의 README: 파일 이름의 언어(README.en.md → en)로 표 머리를 고른다
SHORT_HEADERS = {
    "en": "| Version | Date | Release notes |\n| --- | --- | --- |",
    "ja": "| バージョン | 日付 | リリースノート |\n| --- | --- | --- |",
    "zh-CN": "| 版本 | 日期 | 发行说明 |\n| --- | --- | --- |",
}
READMES = sys.argv[1:] or ["profile/README.md"]


def fetch(name):
    with urllib.request.urlopen(RAW + name, timeout=30) as res:
        return res.read().decode("utf-8")


def released_rows(notes_index):
    rows = []
    for line in notes_index.splitlines():
        m = re.match(r"^\| (v\d+\.\d+\.\d+) \| (\d{4}-\d{2}-\d{2}) \|", line)
        if m:
            # 노트 링크(vX.Y.Z.md)를 저장소 밖에서도 열리게 절대 주소로 바꾼다
            rows.append((m.group(1), m.group(2), re.sub(r"\]\((v[^)]+\.md)\)", lambda l: "](" + BLOB + l.group(1) + ")", line)))
    return rows


def language(path):
    m = re.search(r"README\.([A-Za-z-]+)\.md$", path)
    return m.group(1) if m else "ko"


def table(lang, rows):
    if lang == "ko":
        lines = [HEADER] + [r for _, _, r in rows]
    else:
        lines = [SHORT_HEADERS[lang]] + ["| %s | %s | [%s](%s%s.md) |" % (v, d, v, BLOB, v) for v, d, _ in rows]
    return "<!-- releases:start -->\n" + "\n".join(lines) + "\n<!-- releases:end -->"


def sync(path, rows, latest, nginx):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    text, n = re.subn(r"<!-- releases:start -->.*?<!-- releases:end -->", lambda _: table(language(path), rows), text, flags=re.S)
    if n != 1:
        sys.exit("release markers not found in " + path)
    text = re.sub(r"\[!\[Release\]\([^)]*\)\]\([^)]*\)",
                  "[![Release](https://img.shields.io/badge/release-%s-10b981.svg)]"
                  "(https://github.com/nginx-manager/app/releases/tag/%s)" % (latest, latest), text)
    if nginx:
        text = re.sub(r"badge/nginx-[0-9.]+-009639", "badge/nginx-%s-009639" % nginx, text)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    rows = released_rows(fetch("README.md"))
    if not rows:
        print("no released version in the notes index; nothing to do")
        return
    latest = rows[0][0]
    m = re.search(r"^- nginx: (\d+\.\d+\.\d+)", fetch(latest + ".md"), re.M)
    nginx = m.group(1) if m else None
    for path in READMES:
        sync(path, rows, latest, nginx)
    print("latest", latest, "nginx", nginx or "?", "rows", len(rows), "files", len(READMES))


if __name__ == "__main__":
    main()
