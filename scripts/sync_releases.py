"""조직 소개(profile/README.md)의 릴리스 표와 배지를 app 저장소 릴리스 노트에 맞춘다.

원천은 nginx-manager/app main의 docs/releases/README.md 표다. 날짜가 적힌(출시한) 줄만 가져오고,
맨 위 줄을 최신 버전으로 보고 release 배지와 그 노트의 nginx 버전으로 nginx 배지를 바꾼다.
표는 README의 <!-- releases:start --> 와 <!-- releases:end --> 사이를 통째로 다시 쓴다.
"""
import re
import sys
import urllib.request

RAW = "https://raw.githubusercontent.com/nginx-manager/app/main/docs/releases/"
BLOB = "https://github.com/nginx-manager/app/blob/main/docs/releases/"
HEADER = "| 버전 | 날짜 | 주요 내용 | 릴리스 노트 |\n| --- | --- | --- | --- |"
README = sys.argv[1] if len(sys.argv) > 1 else "profile/README.md"


def fetch(name):
    with urllib.request.urlopen(RAW + name, timeout=30) as res:
        return res.read().decode("utf-8")


def released_rows(notes_index):
    rows = []
    for line in notes_index.splitlines():
        m = re.match(r"^\| (v\d+\.\d+\.\d+) \| (\d{4}-\d{2}-\d{2}) \|", line)
        if m:
            # 노트 링크(vX.Y.Z.md)를 저장소 밖에서도 열리게 절대 주소로 바꾼다
            rows.append((m.group(1), re.sub(r"\]\((v[^)]+\.md)\)", lambda l: "](" + BLOB + l.group(1) + ")", line)))
    return rows


def main():
    rows = released_rows(fetch("README.md"))
    if not rows:
        print("no released version in the notes index; nothing to do")
        return
    latest = rows[0][0]
    nginx = re.search(r"^- nginx: (\d+\.\d+\.\d+)", fetch(latest + ".md"), re.M)

    with open(README, encoding="utf-8") as f:
        text = f.read()
    table = "<!-- releases:start -->\n" + HEADER + "\n" + "\n".join(r for _, r in rows) + "\n<!-- releases:end -->"
    text, n = re.subn(r"<!-- releases:start -->.*?<!-- releases:end -->", table, text, flags=re.S)
    if n != 1:
        sys.exit("release markers not found in " + README)
    text = re.sub(r"\[!\[Release\]\([^)]*\)\]\([^)]*\)",
                  "[![Release](https://img.shields.io/badge/release-%s-10b981.svg)]"
                  "(https://github.com/nginx-manager/app/releases/tag/%s)" % (latest, latest), text)
    if nginx:
        text = re.sub(r"badge/nginx-[0-9.]+-009639", "badge/nginx-%s-009639" % nginx.group(1), text)
    with open(README, "w", encoding="utf-8") as f:
        f.write(text)
    print("latest", latest, "nginx", nginx.group(1) if nginx else "?", "rows", len(rows))


if __name__ == "__main__":
    main()
