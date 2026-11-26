"""搜索仓库内的 Markdown，输出相对路径及原文行号。"""

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SECTIONS = ("木作", "收纳", "住商知识库", "风格手册", "实操经验")


def search(terms):
    matches = []
    for section in SECTIONS:
        for path in (REPO / section).rglob("*.md"):
            lines = path.read_text(encoding="utf-8-sig").splitlines()
            title = next((line.lstrip("# ").strip() for line in lines if line.startswith("# ")), path.stem)
            text = "\n".join(lines).casefold()
            if not all(term in text or term in title.casefold() for term in terms):
                continue

            excerpts = []
            title_hits = sum(term in title.casefold() for term in terms)
            for number, line in enumerate(lines, 1):
                hits = sum(term in line.casefold() for term in terms)
                if hits:
                    excerpts.append((hits, number, line.strip()))

            excerpts.sort(key=lambda match: (-match[0], match[1]))
            best_line = excerpts[0][0] if excerpts else 0
            rank = (title_hits, best_line, min(len(excerpts), 8))
            matches.append((rank, path.relative_to(REPO).as_posix(), title, excerpts[:3]))

    return sorted(matches, key=lambda item: (-item[0][0], -item[0][1], -item[0][2], item[1]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("keywords", nargs="+", help="搜索词，可用空格隔开")
    parser.add_argument("--top", type=int, default=6, help="最多返回的文档数，默认 6")
    args = parser.parse_args()
    terms = tuple(dict.fromkeys(term.casefold() for value in args.keywords for term in value.split()))
    if not terms or args.top < 1:
        parser.error("请输入至少一个关键词和大于零的结果数量")

    matches = search(terms)
    if not matches:
        print("未找到同时包含这些关键词的文档。可换词或查对应分类。")
        return

    print(f"找到 {len(matches)} 份，显示前 {min(args.top, len(matches))} 份。")
    for _, path, title, excerpts in matches[:args.top]:
        print(f"\n{title}")
        for _, number, line in excerpts:
            print(f"{path}:{number}: {line[:200]}")


if __name__ == "__main__":
    main()
