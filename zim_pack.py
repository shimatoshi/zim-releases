#!/usr/bin/env python3
"""zim_pack.py — HTMLを自己完結化し、Kiwix検索対応ZIMへパックする。"""
import argparse, base64, mimetypes, os, re, urllib.request
from datetime import date
from libzim.writer import Creator, Item, StringProvider, Hint

LANG_MAP={"ja":"jpn","en":"eng"}

def extract_title(html):
    m=re.search(r"<title[^>]*>(.*?)</title>",html,re.DOTALL|re.IGNORECASE)
    return m.group(1).strip() if m else "Untitled"

def inline_remote_images(html):
    """Remote <img src=http(s)://...> resources become data URIs before packing."""
    pat=re.compile(r'(<img\b[^>]*?\bsrc\s*=\s*)(["\'])(https?://[^"\']+)\2',re.I)
    cache={}
    def repl(m):
        url=m.group(3)
        if url in cache:
            data_uri=cache[url]
        else:
            try:
                req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (zim-releases image embedder)"})
                with urllib.request.urlopen(req,timeout=30) as r:
                    raw=r.read()
                    ctype=(r.headers.get_content_type() or "").lower()
                if not ctype.startswith("image/"):
                    ctype=mimetypes.guess_type(url.split("?")[0])[0] or "application/octet-stream"
                if not ctype.startswith("image/"):
                    raise ValueError(f"not an image: {ctype}")
                data_uri=f"data:{ctype};base64,"+base64.b64encode(raw).decode("ascii")
                cache[url]=data_uri
                print(f"Embedded image: {url} ({len(raw)//1024} KB, {ctype})")
            except Exception as e:
                print(f"WARNING: could not embed image {url}: {e}")
                return m.group(0)
        return m.group(1)+m.group(2)+data_uri+m.group(2)
    out=pat.sub(repl,html)
    remaining=re.findall(r'<img\b[^>]*?\bsrc\s*=\s*["\']https?://',out,re.I)
    print(f"Images embedded: {len(cache)}; remote image refs remaining: {len(remaining)}")
    return out

class HtmlItem(Item):
    def __init__(self,path,title,html):
        super().__init__(); self._path,self._title,self._html=path,title,html
    def get_path(self): return self._path
    def get_title(self): return self._title
    def get_mimetype(self): return "text/html"
    def get_contentprovider(self): return StringProvider(self._html)
    def get_hints(self): return {Hint.FRONT_ARTICLE:True}

def main():
    p=argparse.ArgumentParser(description="HTML -> self-contained searchable ZIM")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--title",default=None); p.add_argument("--lang",default="ja"); p.add_argument("--date",default=None)
    args=p.parse_args()
    with open(args.input,"r",encoding="utf-8") as f: html=f.read()
    html=inline_remote_images(html)
    title=args.title or extract_title(html)
    lang3=LANG_MAP.get(args.lang,args.lang); zim_date=args.date or date.today().isoformat()
    zim_name=os.path.splitext(os.path.basename(args.output))[0] or "zim-report"
    print(f"Packing self-contained HTML: {len(html)//1024} KB")
    creator=Creator(args.output).config_indexing(True,lang3)
    with creator:
        creator.set_mainpath("index.html"); creator.add_item(HtmlItem("index.html",title,html))
        for name,value in [("Title",title[:30]),("Name",zim_name),("Tags","_ftindex:yes"),("Language",lang3),("Date",zim_date),("Description",title[:80]),("Creator","hikigaeru-zim-ci"),("Publisher","hikigaeru-zim-ci")]:
            creator.add_metadata(name,value)
    print(f"Output: {args.output} ({os.path.getsize(args.output)//1024} KB)")

if __name__=="__main__": main()
