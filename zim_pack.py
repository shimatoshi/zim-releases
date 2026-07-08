#!/usr/bin/env python3
"""zim_pack.py — 単一の self-contained HTML を Kiwix 検索対応 ZIM にパックする。

GitHub Actions(ubuntu-latest, glibc) 上で実行する前提。libzim は manylinux wheel が
あるので `pip install libzim` だけで入る(Termux arm では wheel が無く動かないのが CI 化の動機)。
Pixel5 の research-zim-tools/zim_pack_libzim.py を CI 向けに移植。

  python3 zim_pack.py input.html output.zim [--title T] [--lang ja] [--date YYYY-MM-DD]
"""
import argparse
import os
import re
from datetime import date

from libzim.writer import Creator, Item, StringProvider, Hint

LANG_MAP = {"ja": "jpn", "en": "eng"}


def extract_title(html):
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else "Untitled"


class HtmlItem(Item):
    def __init__(self, path, title, html):
        super().__init__()
        self._path, self._title, self._html = path, title, html

    def get_path(self):
        return self._path

    def get_title(self):
        return self._title

    def get_mimetype(self):
        return "text/html"

    def get_contentprovider(self):
        return StringProvider(self._html)

    def get_hints(self):
        return {Hint.FRONT_ARTICLE: True}  # 全文検索+タイトルサジェスト対象


def main():
    p = argparse.ArgumentParser(description="self-contained HTML -> searchable ZIM")
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--title", default=None)
    p.add_argument("--lang", default="ja")
    p.add_argument("--date", default=None)
    args = p.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        html = f.read()

    title = args.title or extract_title(html)
    lang3 = LANG_MAP.get(args.lang, args.lang)
    zim_date = args.date or date.today().isoformat()
    zim_name = os.path.splitext(os.path.basename(args.output))[0] or "zim-report"

    print(f"Packing: {args.input} ({len(html)//1024}KB) title={title!r} "
          f"lang={lang3} name={zim_name}")

    creator = Creator(args.output).config_indexing(True, lang3)
    with creator:
        creator.set_mainpath("index.html")
        creator.add_item(HtmlItem("index.html", title, html))
        for name, value in [
            ("Title", title[:30]),
            ("Name", zim_name),
            ("Tags", "_ftindex:yes"),
            ("Language", lang3),
            ("Date", zim_date),
            ("Description", title[:80]),
            ("Creator", "hikigaeru-zim-ci"),
            ("Publisher", "hikigaeru-zim-ci"),
        ]:
            creator.add_metadata(name, value)

    size = os.path.getsize(args.output)
    print(f"Output: {args.output} ({size//1024}KB, fulltext index: enabled)")


if __name__ == "__main__":
    main()
